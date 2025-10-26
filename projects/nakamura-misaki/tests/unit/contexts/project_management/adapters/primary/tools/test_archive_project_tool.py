"""ArchiveProjectTool Unit Tests"""

from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.contexts.project_management.adapters.primary.tools.project_tools import ArchiveProjectTool
from src.contexts.project_management.application.dto.project_dto import ProjectDTO
from src.contexts.project_management.application.use_cases.archive_project import ArchiveProjectUseCase


class TestArchiveProjectTool:
    """ArchiveProjectTool tests"""

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """プロジェクトアーカイブ成功"""
        # Arrange
        mock_use_case = AsyncMock(spec=ArchiveProjectUseCase)
        tool = ArchiveProjectTool(mock_use_case, "U123")

        project_id = uuid4()
        project_dto = ProjectDTO(
            project_id=project_id,
            name="Test Project",
            owner_user_id="U123",
            status="archived",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_use_case.execute.return_value = project_dto

        # Act
        result = await tool.execute(project_id=str(project_id))

        # Assert
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["status"] == "archived"
        mock_use_case.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_invalid_project_id(self):
        """不正なプロジェクトIDでエラー"""
        # Arrange
        mock_use_case = AsyncMock(spec=ArchiveProjectUseCase)
        tool = ArchiveProjectTool(mock_use_case, "U123")

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
        mock_use_case = AsyncMock(spec=ArchiveProjectUseCase)
        tool = ArchiveProjectTool(mock_use_case, "U123")

        project_id = str(uuid4())
        mock_use_case.execute.side_effect = ValueError("Project not found")

        # Act
        result = await tool.execute(project_id=project_id)

        # Assert
        assert result["success"] is False
        assert "Project not found" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_converts_all_datetime_fields_to_isoformat(self):
        """すべてのdatetimeフィールドがISO形式で返される"""
        # Arrange
        mock_use_case = AsyncMock(spec=ArchiveProjectUseCase)
        tool = ArchiveProjectTool(mock_use_case, "U123")

        project_id = uuid4()
        created_at = datetime.now()
        updated_at = datetime.now()
        deadline = datetime.now()

        project_dto = ProjectDTO(
            project_id=project_id,
            name="Test Project",
            owner_user_id="U123",
            status="archived",
            created_at=created_at,
            updated_at=updated_at,
            deadline=deadline,
        )
        mock_use_case.execute.return_value = project_dto

        # Act
        result = await tool.execute(project_id=str(project_id))

        # Assert
        assert result["success"] is True
        assert result["data"]["created_at"] == created_at.isoformat()
        assert result["data"]["updated_at"] == updated_at.isoformat()
        assert result["data"]["deadline"] == deadline.isoformat()

    def test_name_property(self):
        """name プロパティ"""
        mock_use_case = AsyncMock(spec=ArchiveProjectUseCase)
        tool = ArchiveProjectTool(mock_use_case, "U123")
        assert tool.name == "archive_project"

    def test_description_property(self):
        """description プロパティ"""
        mock_use_case = AsyncMock(spec=ArchiveProjectUseCase)
        tool = ArchiveProjectTool(mock_use_case, "U123")
        assert "アーカイブ" in tool.description

    def test_input_schema(self):
        """input_schema プロパティ"""
        mock_use_case = AsyncMock(spec=ArchiveProjectUseCase)
        tool = ArchiveProjectTool(mock_use_case, "U123")

        schema = tool.input_schema
        assert schema["type"] == "object"
        assert "project_id" in schema["properties"]
        assert schema["required"] == ["project_id"]
