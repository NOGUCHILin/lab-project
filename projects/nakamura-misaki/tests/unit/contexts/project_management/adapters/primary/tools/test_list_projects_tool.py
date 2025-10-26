"""ListProjectsTool Unit Tests"""

from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.contexts.project_management.adapters.primary.tools.project_tools import ListProjectsTool
from src.contexts.project_management.application.dto.project_dto import ProjectDTO
from src.contexts.project_management.application.use_cases.list_projects import ListProjectsUseCase


class TestListProjectsTool:
    """ListProjectsTool tests"""

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """プロジェクト一覧取得成功"""
        # Arrange
        mock_use_case = AsyncMock(spec=ListProjectsUseCase)
        user_id = "U123"
        tool = ListProjectsTool(mock_use_case, user_id)

        project1 = ProjectDTO(
            project_id=uuid4(),
            name="Project 1",
            owner_user_id=user_id,
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        project2 = ProjectDTO(
            project_id=uuid4(),
            name="Project 2",
            owner_user_id=user_id,
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_use_case.execute.return_value = [project1, project2]

        # Act
        result = await tool.execute()

        # Assert
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["count"] == 2
        assert len(result["data"]["projects"]) == 2
        mock_use_case.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_uses_current_user_when_owner_not_specified(self):
        """オーナー未指定時は現在のユーザーを使用"""
        # Arrange
        mock_use_case = AsyncMock(spec=ListProjectsUseCase)
        user_id = "U123"
        tool = ListProjectsTool(mock_use_case, user_id)

        mock_use_case.execute.return_value = []

        # Act
        result = await tool.execute()

        # Assert
        assert result["success"] is True
        # Verify the use case was called with current user_id
        call_args = mock_use_case.execute.call_args
        assert call_args.kwargs["owner_user_id"] == user_id

    @pytest.mark.asyncio
    async def test_execute_with_custom_owner(self):
        """カスタムオーナーIDを指定"""
        # Arrange
        mock_use_case = AsyncMock(spec=ListProjectsUseCase)
        tool = ListProjectsTool(mock_use_case, "U123")

        mock_use_case.execute.return_value = []

        # Act
        result = await tool.execute(owner_user_id="U999")

        # Assert
        assert result["success"] is True
        call_args = mock_use_case.execute.call_args
        assert call_args.kwargs["owner_user_id"] == "U999"

    @pytest.mark.asyncio
    async def test_execute_with_status_filter(self):
        """ステータスフィルタを指定"""
        # Arrange
        mock_use_case = AsyncMock(spec=ListProjectsUseCase)
        tool = ListProjectsTool(mock_use_case, "U123")

        mock_use_case.execute.return_value = []

        # Act
        result = await tool.execute(status="active")

        # Assert
        assert result["success"] is True
        call_args = mock_use_case.execute.call_args
        assert call_args.kwargs["status"].value == "active"

    @pytest.mark.asyncio
    async def test_execute_returns_empty_list_when_no_projects(self):
        """プロジェクトがない場合は空リスト"""
        # Arrange
        mock_use_case = AsyncMock(spec=ListProjectsUseCase)
        tool = ListProjectsTool(mock_use_case, "U123")

        mock_use_case.execute.return_value = []

        # Act
        result = await tool.execute()

        # Assert
        assert result["success"] is True
        assert result["data"]["count"] == 0
        assert result["data"]["projects"] == []

    @pytest.mark.asyncio
    async def test_execute_when_use_case_raises_exception(self):
        """Use Caseが例外を投げた場合"""
        # Arrange
        mock_use_case = AsyncMock(spec=ListProjectsUseCase)
        tool = ListProjectsTool(mock_use_case, "U123")

        mock_use_case.execute.side_effect = Exception("Database error")

        # Act
        result = await tool.execute()

        # Assert
        assert result["success"] is False
        assert "error" in result
        assert "Database error" in result["error"]

    def test_name_property(self):
        """name プロパティ"""
        mock_use_case = AsyncMock(spec=ListProjectsUseCase)
        tool = ListProjectsTool(mock_use_case, "U123")
        assert tool.name == "list_projects"

    def test_description_property(self):
        """description プロパティ"""
        mock_use_case = AsyncMock(spec=ListProjectsUseCase)
        tool = ListProjectsTool(mock_use_case, "U123")
        assert "一覧" in tool.description

    def test_input_schema(self):
        """input_schema プロパティ"""
        mock_use_case = AsyncMock(spec=ListProjectsUseCase)
        tool = ListProjectsTool(mock_use_case, "U123")

        schema = tool.input_schema
        assert schema["type"] == "object"
        assert "owner_user_id" in schema["properties"]
        assert "status" in schema["properties"]
        assert "enum" in schema["properties"]["status"]
