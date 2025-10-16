"""
Unit tests for UpdateTaskTool.

Following TDD: Red -> Green -> Refactor
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.adapters.primary.tools.task_tools import UpdateTaskTool


@pytest.fixture
def mock_update_use_case():
    """Mock UpdateTaskUseCase."""
    use_case = Mock()
    use_case.execute = AsyncMock()
    return use_case


@pytest.fixture
def update_task_tool(mock_update_use_case):
    """Create UpdateTaskTool instance."""
    return UpdateTaskTool(update_task_use_case=mock_update_use_case, user_id="U5D0CJKMH")


def test_update_task_tool_name(update_task_tool):
    """Should have correct tool name."""
    assert update_task_tool.name == "update_task"


def test_update_task_tool_description(update_task_tool):
    """Should have clear description."""
    assert "タスク" in update_task_tool.description
    assert "更新" in update_task_tool.description


def test_update_task_tool_schema(update_task_tool):
    """Should have valid JSON schema."""
    schema = update_task_tool.input_schema

    assert schema["type"] == "object"
    assert "task_id" in schema["properties"]
    assert "task_id" in schema["required"]
    assert "title" in schema["properties"]
    assert "description" in schema["properties"]
    assert "status" in schema["properties"]
    assert "due_date" in schema["properties"]


@pytest.mark.asyncio
async def test_execute_update_task_title(update_task_tool, mock_update_use_case):
    """Should update task title."""
    task_id = uuid4()
    updated_task_dto = Mock()
    updated_task_dto.id = task_id
    updated_task_dto.title = "Updated Title"
    updated_task_dto.description = ""
    updated_task_dto.status = "pending"
    updated_task_dto.due_at = None
    updated_task_dto.completed_at = None
    updated_task_dto.created_at = datetime.now()

    mock_update_use_case.execute.return_value = updated_task_dto

    result = await update_task_tool.execute(task_id=str(task_id), title="Updated Title")

    assert result["success"] is True
    assert result["data"]["title"] == "Updated Title"
    mock_update_use_case.execute.assert_called_once()


@pytest.mark.asyncio
async def test_execute_update_task_status(update_task_tool, mock_update_use_case):
    """Should update task status."""
    task_id = uuid4()
    updated_task_dto = Mock()
    updated_task_dto.id = task_id
    updated_task_dto.title = "Task"
    updated_task_dto.description = ""
    updated_task_dto.status = "in_progress"
    updated_task_dto.due_at = None
    updated_task_dto.completed_at = None
    updated_task_dto.created_at = datetime.now()

    mock_update_use_case.execute.return_value = updated_task_dto

    result = await update_task_tool.execute(task_id=str(task_id), status="in_progress")

    assert result["success"] is True
    assert result["data"]["status"] == "in_progress"


@pytest.mark.asyncio
async def test_execute_update_task_due_date(update_task_tool, mock_update_use_case):
    """Should update task due date."""
    task_id = uuid4()
    due_date = datetime.now()
    updated_task_dto = Mock()
    updated_task_dto.id = task_id
    updated_task_dto.title = "Task"
    updated_task_dto.description = ""
    updated_task_dto.status = "pending"
    updated_task_dto.due_at = due_date
    updated_task_dto.completed_at = None
    updated_task_dto.created_at = datetime.now()

    mock_update_use_case.execute.return_value = updated_task_dto

    result = await update_task_tool.execute(
        task_id=str(task_id), due_date=due_date.isoformat()
    )

    assert result["success"] is True
    assert result["data"]["due_at"] is not None


@pytest.mark.asyncio
async def test_execute_update_task_multiple_fields(
    update_task_tool, mock_update_use_case
):
    """Should update multiple task fields at once."""
    task_id = uuid4()
    due_date = datetime.now()
    updated_task_dto = Mock()
    updated_task_dto.id = task_id
    updated_task_dto.title = "New Title"
    updated_task_dto.description = "New Description"
    updated_task_dto.status = "in_progress"
    updated_task_dto.due_at = due_date
    updated_task_dto.completed_at = None
    updated_task_dto.created_at = datetime.now()

    mock_update_use_case.execute.return_value = updated_task_dto

    result = await update_task_tool.execute(
        task_id=str(task_id),
        title="New Title",
        description="New Description",
        status="in_progress",
        due_date=due_date.isoformat(),
    )

    assert result["success"] is True
    assert result["data"]["title"] == "New Title"
    assert result["data"]["description"] == "New Description"
    assert result["data"]["status"] == "in_progress"


@pytest.mark.asyncio
async def test_execute_update_task_invalid_uuid(update_task_tool, mock_update_use_case):
    """Should handle invalid UUID gracefully."""
    result = await update_task_tool.execute(task_id="invalid-uuid", title="New Title")

    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_execute_update_task_error(update_task_tool, mock_update_use_case):
    """Should handle execution errors gracefully."""
    task_id = uuid4()
    mock_update_use_case.execute.side_effect = ValueError("Task not found")

    result = await update_task_tool.execute(task_id=str(task_id), title="New Title")

    assert result["success"] is False
    assert "error" in result
    assert "Task not found" in result["error"]
