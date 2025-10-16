"""Unit tests for UpdateTaskUseCase"""

from datetime import datetime, timedelta, UTC
from uuid import uuid4

import pytest

from src.contexts.personal_tasks.application.use_cases.update_task import UpdateTaskUseCase
from src.contexts.personal_tasks.application.dto.task_dto import UpdateTaskDTO, TaskDTO
from src.contexts.personal_tasks.domain.repositories.task_repository import TaskRepository
from src.contexts.personal_tasks.domain.models.task import Task
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
        return []

    async def list_due_today(self, user_id: str):
        return []

    async def list_overdue(self, user_id: str):
        return []

    async def delete(self, task_id):
        if task_id in self.tasks:
            del self.tasks[task_id]


class TestUpdateTaskUseCase:
    """Test suite for UpdateTaskUseCase"""

    @pytest.fixture
    def repository(self) -> FakeTaskRepository:
        return FakeTaskRepository()

    @pytest.fixture
    def use_case(self, repository: FakeTaskRepository) -> UpdateTaskUseCase:
        return UpdateTaskUseCase(task_repository=repository)

    @pytest.mark.asyncio
    async def test_update_task_title(
        self,
        use_case: UpdateTaskUseCase,
        repository: FakeTaskRepository
    ):
        """Test updating task title"""
        task = Task.create("Original Title", "U123", "U123")
        await repository.save(task)

        dto = UpdateTaskDTO(title="Updated Title")
        result = await use_case.execute(task.id, dto)

        assert result.title == "Updated Title"
        assert result.id == task.id

        # Verify in repository
        saved_task = await repository.get_by_id(task.id)
        assert saved_task.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_update_task_description(
        self,
        use_case: UpdateTaskUseCase,
        repository: FakeTaskRepository
    ):
        """Test updating task description"""
        task = Task.create("Task", "U123", "U123")
        await repository.save(task)

        dto = UpdateTaskDTO(description="New description")
        result = await use_case.execute(task.id, dto)

        assert result.description == "New description"

    @pytest.mark.asyncio
    async def test_update_task_status(
        self,
        use_case: UpdateTaskUseCase,
        repository: FakeTaskRepository
    ):
        """Test updating task status"""
        task = Task.create("Task", "U123", "U123")
        await repository.save(task)

        dto = UpdateTaskDTO(status=TaskStatus.IN_PROGRESS)
        result = await use_case.execute(task.id, dto)

        assert result.status == "in_progress"

    @pytest.mark.asyncio
    async def test_update_task_due_date(
        self,
        use_case: UpdateTaskUseCase,
        repository: FakeTaskRepository
    ):
        """Test updating task due date"""
        task = Task.create("Task", "U123", "U123")
        await repository.save(task)

        new_due_date = datetime.now(UTC) + timedelta(days=3)
        dto = UpdateTaskDTO(due_at=new_due_date)
        result = await use_case.execute(task.id, dto)

        assert result.due_at == new_due_date

    @pytest.mark.asyncio
    async def test_update_multiple_fields(
        self,
        use_case: UpdateTaskUseCase,
        repository: FakeTaskRepository
    ):
        """Test updating multiple fields at once"""
        task = Task.create("Task", "U123", "U123")
        await repository.save(task)

        new_due_date = datetime.now(UTC) + timedelta(days=2)
        dto = UpdateTaskDTO(
            title="Updated Task",
            description="Updated desc",
            status=TaskStatus.IN_PROGRESS,
            due_at=new_due_date
        )
        result = await use_case.execute(task.id, dto)

        assert result.title == "Updated Task"
        assert result.description == "Updated desc"
        assert result.status == "in_progress"
        assert result.due_at == new_due_date

    @pytest.mark.asyncio
    async def test_update_task_not_found(
        self,
        use_case: UpdateTaskUseCase,
        repository: FakeTaskRepository
    ):
        """Test updating non-existent task raises error"""
        non_existent_id = uuid4()
        dto = UpdateTaskDTO(title="Test")

        with pytest.raises(ValueError, match="Task not found"):
            await use_case.execute(non_existent_id, dto)

    @pytest.mark.asyncio
    async def test_update_with_empty_dto(
        self,
        use_case: UpdateTaskUseCase,
        repository: FakeTaskRepository
    ):
        """Test update with no changes still updates timestamp"""
        task = Task.create("Task", "U123", "U123")
        original_updated_at = task.updated_at
        await repository.save(task)

        dto = UpdateTaskDTO()  # No changes
        result = await use_case.execute(task.id, dto)

        assert result.updated_at > original_updated_at
