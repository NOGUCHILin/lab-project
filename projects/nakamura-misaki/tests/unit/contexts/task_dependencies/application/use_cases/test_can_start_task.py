"""CanStartTaskUseCase Unit Tests"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.contexts.task_dependencies.application.use_cases.can_start_task import CanStartTaskUseCase
from src.contexts.task_dependencies.domain.entities.task_dependency import TaskDependency
from src.contexts.task_dependencies.domain.repositories.dependency_repository import DependencyRepository


class TestCanStartTaskUseCase:
    """CanStartTaskUseCase tests"""

    @pytest.mark.asyncio
    async def test_can_start_when_no_blockers(self):
        """ブロッカーなしで開始可能"""
        # Arrange
        mock_dependency_repo = AsyncMock(spec=DependencyRepository)
        use_case = CanStartTaskUseCase(mock_dependency_repo)

        task_id = uuid4()
        mock_dependency_repo.find_blocking_dependencies.return_value = []

        # Act
        result = await use_case.execute(task_id)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_cannot_start_when_blockers_exist(self):
        """ブロッカー存在で開始不可"""
        # Arrange
        mock_dependency_repo = AsyncMock(spec=DependencyRepository)
        use_case = CanStartTaskUseCase(mock_dependency_repo)

        task_id = uuid4()
        blocker_id = uuid4()
        dep = TaskDependency.create(blocking_task_id=blocker_id, blocked_task_id=task_id)

        mock_dependency_repo.find_blocking_dependencies.return_value = [dep]

        # Act
        result = await use_case.execute(task_id)

        # Assert
        assert result is False
