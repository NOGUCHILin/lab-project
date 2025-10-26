"""CheckTaskBlockersUseCase Unit Tests"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.contexts.task_dependencies.application.use_cases.check_task_blockers import CheckTaskBlockersUseCase
from src.contexts.task_dependencies.domain.entities.task_dependency import TaskDependency
from src.contexts.task_dependencies.domain.repositories.dependency_repository import DependencyRepository


class TestCheckTaskBlockersUseCase:
    """CheckTaskBlockersUseCase tests"""

    @pytest.mark.asyncio
    async def test_check_blockers_with_blocking_tasks(self):
        """ブロッカーが存在する場合"""
        # Arrange
        mock_dependency_repo = AsyncMock(spec=DependencyRepository)
        use_case = CheckTaskBlockersUseCase(mock_dependency_repo)

        task_id = uuid4()
        blocker_id_1 = uuid4()
        blocker_id_2 = uuid4()

        dep1 = TaskDependency.create(blocking_task_id=blocker_id_1, blocked_task_id=task_id)
        dep2 = TaskDependency.create(blocking_task_id=blocker_id_2, blocked_task_id=task_id)

        mock_dependency_repo.find_blocking_dependencies.return_value = [dep1, dep2]

        # Act
        result = await use_case.execute(task_id)

        # Assert
        assert result.task_id == task_id
        assert result.is_blocked is True
        assert result.blocking_task_count == 2
        assert blocker_id_1 in result.blocking_task_ids
        assert blocker_id_2 in result.blocking_task_ids
        assert result.can_start is False

    @pytest.mark.asyncio
    async def test_check_blockers_with_no_blocking_tasks(self):
        """ブロッカーが存在しない場合"""
        # Arrange
        mock_dependency_repo = AsyncMock(spec=DependencyRepository)
        use_case = CheckTaskBlockersUseCase(mock_dependency_repo)

        task_id = uuid4()

        mock_dependency_repo.find_blocking_dependencies.return_value = []

        # Act
        result = await use_case.execute(task_id)

        # Assert
        assert result.task_id == task_id
        assert result.is_blocked is False
        assert result.blocking_task_count == 0
        assert len(result.blocking_task_ids) == 0
        assert result.can_start is True
