"""CreateProjectTool Unit Tests

Tests for src/contexts/project_management/adapters/primary/tools/project_tools.py::CreateProjectTool
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.contexts.project_management.adapters.primary.tools.project_tools import CreateProjectTool
from src.contexts.project_management.application.dto.project_dto import ProjectDTO
from src.contexts.project_management.application.use_cases.create_project import CreateProjectUseCase


class TestCreateProjectTool:
    """CreateProjectTool tests"""

    @pytest.mark.asyncio
    async def test_execute_with_minimum_fields(self):
        """最小フィールドでのプロジェクト作成"""
        # Arrange
        mock_use_case = AsyncMock(spec=CreateProjectUseCase)
        user_id = "U123456"
        tool = CreateProjectTool(mock_use_case, user_id)

        # Mock use case response
        project_dto = ProjectDTO(
            project_id=uuid4(),
            name="Test Project",
            owner_user_id=user_id,
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_use_case.execute.return_value = project_dto

        # Act
        result = await tool.execute(name="Test Project")

        # Assert
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["name"] == "Test Project"
        assert result["data"]["owner_user_id"] == user_id
        mock_use_case.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_all_fields(self):
        """全フィールド指定でのプロジェクト作成"""
        # Arrange
        mock_use_case = AsyncMock(spec=CreateProjectUseCase)
        user_id = "U123456"
        tool = CreateProjectTool(mock_use_case, user_id)

        deadline = datetime.now() + timedelta(days=30)
        project_dto = ProjectDTO(
            project_id=uuid4(),
            name="Full Project",
            owner_user_id="U999",
            status="active",
            description="Test Description",
            deadline=deadline,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_use_case.execute.return_value = project_dto

        # Act
        result = await tool.execute(
            name="Full Project",
            description="Test Description",
            deadline=deadline.isoformat(),
            owner_user_id="U999",
        )

        # Assert
        assert result["success"] is True
        assert result["data"]["name"] == "Full Project"
        assert result["data"]["description"] == "Test Description"
        assert result["data"]["owner_user_id"] == "U999"

    @pytest.mark.asyncio
    async def test_execute_uses_current_user_when_owner_not_specified(self):
        """オーナー未指定時は現在のユーザーを使用"""
        # Arrange
        mock_use_case = AsyncMock(spec=CreateProjectUseCase)
        user_id = "U123456"
        tool = CreateProjectTool(mock_use_case, user_id)

        project_dto = ProjectDTO(
            project_id=uuid4(),
            name="Test Project",
            owner_user_id=user_id,
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_use_case.execute.return_value = project_dto

        # Act
        result = await tool.execute(name="Test Project")

        # Assert
        assert result["success"] is True
        # Verify the DTO passed to use case has correct owner_user_id
        call_args = mock_use_case.execute.call_args
        assert call_args[0][0].owner_user_id == user_id

    @pytest.mark.asyncio
    async def test_execute_with_invalid_deadline_format(self):
        """不正な期限フォーマットでエラー"""
        # Arrange
        mock_use_case = AsyncMock(spec=CreateProjectUseCase)
        user_id = "U123456"
        tool = CreateProjectTool(mock_use_case, user_id)

        # Act
        result = await tool.execute(
            name="Test Project",
            deadline="invalid-date",
        )

        # Assert
        assert result["success"] is False
        assert "error" in result
        mock_use_case.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_when_use_case_raises_exception(self):
        """Use Caseが例外を投げた場合エラーレスポンス"""
        # Arrange
        mock_use_case = AsyncMock(spec=CreateProjectUseCase)
        user_id = "U123456"
        tool = CreateProjectTool(mock_use_case, user_id)

        mock_use_case.execute.side_effect = ValueError("Project name cannot be empty")

        # Act
        result = await tool.execute(name="")

        # Assert
        assert result["success"] is False
        assert "error" in result
        assert "Project name cannot be empty" in result["error"]

    def test_name_property(self):
        """name プロパティ"""
        mock_use_case = AsyncMock(spec=CreateProjectUseCase)
        tool = CreateProjectTool(mock_use_case, "U123")
        assert tool.name == "create_project"

    def test_description_property(self):
        """description プロパティ"""
        mock_use_case = AsyncMock(spec=CreateProjectUseCase)
        tool = CreateProjectTool(mock_use_case, "U123")
        assert "プロジェクト" in tool.description

    def test_input_schema(self):
        """input_schema プロパティ"""
        mock_use_case = AsyncMock(spec=CreateProjectUseCase)
        tool = CreateProjectTool(mock_use_case, "U123")

        schema = tool.input_schema
        assert schema["type"] == "object"
        assert "name" in schema["properties"]
        assert schema["required"] == ["name"]
        assert "description" in schema["properties"]
        assert "deadline" in schema["properties"]
        assert "owner_user_id" in schema["properties"]
