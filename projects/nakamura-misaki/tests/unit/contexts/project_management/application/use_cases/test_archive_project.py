"""ArchiveProjectUseCase Unit Tests

Tests for src/contexts/project_management/application/use_cases/archive_project.py
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.contexts.project_management.application.dto.project_dto import ProjectDTO
from src.contexts.project_management.application.use_cases.archive_project import ArchiveProjectUseCase
from src.contexts.project_management.domain.entities.project import Project
from src.contexts.project_management.domain.repositories.project_repository import ProjectRepository
from src.contexts.project_management.domain.value_objects.project_status import ProjectStatus


class TestArchiveProjectUseCase:
    """ArchiveProjectUseCase tests"""

    @pytest.mark.asyncio
    async def test_archive_active_project(self):
        """アクティブプロジェクトをアーカイブ"""
        # Arrange
        mock_repo = AsyncMock(spec=ProjectRepository)
        use_case = ArchiveProjectUseCase(mock_repo)

        project_id = uuid4()
        project = Project.create(name="Test Project", owner_user_id="U123")
        assert project.status == ProjectStatus.ACTIVE

        # Setup mocks
        mock_repo.find_by_id.return_value = project

        # Mock save to simulate the archiving
        def mock_save(proj: Project) -> Project:
            return proj

        mock_repo.save.side_effect = mock_save

        # Act
        result = await use_case.execute(project_id)

        # Assert
        assert isinstance(result, ProjectDTO)
        assert result.status == ProjectStatus.ARCHIVED.value
        mock_repo.find_by_id.assert_called_once_with(project_id)
        mock_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_archive_completed_project(self):
        """完了済みプロジェクトをアーカイブ"""
        # Arrange
        mock_repo = AsyncMock(spec=ProjectRepository)
        use_case = ArchiveProjectUseCase(mock_repo)

        project_id = uuid4()
        project = Project.create(name="Test Project", owner_user_id="U123")
        project.complete()
        assert project.status == ProjectStatus.COMPLETED

        # Setup mocks
        mock_repo.find_by_id.return_value = project

        def mock_save(proj: Project) -> Project:
            return proj

        mock_repo.save.side_effect = mock_save

        # Act
        result = await use_case.execute(project_id)

        # Assert
        assert result.status == ProjectStatus.ARCHIVED.value
        mock_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_archive_when_project_not_found_raises_error(self):
        """プロジェクトが存在しない場合エラー"""
        # Arrange
        mock_repo = AsyncMock(spec=ProjectRepository)
        use_case = ArchiveProjectUseCase(mock_repo)

        project_id = uuid4()

        # Setup mocks
        mock_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match=f"Project {project_id} not found"):
            await use_case.execute(project_id)

        mock_repo.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_archive_already_archived_project_is_idempotent(self):
        """既にアーカイブ済みプロジェクトのアーカイブは冪等"""
        # Arrange
        mock_repo = AsyncMock(spec=ProjectRepository)
        use_case = ArchiveProjectUseCase(mock_repo)

        project_id = uuid4()
        project = Project.create(name="Test Project", owner_user_id="U123")
        project.archive()
        assert project.status == ProjectStatus.ARCHIVED

        # Setup mocks
        mock_repo.find_by_id.return_value = project

        def mock_save(proj: Project) -> Project:
            return proj

        mock_repo.save.side_effect = mock_save

        # Act
        result = await use_case.execute(project_id)

        # Assert
        assert result.status == ProjectStatus.ARCHIVED.value
        mock_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_archived_project_returns_correct_fields(self):
        """アーカイブされたプロジェクトが正しいフィールドを返す"""
        # Arrange
        mock_repo = AsyncMock(spec=ProjectRepository)
        use_case = ArchiveProjectUseCase(mock_repo)

        project_id = uuid4()
        project = Project.create(name="Test Project", owner_user_id="U123")
        project.add_task(uuid4())
        project.add_task(uuid4())

        # Setup mocks
        mock_repo.find_by_id.return_value = project

        def mock_save(proj: Project) -> Project:
            return proj

        mock_repo.save.side_effect = mock_save

        # Act
        result = await use_case.execute(project_id)

        # Assert
        assert result.project_id == project.project_id
        assert result.name == "Test Project"
        assert result.owner_user_id == "U123"
        assert result.task_count == 2
        assert result.completed_task_count == 0
