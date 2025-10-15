"""
Unit tests for ClaudeAgentService.

Following TDD: Red -> Green -> Refactor
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, PropertyMock, patch
from uuid import uuid4

import pytest

from src.domain.models.conversation import Conversation, Message, MessageRole
from src.domain.services.claude_agent_service import ClaudeAgentService


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client."""
    client = Mock()
    client.messages = Mock()
    client.messages.create = AsyncMock()
    return client


@pytest.fixture
def mock_tools():
    """Mock tool instances."""
    tools = []
    for i in range(3):
        tool = Mock()
        # Use PropertyMock for properties
        type(tool).name = PropertyMock(return_value=f"tool_{i}")
        type(tool).description = PropertyMock(return_value=f"Tool {i} description")
        type(tool).input_schema = PropertyMock(return_value={"type": "object", "properties": {}})
        tool.execute = AsyncMock(return_value={"success": True, "data": {}})
        tool.to_tool_definition = Mock(
            return_value={
                "name": f"tool_{i}",
                "description": f"Tool {i} description",
                "input_schema": {"type": "object", "properties": {}},
            }
        )
        tools.append(tool)
    return tools


@pytest.fixture
def claude_agent_service(mock_anthropic_client, mock_tools):
    """Create ClaudeAgentService instance."""
    return ClaudeAgentService(
        anthropic_client=mock_anthropic_client,
        tools=mock_tools,
        model="claude-3-5-sonnet-20241022",
    )


def test_claude_agent_service_initialization(claude_agent_service):
    """Should initialize with correct attributes."""
    assert claude_agent_service.model == "claude-3-5-sonnet-20241022"
    assert len(claude_agent_service._tools) == 3


@pytest.mark.asyncio
async def test_process_message_simple_response(
    claude_agent_service, mock_anthropic_client
):
    """Should process simple message without tool use."""
    conversation = Conversation(
        conversation_id=uuid4(),
        user_id="U5D0CJKMH",
        channel_id="C12345",
        messages=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        last_message_at=datetime.now(),
    )

    # Mock Claude response (text only, no tool use)
    mock_response = Mock()
    mock_response.content = [Mock(type="text", text="了解した。")]
    mock_response.stop_reason = "end_turn"
    mock_anthropic_client.messages.create.return_value = mock_response

    response_text = await claude_agent_service.process_message(
        conversation=conversation, user_message="こんにちは"
    )

    assert response_text == "了解した。"
    assert len(conversation.messages) == 2  # user message + assistant response
    assert conversation.messages[0].role == MessageRole.USER
    assert conversation.messages[0].content == "こんにちは"
    assert conversation.messages[1].role == MessageRole.ASSISTANT
    assert conversation.messages[1].content == "了解した。"


@pytest.mark.asyncio
async def test_process_message_with_tool_use(
    claude_agent_service, mock_anthropic_client, mock_tools
):
    """Should process message with tool use."""
    conversation = Conversation(
        conversation_id=uuid4(),
        user_id="U5D0CJKMH",
        channel_id="C12345",
        messages=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        last_message_at=datetime.now(),
    )

    # Mock Claude response with tool use
    tool_use_block = Mock(
        type="tool_use",
        id="toolu_123",
        name="tool_0",
        input={"param": "value"},
    )
    mock_response_1 = Mock()
    mock_response_1.content = [tool_use_block]
    mock_response_1.stop_reason = "tool_use"

    # Mock second response after tool execution
    mock_response_2 = Mock()
    mock_response_2.content = [Mock(type="text", text="タスクを登録した。")]
    mock_response_2.stop_reason = "end_turn"

    mock_anthropic_client.messages.create.side_effect = [
        mock_response_1,
        mock_response_2,
    ]

    response_text = await claude_agent_service.process_message(
        conversation=conversation, user_message="タスク追加して"
    )

    assert response_text == "タスクを登録した。"
    # Tool execution should be called
    mock_tools[0].execute.assert_called_once_with(param="value")


@pytest.mark.asyncio
async def test_process_message_multiple_turns(
    claude_agent_service, mock_anthropic_client
):
    """Should handle multi-turn conversation."""
    conversation = Conversation(
        conversation_id=uuid4(),
        user_id="U5D0CJKMH",
        channel_id="C12345",
        messages=[
            Message(role=MessageRole.USER, content="タスク一覧を見せて"),
            Message(role=MessageRole.ASSISTANT, content="タスクは3件ある。"),
        ],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        last_message_at=datetime.now(),
    )

    mock_response = Mock()
    mock_response.content = [Mock(type="text", text="了解した。")]
    mock_response.stop_reason = "end_turn"
    mock_anthropic_client.messages.create.return_value = mock_response

    response_text = await claude_agent_service.process_message(
        conversation=conversation, user_message="ありがとう"
    )

    assert response_text == "了解した。"
    # Should include previous conversation history
    call_args = mock_anthropic_client.messages.create.call_args
    messages_arg = call_args.kwargs["messages"]
    assert len(messages_arg) == 3  # 2 previous + 1 new user message


@pytest.mark.asyncio
async def test_process_message_tool_error_handling(
    claude_agent_service, mock_anthropic_client, mock_tools
):
    """Should handle tool execution errors gracefully."""
    conversation = Conversation(
        conversation_id=uuid4(),
        user_id="U5D0CJKMH",
        channel_id="C12345",
        messages=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        last_message_at=datetime.now(),
    )

    # Tool execution fails
    mock_tools[0].execute.return_value = {
        "success": False,
        "error": "Task not found",
    }

    tool_use_block = Mock(
        type="tool_use",
        id="toolu_123",
        name="tool_0",
        input={"param": "value"},
    )
    mock_response_1 = Mock()
    mock_response_1.content = [tool_use_block]
    mock_response_1.stop_reason = "tool_use"

    mock_response_2 = Mock()
    mock_response_2.content = [Mock(type="text", text="タスクが見つからなかった。")]
    mock_response_2.stop_reason = "end_turn"

    mock_anthropic_client.messages.create.side_effect = [
        mock_response_1,
        mock_response_2,
    ]

    response_text = await claude_agent_service.process_message(
        conversation=conversation, user_message="タスク完了"
    )

    assert response_text == "タスクが見つからなかった。"


def test_build_system_prompt(claude_agent_service):
    """Should build system prompt with current time."""
    with patch("src.domain.services.claude_agent_service.datetime") as mock_datetime:
        mock_now = datetime(2025, 10, 15, 10, 30, 0)
        mock_datetime.now.return_value = mock_now

        system_prompt = claude_agent_service._build_system_prompt()

        assert "中村美咲" in system_prompt
        assert "2025-10-15" in system_prompt
