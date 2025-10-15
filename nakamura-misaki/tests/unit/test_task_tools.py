"""
Unit tests for TaskTools.

Following TDD: Red -> Green -> Refactor
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.adapters.primary.tools.task_tools import (
    CompleteTaskTool,
    ListTasksTool,
    RegisterTaskTool,
)
from src.application.dto.task_dto import TaskDTO
from src.domain.models.task import Task, TaskStatus


@pytest.fixture
def mock_use_case():
    """Mock RegisterTaskUseCase."""
    use_case = Mock()
    use_case.execute = AsyncMock()
    return use_case


@pytest.fixture
def register_task_tool(mock_use_case):
    """Create RegisterTaskTool instance."""
    return RegisterTaskTool(register_task_use_case=mock_use_case, user_id="U5D0CJKMH")


def test_register_task_tool_name(register_task_tool):
    """Should have correct tool name."""
    assert register_task_tool.name == "register_task"


def test_register_task_tool_description(register_task_tool):
    """Should have clear description."""
    assert "タスク" in register_task_tool.description
    assert "登録" in register_task_tool.description


def test_register_task_tool_schema(register_task_tool):
    """Should have valid JSON schema."""
    schema = register_task_tool.input_schema

    assert schema["type"] == "object"
    assert "title" in schema["properties"]
    assert "title" in schema["required"]
    assert "description" in schema["properties"]
    assert "due_date" in schema["properties"]


def test_to_tool_definition(register_task_tool):
    """Should generate Claude API tool definition."""
    definition = register_task_tool.to_tool_definition()

    assert definition["name"] == "register_task"
    assert "description" in definition
    assert "input_schema" in definition
    assert isinstance(definition["input_schema"], dict)


@pytest.mark.asyncio
async def test_execute_register_task_minimal(register_task_tool, mock_use_case):
    """Should register task with minimal parameters."""
    task = Task(
        id=uuid4(),
        title="レポート作成",
        assignee_user_id="U5D0CJKMH",
        creator_user_id="U5D0CJKMH",
        status=TaskStatus.PENDING,
    )

    mock_use_case.execute.return_value = task

    result = await register_task_tool.execute(title="レポート作成")

    assert result["success"] is True
    assert "data" in result
    assert result["data"]["title"] == "レポート作成"
    assert result["data"]["status"] == "pending"

    mock_use_case.execute.assert_called_once()


@pytest.mark.asyncio
async def test_execute_register_task_with_due_date(register_task_tool, mock_use_case):
    """Should register task with due date."""
    due_date = datetime.now()
    task = Task(
        id=uuid4(),
        title="レポート作成",
        assignee_user_id="U5D0CJKMH",
        creator_user_id="U5D0CJKMH",
        status=TaskStatus.PENDING,
        due_at=due_date,
    )

    mock_use_case.execute.return_value = task

    result = await register_task_tool.execute(
        title="レポート作成", due_date=due_date.isoformat()
    )

    assert result["success"] is True
    assert result["data"]["title"] == "レポート作成"

    mock_use_case.execute.assert_called_once()


@pytest.mark.asyncio
async def test_execute_register_task_with_description(
    register_task_tool, mock_use_case
):
    """Should register task with description."""
    task = Task(
        id=uuid4(),
        title="レポート作成",
        description="月次レポートを作成する",
        assignee_user_id="U5D0CJKMH",
        creator_user_id="U5D0CJKMH",
        status=TaskStatus.PENDING,
    )

    mock_use_case.execute.return_value = task

    result = await register_task_tool.execute(
        title="レポート作成", description="月次レポートを作成する"
    )

    assert result["success"] is True
    assert result["data"]["description"] == "月次レポートを作成する"


@pytest.mark.asyncio
async def test_execute_register_task_error(register_task_tool, mock_use_case):
    """Should handle execution errors gracefully."""
    mock_use_case.execute.side_effect = ValueError("Invalid title")

    result = await register_task_tool.execute(title="")

    assert result["success"] is False
    assert "error" in result
    assert "Invalid title" in result["error"]


# ListTasksTool tests


@pytest.fixture
def mock_query_use_case():
    """Mock QueryUserTasksUseCase."""
    use_case = Mock()
    use_case.execute = AsyncMock()
    return use_case


@pytest.fixture
def list_tasks_tool(mock_query_use_case):
    """Create ListTasksTool instance."""
    return ListTasksTool(query_user_tasks_use_case=mock_query_use_case, user_id="U5D0CJKMH")


def test_list_tasks_tool_name(list_tasks_tool):
    """Should have correct tool name."""
    assert list_tasks_tool.name == "list_tasks"


def test_list_tasks_tool_schema(list_tasks_tool):
    """Should have valid JSON schema."""
    schema = list_tasks_tool.input_schema

    assert schema["type"] == "object"
    assert "status" in schema["properties"]
    assert "date_filter" in schema["properties"]


@pytest.mark.asyncio
async def test_execute_list_tasks_all(list_tasks_tool, mock_query_use_case):
    """Should list all tasks."""
    tasks = [
        TaskDTO(
            id=uuid4(),
            user_id="U5D0CJKMH",
            title="タスク1",
            description="",
            status="pending",
            due_at=None,
            completed_at=None,
            created_at=datetime.now(),
        ),
        TaskDTO(
            id=uuid4(),
            user_id="U5D0CJKMH",
            title="タスク2",
            description="",
            status="in_progress",
            due_at=None,
            completed_at=None,
            created_at=datetime.now(),
        ),
    ]

    mock_query_use_case.execute.return_value = tasks

    result = await list_tasks_tool.execute()

    assert result["success"] is True
    assert len(result["data"]["tasks"]) == 2
    assert result["data"]["count"] == 2


@pytest.mark.asyncio
async def test_execute_list_tasks_with_status_filter(list_tasks_tool, mock_query_use_case):
    """Should list tasks filtered by status."""
    tasks = [
        TaskDTO(
            id=uuid4(),
            user_id="U5D0CJKMH",
            title="タスク1",
            description="",
            status="pending",
            due_at=None,
            completed_at=None,
            created_at=datetime.now(),
        ),
    ]

    mock_query_use_case.execute.return_value = tasks

    result = await list_tasks_tool.execute(status="pending")

    assert result["success"] is True
    assert len(result["data"]["tasks"]) == 1


# CompleteTaskTool tests


@pytest.fixture
def mock_complete_use_case():
    """Mock CompleteTaskUseCase."""
    use_case = Mock()
    use_case.execute = AsyncMock()
    return use_case


@pytest.fixture
def mock_query_for_complete():
    """Mock QueryUserTasksUseCase for CompleteTaskTool."""
    use_case = Mock()
    use_case.execute = AsyncMock()
    return use_case


@pytest.fixture
def complete_task_tool(mock_complete_use_case, mock_query_for_complete):
    """Create CompleteTaskTool instance."""
    return CompleteTaskTool(
        complete_task_use_case=mock_complete_use_case,
        query_user_tasks_use_case=mock_query_for_complete,
        user_id="U5D0CJKMH",
    )


def test_complete_task_tool_name(complete_task_tool):
    """Should have correct tool name."""
    assert complete_task_tool.name == "complete_task"


@pytest.mark.asyncio
async def test_execute_complete_task_by_id(complete_task_tool, mock_complete_use_case, mock_query_for_complete):
    """Should complete task by UUID."""
    task_id = str(uuid4())
    task = Task(
        id=task_id,
        title="タスク1",
        assignee_user_id="U5D0CJKMH",
        creator_user_id="U5D0CJKMH",
        status=TaskStatus.COMPLETED,
    )

    mock_complete_use_case.execute.return_value = task

    result = await complete_task_tool.execute(task_identifier=task_id)

    assert result["success"] is True
    assert result["data"]["status"] == "completed"
    mock_complete_use_case.execute.assert_called_once()


@pytest.mark.asyncio
async def test_execute_complete_task_by_title(complete_task_tool, mock_complete_use_case, mock_query_for_complete):
    """Should complete task by title match."""
    task_id = uuid4()
    task_dto = TaskDTO(
        id=task_id,
        user_id="U5D0CJKMH",
        title="レポート作成",
        description="",
        status="pending",
        due_at=None,
        completed_at=None,
        created_at=datetime.now(),
    )

    completed_task = Task(
        id=task_id,
        title="レポート作成",
        assignee_user_id="U5D0CJKMH",
        creator_user_id="U5D0CJKMH",
        status=TaskStatus.COMPLETED,
    )

    # Mock query to find task by title
    mock_query_for_complete.execute.return_value = [task_dto]
    mock_complete_use_case.execute.return_value = completed_task

    result = await complete_task_tool.execute(task_identifier="レポート")

    assert result["success"] is True
    assert result["data"]["status"] == "completed"
