"""GetDependencyChainUseCase Unit Tests"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.contexts.task_dependencies.application.use_cases.get_dependency_chain import GetDependencyChainUseCase
from src.contexts.task_dependencies.domain.entities.task_dependency import TaskDependency
from src.contexts.task_dependencies.domain.repositories.dependency_repository import DependencyRepository


class TestGetDependencyChainUseCase:
    """GetDependencyChainUseCase tests"""

    @pytest.mark.asyncio
    async def test_get_dependency_chain_success(self):
        """依存関係チェーン取得成功"""
        # Arrange
        mock_dependency_repo = AsyncMock(spec=DependencyRepository)
        use_case = GetDependencyChainUseCase(mock_dependency_repo)

        task_id = uuid4()
        blocker_id = uuid4()
        blocked_id = uuid4()

        blocking_dep = TaskDependency.create(blocking_task_id=blocker_id, blocked_task_id=task_id)
        blocked_dep = TaskDependency.create(blocking_task_id=task_id, blocked_task_id=blocked_id)

        mock_dependency_repo.find_blocking_dependencies.return_value = [blocking_dep]
        mock_dependency_repo.find_blocked_dependencies.return_value = [blocked_dep]
        mock_dependency_repo.find_all_blocking_task_ids.return_value = [blocker_id]

        # Act
        result = await use_case.execute(task_id)

        # Assert
        assert result.task_id == task_id
        assert len(result.blocking_dependencies) == 1
        assert len(result.blocked_dependencies) == 1
        assert blocker_id in result.all_blocking_task_ids

    @pytest.mark.asyncio
    async def test_get_dependency_chain_no_dependencies(self):
        """依存関係なし"""
        # Arrange
        mock_dependency_repo = AsyncMock(spec=DependencyRepository)
        use_case = GetDependencyChainUseCase(mock_dependency_repo)

        task_id = uuid4()

        mock_dependency_repo.find_blocking_dependencies.return_value = []
        mock_dependency_repo.find_blocked_dependencies.return_value = []
        mock_dependency_repo.find_all_blocking_task_ids.return_value = []

        # Act
        result = await use_case.execute(task_id)

        # Assert
        assert result.task_id == task_id
        assert len(result.blocking_dependencies) == 0
        assert len(result.blocked_dependencies) == 0
        assert len(result.all_blocking_task_ids) == 0
