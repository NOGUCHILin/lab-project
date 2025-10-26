"""PostgreSQLProjectRepository Integration Tests

Tests for src/contexts/project_management/infrastructure/repositories/postgresql_project_repository.py

Integration tests that verify the repository works correctly with the actual PostgreSQL database.
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.contexts.project_management.domain.entities.project import Project
from src.contexts.project_management.domain.value_objects.project_status import ProjectStatus
from src.contexts.project_management.infrastructure.repositories.postgresql_project_repository import (
    PostgreSQLProjectRepository,
)

pytestmark = pytest.mark.integration


class TestPostgreSQLProjectRepository:
    """Integration tests for PostgreSQLProjectRepository"""

    @pytest.fixture
    def repository(self, db_session: AsyncSession) -> PostgreSQLProjectRepository:
        """Create repository instance

        Args:
            db_session: Database session fixture

        Returns:
            PostgreSQLProjectRepository instance
        """
        return PostgreSQLProjectRepository(db_session)

    @pytest.mark.asyncio
    async def test_save_new_project(self, repository: PostgreSQLProjectRepository):
        """プロジェクトの新規作成"""
        # Arrange
        project = Project.create(
            name="New Integration Test Project",
            owner_user_id="U123456",
            description="Test Description",
        )

        # Act
        saved_project = await repository.save(project)

        # Assert
        assert saved_project.project_id == project.project_id
        assert saved_project.name == "New Integration Test Project"
        assert saved_project.owner_user_id == "U123456"
        assert saved_project.description == "Test Description"
        assert saved_project.status == ProjectStatus.ACTIVE

        # Verify it was persisted
        found_project = await repository.find_by_id(project.project_id)
        assert found_project is not None
        assert found_project.name == "New Integration Test Project"

    @pytest.mark.asyncio
    async def test_save_updates_existing_project(self, repository: PostgreSQLProjectRepository):
        """既存プロジェクトの更新"""
        # Arrange - Create project
        project = Project.create(
            name="Original Name",
            owner_user_id="U123456",
        )
        await repository.save(project)

        # Act - Update project
        project.update_details(name="Updated Name", description="New Description")
        updated_project = await repository.save(project)

        # Assert
        assert updated_project.name == "Updated Name"
        assert updated_project.description == "New Description"

        # Verify update was persisted
        found_project = await repository.find_by_id(project.project_id)
        assert found_project is not None
        assert found_project.name == "Updated Name"
        assert found_project.description == "New Description"

    @pytest.mark.asyncio
    async def test_find_by_id_existing_project(self, repository: PostgreSQLProjectRepository):
        """既存プロジェクトの検索"""
        # Arrange
        project = Project.create(
            name="Find Me",
            owner_user_id="U123456",
        )
        await repository.save(project)

        # Act
        found_project = await repository.find_by_id(project.project_id)

        # Assert
        assert found_project is not None
        assert found_project.project_id == project.project_id
        assert found_project.name == "Find Me"
        assert found_project.owner_user_id == "U123456"

    @pytest.mark.asyncio
    async def test_find_by_id_nonexistent_project(self, repository: PostgreSQLProjectRepository):
        """存在しないプロジェクトの検索"""
        # Arrange
        nonexistent_id = uuid4()

        # Act
        found_project = await repository.find_by_id(nonexistent_id)

        # Assert
        assert found_project is None

    @pytest.mark.asyncio
    async def test_find_by_owner_returns_all_projects(self, repository: PostgreSQLProjectRepository):
        """オーナーによるプロジェクト検索（全件）"""
        # Arrange
        owner_id = "U_OWNER_1"
        project1 = Project.create(name="Project 1", owner_user_id=owner_id)
        project2 = Project.create(name="Project 2", owner_user_id=owner_id)
        other_project = Project.create(name="Other Project", owner_user_id="U_OTHER")

        await repository.save(project1)
        await repository.save(project2)
        await repository.save(other_project)

        # Act
        projects = await repository.find_by_owner(owner_id)

        # Assert
        assert len(projects) == 2
        project_names = {p.name for p in projects}
        assert project_names == {"Project 1", "Project 2"}

    @pytest.mark.asyncio
    async def test_find_by_owner_with_status_filter(self, repository: PostgreSQLProjectRepository):
        """ステータスフィルタ付きでオーナーによる検索"""
        # Arrange
        owner_id = "U_OWNER_2"
        active_project = Project.create(name="Active Project", owner_user_id=owner_id)
        archived_project = Project.create(name="Archived Project", owner_user_id=owner_id)
        archived_project.archive()

        await repository.save(active_project)
        await repository.save(archived_project)

        # Act
        active_projects = await repository.find_by_owner(owner_id, status=ProjectStatus.ACTIVE)
        archived_projects = await repository.find_by_owner(owner_id, status=ProjectStatus.ARCHIVED)

        # Assert
        assert len(active_projects) == 1
        assert active_projects[0].name == "Active Project"

        assert len(archived_projects) == 1
        assert archived_projects[0].name == "Archived Project"

    @pytest.mark.asyncio
    async def test_delete_project(self, repository: PostgreSQLProjectRepository):
        """プロジェクトの削除"""
        # Arrange
        project = Project.create(name="To Be Deleted", owner_user_id="U123456")
        await repository.save(project)

        # Verify it exists
        found_project = await repository.find_by_id(project.project_id)
        assert found_project is not None

        # Act
        await repository.delete(project.project_id)

        # Assert
        deleted_project = await repository.find_by_id(project.project_id)
        assert deleted_project is None

    @pytest.mark.asyncio
    async def test_get_task_ids_empty_project(self, repository: PostgreSQLProjectRepository):
        """タスクが紐づいていないプロジェクト"""
        # Arrange
        project = Project.create(name="Empty Project", owner_user_id="U123456")
        await repository.save(project)

        # Act
        task_ids = await repository.get_task_ids(project.project_id)

        # Assert
        assert task_ids == []

    @pytest.mark.asyncio
    async def test_add_task_to_project(self, repository: PostgreSQLProjectRepository):
        """プロジェクトにタスクを追加"""
        # Arrange
        project = Project.create(name="Project with Tasks", owner_user_id="U123456")
        await repository.save(project)

        task_id_1 = uuid4()
        task_id_2 = uuid4()

        # Act
        await repository.add_task_to_project(project.project_id, task_id_1, position=0)
        await repository.add_task_to_project(project.project_id, task_id_2, position=1)

        # Assert
        task_ids = await repository.get_task_ids(project.project_id)
        assert len(task_ids) == 2
        assert task_ids[0] == task_id_1  # Position order
        assert task_ids[1] == task_id_2

    @pytest.mark.asyncio
    async def test_remove_task_from_project(self, repository: PostgreSQLProjectRepository):
        """プロジェクトからタスクを削除"""
        # Arrange
        project = Project.create(name="Project", owner_user_id="U123456")
        await repository.save(project)

        task_id_1 = uuid4()
        task_id_2 = uuid4()
        await repository.add_task_to_project(project.project_id, task_id_1, position=0)
        await repository.add_task_to_project(project.project_id, task_id_2, position=1)

        # Act
        await repository.remove_task_from_project(project.project_id, task_id_1)

        # Assert
        task_ids = await repository.get_task_ids(project.project_id)
        assert len(task_ids) == 1
        assert task_ids[0] == task_id_2

    @pytest.mark.asyncio
    async def test_find_by_id_includes_task_ids(self, repository: PostgreSQLProjectRepository):
        """find_by_idがtask_idsを含む"""
        # Arrange
        project = Project.create(name="Project", owner_user_id="U123456")
        await repository.save(project)

        task_id = uuid4()
        await repository.add_task_to_project(project.project_id, task_id, position=0)

        # Act
        found_project = await repository.find_by_id(project.project_id)

        # Assert
        assert found_project is not None
        assert len(found_project.task_ids) == 1
        assert found_project.task_ids[0] == task_id

    @pytest.mark.asyncio
    async def test_save_preserves_deadline(self, repository: PostgreSQLProjectRepository):
        """期限の保存と復元"""
        # Arrange
        deadline = datetime.now() + timedelta(days=30)
        project = Project.create(
            name="Project with Deadline",
            owner_user_id="U123456",
            deadline=deadline,
        )

        # Act
        await repository.save(project)
        found_project = await repository.find_by_id(project.project_id)

        # Assert
        assert found_project is not None
        assert found_project.deadline is not None
        # Compare as timestamps (microsecond precision may differ)
        assert abs((found_project.deadline - deadline).total_seconds()) < 1

    @pytest.mark.asyncio
    async def test_save_and_retrieve_project_status(self, repository: PostgreSQLProjectRepository):
        """プロジェクトステータスの保存と取得"""
        # Arrange
        project = Project.create(name="Test Project", owner_user_id="U123456")
        await repository.save(project)

        # Act - Complete the project
        project.complete()
        await repository.save(project)

        # Assert
        found_project = await repository.find_by_id(project.project_id)
        assert found_project is not None
        assert found_project.status == ProjectStatus.COMPLETED

        # Act - Archive the project
        project.archive()
        await repository.save(project)

        # Assert
        found_project = await repository.find_by_id(project.project_id)
        assert found_project is not None
        assert found_project.status == ProjectStatus.ARCHIVED
