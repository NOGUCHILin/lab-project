"""RemoveTaskFromProjectUseCase Unit Tests

Tests for src/contexts/project_management/application/use_cases/remove_task_from_project.py
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.contexts.project_management.application.use_cases.remove_task_from_project import RemoveTaskFromProjectUseCase
from src.contexts.project_management.domain.entities.project import Project
from src.contexts.project_management.domain.repositories.project_repository import ProjectRepository


class TestRemoveTaskFromProjectUseCase:
    """RemoveTaskFromProjectUseCase tests"""

    @pytest.mark.asyncio
    async def test_remove_task_from_project_success(self):
        """タスク削除成功"""
        # Arrange
        mock_repo = AsyncMock(spec=ProjectRepository)
        use_case = RemoveTaskFromProjectUseCase(mock_repo)

        project_id = uuid4()
        task_id = uuid4()
        project = Project.create(name="Test Project", owner_user_id="U123")
        project.add_task(task_id)  # タスクを事前に追加

        # Setup mocks
        mock_repo.find_by_id.return_value = project
        mock_repo.remove_task_from_project.return_value = None
        mock_repo.save.return_value = project

        # Act
        await use_case.execute(project_id, task_id)

        # Assert
        mock_repo.find_by_id.assert_called_once_with(project_id)
        mock_repo.remove_task_from_project.assert_called_once_with(
            project_id=project_id,
            task_id=task_id,
        )
        mock_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_task_when_project_not_found_raises_error(self):
        """プロジェクトが存在しない場合エラー"""
        # Arrange
        mock_repo = AsyncMock(spec=ProjectRepository)
        use_case = RemoveTaskFromProjectUseCase(mock_repo)

        project_id = uuid4()
        task_id = uuid4()

        # Setup mocks
        mock_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match=f"Project {project_id} not found"):
            await use_case.execute(project_id, task_id)

        mock_repo.remove_task_from_project.assert_not_called()

    @pytest.mark.asyncio
    async def test_remove_nonexistent_task_raises_error(self):
        """存在しないタスク削除でエラー"""
        # Arrange
        mock_repo = AsyncMock(spec=ProjectRepository)
        use_case = RemoveTaskFromProjectUseCase(mock_repo)

        project_id = uuid4()
        task_id = uuid4()
        project = Project.create(name="Test Project", owner_user_id="U123")

        # Setup mocks
        mock_repo.find_by_id.return_value = project

        # Act & Assert
        with pytest.raises(ValueError, match="is not in the project"):
            await use_case.execute(project_id, task_id)

        mock_repo.remove_task_from_project.assert_not_called()
        mock_repo.save.assert_not_called()
