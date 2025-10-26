"""AddTaskToProjectUseCase Unit Tests

Tests for src/contexts/project_management/application/use_cases/add_task_to_project.py
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.contexts.personal_tasks.domain.repositories.task_repository import TaskRepository
from src.contexts.project_management.application.use_cases.add_task_to_project import AddTaskToProjectUseCase
from src.contexts.project_management.domain.entities.project import Project
from src.contexts.project_management.domain.repositories.project_repository import ProjectRepository


class TestAddTaskToProjectUseCase:
    """AddTaskToProjectUseCase tests"""

    @pytest.mark.asyncio
    async def test_add_task_to_project_success(self):
        """タスク追加成功"""
        # Arrange
        mock_project_repo = AsyncMock(spec=ProjectRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        use_case = AddTaskToProjectUseCase(mock_project_repo, mock_task_repo)

        project_id = uuid4()
        task_id = uuid4()
        project = Project.create(name="Test Project", owner_user_id="U123")

        # Setup mocks (task exists - using MagicMock instead of real Task)
        mock_task = MagicMock()
        mock_task_repo.get_by_id.return_value = mock_task
        mock_project_repo.find_by_id.return_value = project
        mock_project_repo.get_task_ids.return_value = []
        mock_project_repo.add_task_to_project.return_value = None
        mock_project_repo.save.return_value = project

        # Act
        await use_case.execute(project_id, task_id)

        # Assert
        mock_task_repo.get_by_id.assert_called_once_with(task_id)
        mock_project_repo.find_by_id.assert_called_once_with(project_id)
        mock_project_repo.get_task_ids.assert_called_once_with(project_id)
        mock_project_repo.add_task_to_project.assert_called_once_with(
            project_id=project_id,
            task_id=task_id,
            position=0,
        )
        mock_project_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_task_when_task_not_found_raises_error(self):
        """タスクが存在しない場合エラー"""
        # Arrange
        mock_project_repo = AsyncMock(spec=ProjectRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        use_case = AddTaskToProjectUseCase(mock_project_repo, mock_task_repo)

        project_id = uuid4()
        task_id = uuid4()

        # Setup mocks
        mock_task_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match=f"Task {task_id} not found"):
            await use_case.execute(project_id, task_id)

        mock_project_repo.find_by_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_task_when_project_not_found_raises_error(self):
        """プロジェクトが存在しない場合エラー"""
        # Arrange
        mock_project_repo = AsyncMock(spec=ProjectRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        use_case = AddTaskToProjectUseCase(mock_project_repo, mock_task_repo)

        project_id = uuid4()
        task_id = uuid4()

        # Setup mocks
        mock_task = MagicMock()
        mock_task_repo.get_by_id.return_value = mock_task
        mock_project_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match=f"Project {project_id} not found"):
            await use_case.execute(project_id, task_id)

        mock_project_repo.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_duplicate_task_raises_error(self):
        """既に存在するタスク追加でエラー"""
        # Arrange
        mock_project_repo = AsyncMock(spec=ProjectRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        use_case = AddTaskToProjectUseCase(mock_project_repo, mock_task_repo)

        project_id = uuid4()
        task_id = uuid4()
        project = Project.create(name="Test Project", owner_user_id="U123")
        project.add_task(task_id)  # タスクを事前に追加

        # Setup mocks
        mock_task = MagicMock()
        mock_task_repo.get_by_id.return_value = mock_task
        mock_project_repo.find_by_id.return_value = project

        # Act & Assert
        with pytest.raises(ValueError, match="is already in the project"):
            await use_case.execute(project_id, task_id)

        mock_project_repo.add_task_to_project.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_second_task_with_correct_position(self):
        """2番目のタスク追加で位置が正しい"""
        # Arrange
        mock_project_repo = AsyncMock(spec=ProjectRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        use_case = AddTaskToProjectUseCase(mock_project_repo, mock_task_repo)

        project_id = uuid4()
        task_id = uuid4()
        existing_task_id = uuid4()
        project = Project.create(name="Test Project", owner_user_id="U123")

        # Setup mocks (1つのタスクが既に存在)
        mock_task = MagicMock()
        mock_task_repo.get_by_id.return_value = mock_task
        mock_project_repo.find_by_id.return_value = project
        mock_project_repo.get_task_ids.return_value = [existing_task_id]
        mock_project_repo.add_task_to_project.return_value = None
        mock_project_repo.save.return_value = project

        # Act
        await use_case.execute(project_id, task_id)

        # Assert
        mock_project_repo.add_task_to_project.assert_called_once_with(
            project_id=project_id,
            task_id=task_id,
            position=1,  # 2番目のタスクなので position=1
        )
