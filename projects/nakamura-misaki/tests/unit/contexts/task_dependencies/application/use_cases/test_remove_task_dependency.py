"""RemoveTaskDependencyUseCase Unit Tests"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.contexts.task_dependencies.application.use_cases.remove_task_dependency import RemoveTaskDependencyUseCase
from src.contexts.task_dependencies.domain.repositories.dependency_repository import DependencyRepository


class TestRemoveTaskDependencyUseCase:
    """RemoveTaskDependencyUseCase tests"""

    @pytest.mark.asyncio
    async def test_remove_dependency_success(self):
        """依存関係削除成功"""
        # Arrange
        mock_dependency_repo = AsyncMock(spec=DependencyRepository)
        use_case = RemoveTaskDependencyUseCase(mock_dependency_repo)

        blocking_task_id = uuid4()
        blocked_task_id = uuid4()

        mock_dependency_repo.delete_by_tasks.return_value = None

        # Act
        await use_case.execute(blocking_task_id, blocked_task_id)

        # Assert
        mock_dependency_repo.delete_by_tasks.assert_called_once_with(
            blocking_task_id=blocking_task_id,
            blocked_task_id=blocked_task_id,
        )
