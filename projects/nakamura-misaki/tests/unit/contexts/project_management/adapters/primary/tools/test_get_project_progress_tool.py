"""GetProjectProgressTool Unit Tests"""

from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.contexts.project_management.adapters.primary.tools.project_tools import GetProjectProgressTool
from src.contexts.project_management.application.dto.project_dto import ProjectProgressDTO
from src.contexts.project_management.application.use_cases.get_project_progress import GetProjectProgressUseCase


class TestGetProjectProgressTool:
    """GetProjectProgressTool tests"""

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """進捗取得成功"""
        # Arrange
        mock_use_case = AsyncMock(spec=GetProjectProgressUseCase)
        tool = GetProjectProgressTool(mock_use_case, "U123")

        project_id = uuid4()
        progress_dto = ProjectProgressDTO(
            project_id=project_id,
            name="Test Project",
            total_tasks=10,
            completed_tasks=5,
            in_progress_tasks=3,
            pending_tasks=2,
            completion_percentage=50.0,
            status="active",
        )
        mock_use_case.execute.return_value = progress_dto

        # Act
        result = await tool.execute(project_id=str(project_id))

        # Assert
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["total_tasks"] == 10
        assert result["data"]["completed_tasks"] == 5
        assert result["data"]["completion_percentage"] == 50.0
        mock_use_case.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_invalid_project_id(self):
        """不正なプロジェクトIDでエラー"""
        # Arrange
        mock_use_case = AsyncMock(spec=GetProjectProgressUseCase)
        tool = GetProjectProgressTool(mock_use_case, "U123")

        # Act
        result = await tool.execute(project_id="invalid-uuid")

        # Assert
        assert result["success"] is False
        assert "Invalid UUID format" in result["error"]
        mock_use_case.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_when_use_case_raises_exception(self):
        """Use Caseが例外を投げた場合"""
        # Arrange
        mock_use_case = AsyncMock(spec=GetProjectProgressUseCase)
        tool = GetProjectProgressTool(mock_use_case, "U123")

        project_id = str(uuid4())
        mock_use_case.execute.side_effect = ValueError("Project not found")

        # Act
        result = await tool.execute(project_id=project_id)

        # Assert
        assert result["success"] is False
        assert "Project not found" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_converts_deadline_to_isoformat(self):
        """deadlineがISO形式で返される"""
        # Arrange
        mock_use_case = AsyncMock(spec=GetProjectProgressUseCase)
        tool = GetProjectProgressTool(mock_use_case, "U123")

        project_id = uuid4()
        deadline = datetime.now()
        progress_dto = ProjectProgressDTO(
            project_id=project_id,
            name="Test Project",
            total_tasks=0,
            completed_tasks=0,
            in_progress_tasks=0,
            pending_tasks=0,
            completion_percentage=0.0,
            status="active",
            deadline=deadline,
        )
        mock_use_case.execute.return_value = progress_dto

        # Act
        result = await tool.execute(project_id=str(project_id))

        # Assert
        assert result["success"] is True
        assert result["data"]["deadline"] == deadline.isoformat()

    def test_name_property(self):
        """name プロパティ"""
        mock_use_case = AsyncMock(spec=GetProjectProgressUseCase)
        tool = GetProjectProgressTool(mock_use_case, "U123")
        assert tool.name == "get_project_progress"

    def test_description_property(self):
        """description プロパティ"""
        mock_use_case = AsyncMock(spec=GetProjectProgressUseCase)
        tool = GetProjectProgressTool(mock_use_case, "U123")
        assert "進捗" in tool.description

    def test_input_schema(self):
        """input_schema プロパティ"""
        mock_use_case = AsyncMock(spec=GetProjectProgressUseCase)
        tool = GetProjectProgressTool(mock_use_case, "U123")

        schema = tool.input_schema
        assert schema["type"] == "object"
        assert "project_id" in schema["properties"]
        assert schema["required"] == ["project_id"]
