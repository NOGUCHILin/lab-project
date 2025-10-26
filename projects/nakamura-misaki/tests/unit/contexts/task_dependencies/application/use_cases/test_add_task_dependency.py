"""AddTaskDependencyUseCase Unit Tests

Tests for src/contexts/task_dependencies/application/use_cases/add_task_dependency.py

Following TDD Strategy (AAA Pattern)
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.contexts.personal_tasks.domain.repositories.task_repository import TaskRepository
from src.contexts.task_dependencies.application.dto.dependency_dto import CreateDependencyDTO
from src.contexts.task_dependencies.application.use_cases.add_task_dependency import AddTaskDependencyUseCase
from src.contexts.task_dependencies.domain.entities.task_dependency import TaskDependency
from src.contexts.task_dependencies.domain.repositories.dependency_repository import DependencyRepository


class TestAddTaskDependencyUseCase:
    """AddTaskDependencyUseCase tests"""

    @pytest.mark.asyncio
    async def test_add_dependency_success(self):
        """依存関係追加成功"""
        # Arrange
        mock_dependency_repo = AsyncMock(spec=DependencyRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        use_case = AddTaskDependencyUseCase(mock_dependency_repo, mock_task_repo)

        blocking_task_id = uuid4()
        blocked_task_id = uuid4()
        dto = CreateDependencyDTO(
            blocking_task_id=blocking_task_id,
            blocked_task_id=blocked_task_id,
        )

        # Setup mocks
        mock_blocking_task = MagicMock()
        mock_blocked_task = MagicMock()
        mock_task_repo.get_by_id.side_effect = [mock_blocking_task, mock_blocked_task]
        mock_dependency_repo.exists.return_value = False
        mock_dependency_repo.save.return_value = TaskDependency.create(
            blocking_task_id=blocking_task_id,
            blocked_task_id=blocked_task_id,
        )

        # Act
        result = await use_case.execute(dto)

        # Assert
        assert result.blocking_task_id == blocking_task_id
        assert result.blocked_task_id == blocked_task_id
        assert result.dependency_type == "blocks"
        mock_task_repo.get_by_id.assert_any_call(blocking_task_id)
        mock_task_repo.get_by_id.assert_any_call(blocked_task_id)
        mock_dependency_repo.exists.assert_called_once_with(
            blocking_task_id=blocking_task_id,
            blocked_task_id=blocked_task_id,
        )
        mock_dependency_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_dependency_when_blocking_task_not_found_raises_error(self):
        """ブロッキングタスクが存在しない場合エラー"""
        # Arrange
        mock_dependency_repo = AsyncMock(spec=DependencyRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        use_case = AddTaskDependencyUseCase(mock_dependency_repo, mock_task_repo)

        blocking_task_id = uuid4()
        blocked_task_id = uuid4()
        dto = CreateDependencyDTO(
            blocking_task_id=blocking_task_id,
            blocked_task_id=blocked_task_id,
        )

        # Setup mocks
        mock_task_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match=f"Blocking task {blocking_task_id} not found"):
            await use_case.execute(dto)

        mock_dependency_repo.exists.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_dependency_when_blocked_task_not_found_raises_error(self):
        """ブロックされたタスクが存在しない場合エラー"""
        # Arrange
        mock_dependency_repo = AsyncMock(spec=DependencyRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        use_case = AddTaskDependencyUseCase(mock_dependency_repo, mock_task_repo)

        blocking_task_id = uuid4()
        blocked_task_id = uuid4()
        dto = CreateDependencyDTO(
            blocking_task_id=blocking_task_id,
            blocked_task_id=blocked_task_id,
        )

        # Setup mocks
        mock_blocking_task = MagicMock()
        mock_task_repo.get_by_id.side_effect = [mock_blocking_task, None]

        # Act & Assert
        with pytest.raises(ValueError, match=f"Blocked task {blocked_task_id} not found"):
            await use_case.execute(dto)

        mock_dependency_repo.exists.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_dependency_when_already_exists_raises_error(self):
        """依存関係が既に存在する場合エラー"""
        # Arrange
        mock_dependency_repo = AsyncMock(spec=DependencyRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        use_case = AddTaskDependencyUseCase(mock_dependency_repo, mock_task_repo)

        blocking_task_id = uuid4()
        blocked_task_id = uuid4()
        dto = CreateDependencyDTO(
            blocking_task_id=blocking_task_id,
            blocked_task_id=blocked_task_id,
        )

        # Setup mocks
        mock_blocking_task = MagicMock()
        mock_blocked_task = MagicMock()
        mock_task_repo.get_by_id.side_effect = [mock_blocking_task, mock_blocked_task]
        mock_dependency_repo.exists.return_value = True

        # Act & Assert
        with pytest.raises(ValueError, match="Dependency already exists"):
            await use_case.execute(dto)

        mock_dependency_repo.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_self_dependency_raises_error(self):
        """自己依存でエラー"""
        # Arrange
        mock_dependency_repo = AsyncMock(spec=DependencyRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        use_case = AddTaskDependencyUseCase(mock_dependency_repo, mock_task_repo)

        task_id = uuid4()
        dto = CreateDependencyDTO(
            blocking_task_id=task_id,
            blocked_task_id=task_id,
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Task cannot depend on itself"):
            await use_case.execute(dto)

        mock_task_repo.get_by_id.assert_not_called()
        mock_dependency_repo.exists.assert_not_called()
