"""CreateProjectUseCase Unit Tests

Tests for src/contexts/project_management/application/use_cases/create_project.py

Following TDD Strategy (AAA Pattern):
- Arrange: Setup test data and mocks
- Act: Execute use case
- Assert: Verify results
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from src.contexts.project_management.application.dto.project_dto import CreateProjectDTO, ProjectDTO
from src.contexts.project_management.application.use_cases.create_project import CreateProjectUseCase
from src.contexts.project_management.domain.entities.project import Project
from src.contexts.project_management.domain.repositories.project_repository import ProjectRepository
from src.contexts.project_management.domain.value_objects.project_status import ProjectStatus


class TestCreateProjectUseCase:
    """CreateProjectUseCase tests"""

    @pytest.mark.asyncio
    async def test_create_project_with_minimum_required_fields(self):
        """プロジェクト作成 - 必須フィールドのみ"""
        # Arrange
        mock_repo = AsyncMock(spec=ProjectRepository)
        use_case = CreateProjectUseCase(mock_repo)

        dto = CreateProjectDTO(
            name="新規プロジェクト",
            owner_user_id="U123456",
        )

        # Mock repository to return saved project
        def mock_save(project: Project) -> Project:
            return project

        mock_repo.save.side_effect = mock_save

        # Act
        result = await use_case.execute(dto)

        # Assert
        assert isinstance(result, ProjectDTO)
        assert result.name == "新規プロジェクト"
        assert result.owner_user_id == "U123456"
        assert result.status == ProjectStatus.ACTIVE.value
        assert result.description is None
        assert result.deadline is None
        assert result.task_count == 0
        assert result.completed_task_count == 0
        assert isinstance(result.project_id, UUID)

        # Verify repository was called
        mock_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_project_with_all_fields(self):
        """プロジェクト作成 - 全フィールド指定"""
        # Arrange
        mock_repo = AsyncMock(spec=ProjectRepository)
        use_case = CreateProjectUseCase(mock_repo)

        deadline = datetime.now() + timedelta(days=30)
        dto = CreateProjectDTO(
            name="完全指定プロジェクト",
            owner_user_id="U123456",
            description="詳細説明",
            deadline=deadline,
        )

        # Mock repository
        def mock_save(project: Project) -> Project:
            return project

        mock_repo.save.side_effect = mock_save

        # Act
        result = await use_case.execute(dto)

        # Assert
        assert result.name == "完全指定プロジェクト"
        assert result.owner_user_id == "U123456"
        assert result.description == "詳細説明"
        assert result.deadline == deadline
        mock_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_project_with_empty_name_raises_error(self):
        """空のプロジェクト名でエラー"""
        # Arrange
        mock_repo = AsyncMock(spec=ProjectRepository)
        use_case = CreateProjectUseCase(mock_repo)

        dto = CreateProjectDTO(
            name="",
            owner_user_id="U123456",
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Project name cannot be empty"):
            await use_case.execute(dto)

        # Verify repository was NOT called
        mock_repo.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_project_with_whitespace_only_name_raises_error(self):
        """空白のみのプロジェクト名でエラー"""
        # Arrange
        mock_repo = AsyncMock(spec=ProjectRepository)
        use_case = CreateProjectUseCase(mock_repo)

        dto = CreateProjectDTO(
            name="   ",
            owner_user_id="U123456",
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Project name cannot be empty"):
            await use_case.execute(dto)

        mock_repo.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_project_with_empty_owner_raises_error(self):
        """空のオーナーIDでエラー"""
        # Arrange
        mock_repo = AsyncMock(spec=ProjectRepository)
        use_case = CreateProjectUseCase(mock_repo)

        dto = CreateProjectDTO(
            name="テストプロジェクト",
            owner_user_id="",
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Owner user ID cannot be empty"):
            await use_case.execute(dto)

        mock_repo.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_project_trims_whitespace_from_name(self):
        """プロジェクト名の前後空白をトリム"""
        # Arrange
        mock_repo = AsyncMock(spec=ProjectRepository)
        use_case = CreateProjectUseCase(mock_repo)

        dto = CreateProjectDTO(
            name="  プロジェクト名  ",
            owner_user_id="U123456",
        )

        # Mock repository
        def mock_save(project: Project) -> Project:
            return project

        mock_repo.save.side_effect = mock_save

        # Act
        result = await use_case.execute(dto)

        # Assert
        assert result.name == "プロジェクト名"  # Trimmed
        mock_repo.save.assert_called_once()
