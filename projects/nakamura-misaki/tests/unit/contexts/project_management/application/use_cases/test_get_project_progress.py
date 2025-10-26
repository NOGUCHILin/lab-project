"""GetProjectProgressUseCase Unit Tests

Tests for src/contexts/project_management/application/use_cases/get_project_progress.py
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.contexts.personal_tasks.domain.repositories.task_repository import TaskRepository
from src.contexts.project_management.application.dto.project_dto import ProjectProgressDTO
from src.contexts.project_management.application.use_cases.get_project_progress import GetProjectProgressUseCase
from src.contexts.project_management.domain.entities.project import Project
from src.contexts.project_management.domain.repositories.project_repository import ProjectRepository
from src.shared_kernel.domain.value_objects.task_status import TaskStatus


class TestGetProjectProgressUseCase:
    """GetProjectProgressUseCase tests"""

    @pytest.mark.asyncio
    async def test_get_progress_for_empty_project(self):
        """空のプロジェクトの進捗取得"""
        # Arrange
        mock_project_repo = AsyncMock(spec=ProjectRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        use_case = GetProjectProgressUseCase(mock_project_repo, mock_task_repo)

        project_id = uuid4()
        project = Project.create(name="Empty Project", owner_user_id="U123")

        # Setup mocks
        mock_project_repo.find_by_id.return_value = project
        mock_project_repo.get_task_ids.return_value = []

        # Act
        result = await use_case.execute(project_id)

        # Assert
        assert isinstance(result, ProjectProgressDTO)
        assert result.project_id == project.project_id
        assert result.name == "Empty Project"
        assert result.total_tasks == 0
        assert result.completed_tasks == 0
        assert result.in_progress_tasks == 0
        assert result.pending_tasks == 0
        assert result.completion_percentage == 0.0

    @pytest.mark.asyncio
    async def test_get_progress_with_all_completed_tasks(self):
        """すべて完了済みタスクの進捗取得"""
        # Arrange
        mock_project_repo = AsyncMock(spec=ProjectRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        use_case = GetProjectProgressUseCase(mock_project_repo, mock_task_repo)

        project_id = uuid4()
        project = Project.create(name="Test Project", owner_user_id="U123")

        # 3つの完了済みタスク (Mock)
        task1 = MagicMock()
        task1.status = TaskStatus.COMPLETED
        task2 = MagicMock()
        task2.status = TaskStatus.COMPLETED
        task3 = MagicMock()
        task3.status = TaskStatus.COMPLETED

        task_ids = [uuid4(), uuid4(), uuid4()]

        # Setup mocks
        mock_project_repo.find_by_id.return_value = project
        mock_project_repo.get_task_ids.return_value = task_ids
        mock_task_repo.get_by_id.side_effect = [task1, task2, task3]

        # Act
        result = await use_case.execute(project_id)

        # Assert
        assert result.total_tasks == 3
        assert result.completed_tasks == 3
        assert result.in_progress_tasks == 0
        assert result.pending_tasks == 0
        assert result.completion_percentage == 100.0

    @pytest.mark.asyncio
    async def test_get_progress_with_mixed_status_tasks(self):
        """混合ステータスタスクの進捗取得"""
        # Arrange
        mock_project_repo = AsyncMock(spec=ProjectRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        use_case = GetProjectProgressUseCase(mock_project_repo, mock_task_repo)

        project_id = uuid4()
        project = Project.create(name="Test Project", owner_user_id="U123")

        # 完了1、進行中1、保留2 (Mock)
        task_completed = MagicMock()
        task_completed.status = TaskStatus.COMPLETED

        task_in_progress = MagicMock()
        task_in_progress.status = TaskStatus.IN_PROGRESS

        task_pending1 = MagicMock()
        task_pending1.status = TaskStatus.PENDING

        task_pending2 = MagicMock()
        task_pending2.status = TaskStatus.PENDING

        task_ids = [uuid4(), uuid4(), uuid4(), uuid4()]

        # Setup mocks
        mock_project_repo.find_by_id.return_value = project
        mock_project_repo.get_task_ids.return_value = task_ids
        mock_task_repo.get_by_id.side_effect = [
            task_completed,
            task_in_progress,
            task_pending1,
            task_pending2,
        ]

        # Act
        result = await use_case.execute(project_id)

        # Assert
        assert result.total_tasks == 4
        assert result.completed_tasks == 1
        assert result.in_progress_tasks == 1
        assert result.pending_tasks == 2
        assert result.completion_percentage == 25.0  # 1/4 * 100

    @pytest.mark.asyncio
    async def test_get_progress_when_project_not_found_raises_error(self):
        """プロジェクトが存在しない場合エラー"""
        # Arrange
        mock_project_repo = AsyncMock(spec=ProjectRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        use_case = GetProjectProgressUseCase(mock_project_repo, mock_task_repo)

        project_id = uuid4()

        # Setup mocks
        mock_project_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match=f"Project {project_id} not found"):
            await use_case.execute(project_id)

    @pytest.mark.asyncio
    async def test_completion_percentage_rounds_to_two_decimals(self):
        """完了率が小数点第2位まで丸められる"""
        # Arrange
        mock_project_repo = AsyncMock(spec=ProjectRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        use_case = GetProjectProgressUseCase(mock_project_repo, mock_task_repo)

        project_id = uuid4()
        project = Project.create(name="Test Project", owner_user_id="U123")

        # 3つのタスクのうち1つ完了 (1/3 = 33.33...%)
        task_completed = MagicMock()
        task_completed.status = TaskStatus.COMPLETED

        task_pending1 = MagicMock()
        task_pending1.status = TaskStatus.PENDING

        task_pending2 = MagicMock()
        task_pending2.status = TaskStatus.PENDING

        task_ids = [uuid4(), uuid4(), uuid4()]

        # Setup mocks
        mock_project_repo.find_by_id.return_value = project
        mock_project_repo.get_task_ids.return_value = task_ids
        mock_task_repo.get_by_id.side_effect = [task_completed, task_pending1, task_pending2]

        # Act
        result = await use_case.execute(project_id)

        # Assert
        assert result.completion_percentage == 33.33
