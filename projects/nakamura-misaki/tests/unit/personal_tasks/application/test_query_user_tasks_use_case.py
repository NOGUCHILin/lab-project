"""Unit tests for QueryUserTasksUseCase"""

import pytest

from src.contexts.personal_tasks.application.use_cases.query_user_tasks import QueryUserTasksUseCase
from src.contexts.personal_tasks.domain.models.task import Task
from src.contexts.personal_tasks.domain.repositories.task_repository import TaskRepository
from src.shared_kernel.domain.value_objects.task_status import TaskStatus


class FakeTaskRepository(TaskRepository):
    """Fake repository for testing"""

    def __init__(self):
        self.tasks = {}

    async def save(self, task: Task) -> None:
        self.tasks[task.id] = task

    async def get_by_id(self, task_id):
        return self.tasks.get(task_id)

    async def list_by_user(self, user_id: str, status=None):
        tasks = [t for t in self.tasks.values() if t.assignee_user_id == user_id]
        if status:
            tasks = [t for t in tasks if t.status == status]
        return tasks

    async def list_due_today(self, user_id: str):
        return []

    async def list_overdue(self, user_id: str):
        return []

    async def delete(self, task_id):
        if task_id in self.tasks:
            del self.tasks[task_id]


class TestQueryUserTasksUseCase:
    """Test suite for QueryUserTasksUseCase"""

    @pytest.fixture
    def repository(self) -> FakeTaskRepository:
        return FakeTaskRepository()

    @pytest.fixture
    def use_case(self, repository: FakeTaskRepository) -> QueryUserTasksUseCase:
        return QueryUserTasksUseCase(task_repository=repository)

    @pytest.mark.asyncio
    async def test_query_all_user_tasks(
        self,
        use_case: QueryUserTasksUseCase,
        repository: FakeTaskRepository
    ):
        """Test querying all tasks for a user"""
        task1 = Task.create("Task 1", "U123", "U123")
        task2 = Task.create("Task 2", "U123", "U123")
        task3 = Task.create("Task 3", "U456", "U456")

        await repository.save(task1)
        await repository.save(task2)
        await repository.save(task3)

        results = await use_case.execute(user_id="U123")

        assert len(results) == 2
        assert all(r.assignee_user_id == "U123" for r in results)

    @pytest.mark.asyncio
    async def test_query_user_tasks_with_status_filter(
        self,
        use_case: QueryUserTasksUseCase,
        repository: FakeTaskRepository
    ):
        """Test querying tasks with status filter"""
        task1 = Task.create("Task 1", "U123", "U123")
        task2 = Task.create("Task 2", "U123", "U123")
        task2.complete()
        task3 = Task.create("Task 3", "U123", "U123")

        await repository.save(task1)
        await repository.save(task2)
        await repository.save(task3)

        # Query only pending tasks
        results = await use_case.execute(user_id="U123", status=TaskStatus.PENDING)

        assert len(results) == 2
        assert all(r.status == "pending" for r in results)

    @pytest.mark.asyncio
    async def test_query_user_tasks_empty_result(
        self,
        use_case: QueryUserTasksUseCase,
        repository: FakeTaskRepository
    ):
        """Test querying tasks for user with no tasks"""
        results = await use_case.execute(user_id="U999")

        assert results == []

    @pytest.mark.asyncio
    async def test_query_completed_tasks_only(
        self,
        use_case: QueryUserTasksUseCase,
        repository: FakeTaskRepository
    ):
        """Test querying only completed tasks"""
        task1 = Task.create("Task 1", "U123", "U123")
        task2 = Task.create("Task 2", "U123", "U123")
        task2.complete()

        await repository.save(task1)
        await repository.save(task2)

        results = await use_case.execute(user_id="U123", status=TaskStatus.COMPLETED)

        assert len(results) == 1
        assert results[0].status == "completed"
