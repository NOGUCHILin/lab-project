"""ListProjectsUseCase Unit Tests

Tests for src/contexts/project_management/application/use_cases/list_projects.py
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.contexts.project_management.application.dto.project_dto import ProjectDTO
from src.contexts.project_management.application.use_cases.list_projects import ListProjectsUseCase
from src.contexts.project_management.domain.entities.project import Project
from src.contexts.project_management.domain.repositories.project_repository import ProjectRepository
from src.contexts.project_management.domain.value_objects.project_status import ProjectStatus


class TestListProjectsUseCase:
    """ListProjectsUseCase tests"""

    @pytest.mark.asyncio
    async def test_list_all_projects_for_user(self):
        """ユーザーのすべてのプロジェクトを一覧表示"""
        # Arrange
        mock_repo = AsyncMock(spec=ProjectRepository)
        use_case = ListProjectsUseCase(mock_repo)

        owner_user_id = "U123456"
        project1 = Project.create(name="Project 1", owner_user_id=owner_user_id)
        project2 = Project.create(name="Project 2", owner_user_id=owner_user_id)

        # Setup mocks
        mock_repo.find_by_owner.return_value = [project1, project2]

        # Act
        result = await use_case.execute(owner_user_id)

        # Assert
        assert len(result) == 2
        assert all(isinstance(dto, ProjectDTO) for dto in result)
        assert result[0].name == "Project 1"
        assert result[1].name == "Project 2"
        mock_repo.find_by_owner.assert_called_once_with(
            owner_user_id=owner_user_id,
            status=None,
        )

    @pytest.mark.asyncio
    async def test_list_projects_filtered_by_status(self):
        """ステータスでフィルタリングされたプロジェクト一覧"""
        # Arrange
        mock_repo = AsyncMock(spec=ProjectRepository)
        use_case = ListProjectsUseCase(mock_repo)

        owner_user_id = "U123456"
        project_active = Project.create(name="Active Project", owner_user_id=owner_user_id)

        # Setup mocks
        mock_repo.find_by_owner.return_value = [project_active]

        # Act
        result = await use_case.execute(owner_user_id, status=ProjectStatus.ACTIVE)

        # Assert
        assert len(result) == 1
        assert result[0].status == ProjectStatus.ACTIVE.value
        mock_repo.find_by_owner.assert_called_once_with(
            owner_user_id=owner_user_id,
            status=ProjectStatus.ACTIVE,
        )

    @pytest.mark.asyncio
    async def test_list_projects_returns_empty_list_when_no_projects(self):
        """プロジェクトがない場合は空のリストを返す"""
        # Arrange
        mock_repo = AsyncMock(spec=ProjectRepository)
        use_case = ListProjectsUseCase(mock_repo)

        owner_user_id = "U123456"

        # Setup mocks
        mock_repo.find_by_owner.return_value = []

        # Act
        result = await use_case.execute(owner_user_id)

        # Assert
        assert len(result) == 0
        assert result == []

    @pytest.mark.asyncio
    async def test_list_projects_includes_task_count(self):
        """プロジェクト一覧にタスク数が含まれる"""
        # Arrange
        mock_repo = AsyncMock(spec=ProjectRepository)
        use_case = ListProjectsUseCase(mock_repo)

        owner_user_id = "U123456"
        project = Project.create(name="Test Project", owner_user_id=owner_user_id)
        project.add_task(uuid4())
        project.add_task(uuid4())
        project.add_task(uuid4())

        # Setup mocks
        mock_repo.find_by_owner.return_value = [project]

        # Act
        result = await use_case.execute(owner_user_id)

        # Assert
        assert len(result) == 1
        assert result[0].task_count == 3

    @pytest.mark.asyncio
    async def test_list_projects_includes_all_project_fields(self):
        """プロジェクト一覧にすべてのフィールドが含まれる"""
        # Arrange
        mock_repo = AsyncMock(spec=ProjectRepository)
        use_case = ListProjectsUseCase(mock_repo)

        owner_user_id = "U123456"
        deadline = datetime.now() + timedelta(days=30)
        project = Project.create(
            name="Full Project",
            owner_user_id=owner_user_id,
            description="Description",
            deadline=deadline,
        )

        # Setup mocks
        mock_repo.find_by_owner.return_value = [project]

        # Act
        result = await use_case.execute(owner_user_id)

        # Assert
        assert len(result) == 1
        dto = result[0]
        assert dto.project_id == project.project_id
        assert dto.name == "Full Project"
        assert dto.owner_user_id == owner_user_id
        assert dto.status == ProjectStatus.ACTIVE.value
        assert dto.description == "Description"
        assert dto.deadline == deadline
        assert isinstance(dto.created_at, datetime)
        assert isinstance(dto.updated_at, datetime)
