"""Unit tests for QueryDueTasksUseCase"""

from datetime import datetime, timedelta, UTC

import pytest

from src.contexts.personal_tasks.application.use_cases.query_due_tasks import QueryDueTasksUseCase
from src.contexts.personal_tasks.application.dto.task_dto import TaskDTO
from src.contexts.personal_tasks.domain.repositories.task_repository import TaskRepository
from src.contexts.personal_tasks.domain.models.task import Task


class FakeTaskRepository(TaskRepository):
    """Fake repository for testing"""

    def __init__(self):
        self.tasks: dict = {}

    async def save(self, task: Task) -> None:
        self.tasks[task.id] = task

    async def get_by_id(self, task_id):
        return self.tasks.get(task_id)

    async def list_by_user(self, user_id: str, status=None):
        return []

    async def list_due_today(self, user_id: str):
        """Return tasks due today"""
        today = datetime.now(UTC).date()
        return [
            task for task in self.tasks.values()
            if task.assignee_user_id == user_id
            and task.due_at
            and task.due_at.date() == today
        ]

    async def list_overdue(self, user_id: str):
        """Return overdue tasks"""
        now = datetime.now(UTC)
        return [
            task for task in self.tasks.values()
            if task.assignee_user_id == user_id
            and task.due_at
            and task.due_at < now
        ]

    async def delete(self, task_id):
        if task_id in self.tasks:
            del self.tasks[task_id]


class TestQueryDueTasksUseCase:
    """Test suite for QueryDueTasksUseCase"""

    @pytest.fixture
    def repository(self) -> FakeTaskRepository:
        return FakeTaskRepository()

    @pytest.fixture
    def use_case(self, repository: FakeTaskRepository) -> QueryDueTasksUseCase:
        return QueryDueTasksUseCase(task_repository=repository)

    @pytest.mark.asyncio
    async def test_query_due_today(
        self,
        use_case: QueryDueTasksUseCase,
        repository: FakeTaskRepository
    ):
        """Test querying tasks due today"""
        # Create tasks with different due dates
        today = datetime.now(UTC)
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)

        task_today = Task.create("Due Today", "U123", "U123", due_at=today)
        task_tomorrow = Task.create("Due Tomorrow", "U123", "U123", due_at=tomorrow)
        task_yesterday = Task.create("Due Yesterday", "U123", "U123", due_at=yesterday)

        await repository.save(task_today)
        await repository.save(task_tomorrow)
        await repository.save(task_yesterday)

        # Query tasks due today
        results = await use_case.execute_due_today(user_id="U123")

        assert len(results) == 1
        assert results[0].title == "Due Today"

    @pytest.mark.asyncio
    async def test_query_overdue(
        self,
        use_case: QueryDueTasksUseCase,
        repository: FakeTaskRepository
    ):
        """Test querying overdue tasks"""
        # Create tasks with different due dates
        now = datetime.now(UTC)
        future = now + timedelta(days=1)
        past1 = now - timedelta(hours=1)
        past2 = now - timedelta(days=2)

        task_future = Task.create("Future Task", "U123", "U123", due_at=future)
        task_past1 = Task.create("Overdue 1", "U123", "U123", due_at=past1)
        task_past2 = Task.create("Overdue 2", "U123", "U123", due_at=past2)

        await repository.save(task_future)
        await repository.save(task_past1)
        await repository.save(task_past2)

        # Query overdue tasks
        results = await use_case.execute_overdue(user_id="U123")

        assert len(results) == 2
        titles = {r.title for r in results}
        assert titles == {"Overdue 1", "Overdue 2"}

    @pytest.mark.asyncio
    async def test_query_due_today_empty(
        self,
        use_case: QueryDueTasksUseCase,
        repository: FakeTaskRepository
    ):
        """Test querying tasks due today returns empty list when none exist"""
        # Create tasks with different dates
        tomorrow = datetime.now(UTC) + timedelta(days=1)
        task = Task.create("Due Tomorrow", "U123", "U123", due_at=tomorrow)
        await repository.save(task)

        results = await use_case.execute_due_today(user_id="U123")

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_query_overdue_empty(
        self,
        use_case: QueryDueTasksUseCase,
        repository: FakeTaskRepository
    ):
        """Test querying overdue tasks returns empty list when none exist"""
        # Create future task
        future = datetime.now(UTC) + timedelta(days=1)
        task = Task.create("Future Task", "U123", "U123", due_at=future)
        await repository.save(task)

        results = await use_case.execute_overdue(user_id="U123")

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_query_filters_by_user(
        self,
        use_case: QueryDueTasksUseCase,
        repository: FakeTaskRepository
    ):
        """Test that queries filter by user correctly"""
        now = datetime.now(UTC)
        past = now - timedelta(days=1)

        # Tasks for different users
        task_user1 = Task.create("User1 Overdue", "U123", "U123", due_at=past)
        task_user2 = Task.create("User2 Overdue", "U456", "U456", due_at=past)

        await repository.save(task_user1)
        await repository.save(task_user2)

        # Query for U123 only
        results = await use_case.execute_overdue(user_id="U123")

        assert len(results) == 1
        assert results[0].assignee_user_id == "U123"

    @pytest.mark.asyncio
    async def test_query_returns_dto_objects(
        self,
        use_case: QueryDueTasksUseCase,
        repository: FakeTaskRepository
    ):
        """Test that queries return TaskDTO objects"""
        today = datetime.now(UTC)
        task = Task.create("Due Today", "U123", "U123", due_at=today)
        await repository.save(task)

        results = await use_case.execute_due_today(user_id="U123")

        assert len(results) == 1
        assert isinstance(results[0], TaskDTO)
        assert results[0].id == task.id
        assert results[0].title == "Due Today"
