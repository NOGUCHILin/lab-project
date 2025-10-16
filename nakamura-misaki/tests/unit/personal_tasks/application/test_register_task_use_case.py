"""Unit tests for RegisterTaskUseCase"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from src.contexts.personal_tasks.application.dto.task_dto import CreateTaskDTO, TaskDTO
from src.contexts.personal_tasks.application.use_cases.register_task import RegisterTaskUseCase
from src.contexts.personal_tasks.domain.models.task import Task
from src.contexts.personal_tasks.domain.repositories.task_repository import TaskRepository
from src.shared_kernel.domain.value_objects.task_status import TaskStatus


class FakeTaskRepository(TaskRepository):
    """Fake repository for testing"""

    def __init__(self):
        self.tasks: dict[UUID, Task] = {}

    async def save(self, task: Task) -> None:
        self.tasks[task.id] = task

    async def get_by_id(self, task_id: UUID) -> Task | None:
        return self.tasks.get(task_id)

    async def list_by_user(
        self,
        user_id: str,
        status: TaskStatus | None = None
    ) -> list[Task]:
        return []

    async def list_due_today(self, user_id: str) -> list[Task]:
        return []

    async def list_overdue(self, user_id: str) -> list[Task]:
        return []

    async def delete(self, task_id: UUID) -> None:
        if task_id in self.tasks:
            del self.tasks[task_id]


class TestRegisterTaskUseCase:
    """Test suite for RegisterTaskUseCase"""

    @pytest.fixture
    def repository(self) -> FakeTaskRepository:
        return FakeTaskRepository()

    @pytest.fixture
    def use_case(self, repository: FakeTaskRepository) -> RegisterTaskUseCase:
        return RegisterTaskUseCase(task_repository=repository)

    @pytest.mark.asyncio
    async def test_register_task_with_minimum_fields(
        self,
        use_case: RegisterTaskUseCase,
        repository: FakeTaskRepository
    ):
        """Test registering a task with only required fields"""
        dto = CreateTaskDTO(
            title="Complete Phase 1",
            assignee_user_id="U12345",
            creator_user_id="U12345"
        )

        result = await use_case.execute(dto)

        assert isinstance(result, TaskDTO)
        assert result.title == "Complete Phase 1"
        assert result.assignee_user_id == "U12345"
        assert result.creator_user_id == "U12345"
        assert result.status == "pending"
        assert result.description is None
        assert result.due_at is None
        assert isinstance(result.id, UUID)

        # Verify task was saved to repository
        assert len(repository.tasks) == 1
        saved_task = list(repository.tasks.values())[0]
        assert saved_task.title == "Complete Phase 1"

    @pytest.mark.asyncio
    async def test_register_task_with_all_fields(
        self,
        use_case: RegisterTaskUseCase,
        repository: FakeTaskRepository
    ):
        """Test registering a task with all optional fields"""
        due_date = datetime.now(UTC) + timedelta(days=1)
        dto = CreateTaskDTO(
            title="Complete Phase 1",
            assignee_user_id="U12345",
            creator_user_id="U67890",
            description="Implement Bounded Context structure",
            due_at=due_date
        )

        result = await use_case.execute(dto)

        assert result.title == "Complete Phase 1"
        assert result.description == "Implement Bounded Context structure"
        assert result.assignee_user_id == "U12345"
        assert result.creator_user_id == "U67890"
        assert result.due_at == due_date

        # Verify saved task
        saved_task = list(repository.tasks.values())[0]
        assert saved_task.due_at == due_date
        assert saved_task.description == "Implement Bounded Context structure"

    @pytest.mark.asyncio
    async def test_register_multiple_tasks(
        self,
        use_case: RegisterTaskUseCase,
        repository: FakeTaskRepository
    ):
        """Test registering multiple tasks"""
        dto1 = CreateTaskDTO("Task 1", "U123", "U123")
        dto2 = CreateTaskDTO("Task 2", "U123", "U123")
        dto3 = CreateTaskDTO("Task 3", "U123", "U123")

        result1 = await use_case.execute(dto1)
        result2 = await use_case.execute(dto2)
        result3 = await use_case.execute(dto3)

        assert len(repository.tasks) == 3
        assert result1.title == "Task 1"
        assert result2.title == "Task 2"
        assert result3.title == "Task 3"

    @pytest.mark.asyncio
    async def test_register_task_creates_timestamps(
        self,
        use_case: RegisterTaskUseCase,
        repository: FakeTaskRepository
    ):
        """Test that registering a task creates timestamps"""
        before = datetime.now(UTC)
        dto = CreateTaskDTO("Test Task", "U123", "U123")

        result = await use_case.execute(dto)

        after = datetime.now(UTC)
        assert before <= result.created_at <= after
        assert before <= result.updated_at <= after
        assert result.created_at == result.updated_at

    @pytest.mark.asyncio
    async def test_register_task_with_different_assignee_and_creator(
        self,
        use_case: RegisterTaskUseCase,
        repository: FakeTaskRepository
    ):
        """Test creating task where assignee differs from creator"""
        dto = CreateTaskDTO(
            title="Delegated Task",
            assignee_user_id="U12345",  # Assigned to someone
            creator_user_id="U67890"    # Created by someone else
        )

        result = await use_case.execute(dto)

        assert result.assignee_user_id == "U12345"
        assert result.creator_user_id == "U67890"
