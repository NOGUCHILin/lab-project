"""Unit tests for CompleteTaskUseCase"""

from uuid import uuid4

import pytest

from src.contexts.personal_tasks.application.use_cases.complete_task import CompleteTaskUseCase
from src.contexts.personal_tasks.application.dto.task_dto import TaskDTO
from src.contexts.personal_tasks.domain.repositories.task_repository import TaskRepository
from src.contexts.personal_tasks.domain.models.task import Task
from src.shared_kernel.domain.value_objects.task_status import TaskStatus


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
        return []

    async def list_overdue(self, user_id: str):
        return []

    async def delete(self, task_id):
        if task_id in self.tasks:
            del self.tasks[task_id]


class TestCompleteTaskUseCase:
    """Test suite for CompleteTaskUseCase"""

    @pytest.fixture
    def repository(self) -> FakeTaskRepository:
        return FakeTaskRepository()

    @pytest.fixture
    def use_case(self, repository: FakeTaskRepository) -> CompleteTaskUseCase:
        return CompleteTaskUseCase(task_repository=repository)

    @pytest.mark.asyncio
    async def test_complete_pending_task(
        self,
        use_case: CompleteTaskUseCase,
        repository: FakeTaskRepository
    ):
        """Test completing a pending task"""
        # Create and save a pending task
        task = Task.create("Test Task", "U123", "U123")
        await repository.save(task)

        # Complete the task
        result = await use_case.execute(task.id)

        assert isinstance(result, TaskDTO)
        assert result.id == task.id
        assert result.status == "completed"
        assert result.completed_at is not None

        # Verify task was updated in repository
        saved_task = await repository.get_by_id(task.id)
        assert saved_task.status == TaskStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_complete_task_not_found(
        self,
        use_case: CompleteTaskUseCase,
        repository: FakeTaskRepository
    ):
        """Test completing non-existent task raises error"""
        non_existent_id = uuid4()

        with pytest.raises(ValueError, match="Task not found"):
            await use_case.execute(non_existent_id)

    @pytest.mark.asyncio
    async def test_complete_already_completed_task(
        self,
        use_case: CompleteTaskUseCase,
        repository: FakeTaskRepository
    ):
        """Test completing already completed task raises error"""
        # Create and complete a task
        task = Task.create("Test Task", "U123", "U123")
        task.complete()
        await repository.save(task)

        # Try to complete again
        with pytest.raises(ValueError, match="Task is already completed"):
            await use_case.execute(task.id)

    @pytest.mark.asyncio
    async def test_complete_task_updates_timestamps(
        self,
        use_case: CompleteTaskUseCase,
        repository: FakeTaskRepository
    ):
        """Test that completing task updates both completed_at and updated_at"""
        task = Task.create("Test Task", "U123", "U123")
        original_updated_at = task.updated_at
        await repository.save(task)

        result = await use_case.execute(task.id)

        assert result.completed_at is not None
        assert result.updated_at > original_updated_at
        assert result.completed_at == result.updated_at

    @pytest.mark.asyncio
    async def test_complete_multiple_tasks(
        self,
        use_case: CompleteTaskUseCase,
        repository: FakeTaskRepository
    ):
        """Test completing multiple tasks independently"""
        task1 = Task.create("Task 1", "U123", "U123")
        task2 = Task.create("Task 2", "U123", "U123")
        task3 = Task.create("Task 3", "U123", "U123")

        await repository.save(task1)
        await repository.save(task2)
        await repository.save(task3)

        # Complete only task1 and task3
        await use_case.execute(task1.id)
        await use_case.execute(task3.id)

        # Verify states
        saved_task1 = await repository.get_by_id(task1.id)
        saved_task2 = await repository.get_by_id(task2.id)
        saved_task3 = await repository.get_by_id(task3.id)

        assert saved_task1.status == TaskStatus.COMPLETED
        assert saved_task2.status == TaskStatus.PENDING
        assert saved_task3.status == TaskStatus.COMPLETED
