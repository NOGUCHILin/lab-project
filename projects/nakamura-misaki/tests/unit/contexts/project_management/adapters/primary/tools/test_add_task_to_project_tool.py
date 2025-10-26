"""AddTaskToProjectTool Unit Tests"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.contexts.project_management.adapters.primary.tools.project_tools import AddTaskToProjectTool
from src.contexts.project_management.application.use_cases.add_task_to_project import AddTaskToProjectUseCase


class TestAddTaskToProjectTool:
    """AddTaskToProjectTool tests"""

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """タスク追加成功"""
        # Arrange
        mock_use_case = AsyncMock(spec=AddTaskToProjectUseCase)
        tool = AddTaskToProjectTool(mock_use_case, "U123")

        project_id = str(uuid4())
        task_id = str(uuid4())

        # Act
        result = await tool.execute(project_id=project_id, task_id=task_id)

        # Assert
        assert result["success"] is True
        assert "message" in result
        mock_use_case.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_invalid_project_id(self):
        """不正なプロジェクトIDでエラー"""
        # Arrange
        mock_use_case = AsyncMock(spec=AddTaskToProjectUseCase)
        tool = AddTaskToProjectTool(mock_use_case, "U123")

        # Act
        result = await tool.execute(project_id="invalid-uuid", task_id=str(uuid4()))

        # Assert
        assert result["success"] is False
        assert "error" in result
        assert "Invalid UUID format" in result["error"]
        mock_use_case.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_with_invalid_task_id(self):
        """不正なタスクIDでエラー"""
        # Arrange
        mock_use_case = AsyncMock(spec=AddTaskToProjectUseCase)
        tool = AddTaskToProjectTool(mock_use_case, "U123")

        # Act
        result = await tool.execute(project_id=str(uuid4()), task_id="invalid-uuid")

        # Assert
        assert result["success"] is False
        assert "Invalid UUID format" in result["error"]
        mock_use_case.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_when_use_case_raises_exception(self):
        """Use Caseが例外を投げた場合"""
        # Arrange
        mock_use_case = AsyncMock(spec=AddTaskToProjectUseCase)
        tool = AddTaskToProjectTool(mock_use_case, "U123")

        project_id = str(uuid4())
        task_id = str(uuid4())
        mock_use_case.execute.side_effect = ValueError("Task not found")

        # Act
        result = await tool.execute(project_id=project_id, task_id=task_id)

        # Assert
        assert result["success"] is False
        assert "Task not found" in result["error"]

    def test_name_property(self):
        """name プロパティ"""
        mock_use_case = AsyncMock(spec=AddTaskToProjectUseCase)
        tool = AddTaskToProjectTool(mock_use_case, "U123")
        assert tool.name == "add_task_to_project"

    def test_description_property(self):
        """description プロパティ"""
        mock_use_case = AsyncMock(spec=AddTaskToProjectUseCase)
        tool = AddTaskToProjectTool(mock_use_case, "U123")
        assert "タスク" in tool.description

    def test_input_schema(self):
        """input_schema プロパティ"""
        mock_use_case = AsyncMock(spec=AddTaskToProjectUseCase)
        tool = AddTaskToProjectTool(mock_use_case, "U123")

        schema = tool.input_schema
        assert schema["type"] == "object"
        assert "project_id" in schema["properties"]
        assert "task_id" in schema["properties"]
        assert set(schema["required"]) == {"project_id", "task_id"}
