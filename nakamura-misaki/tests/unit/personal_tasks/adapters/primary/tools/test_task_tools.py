"""Unit tests for Task Tools (MCP tools adapter)"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.contexts.personal_tasks.adapters.primary.tools.task_tools import (
    CompleteTaskParams,
    QueryUserTasksParams,
    RegisterTaskParams,
    TaskTools,
    UpdateTaskParams,
)
from src.contexts.personal_tasks.application.use_cases.complete_task import CompleteTaskUseCase
from src.contexts.personal_tasks.application.use_cases.query_due_tasks import QueryDueTasksUseCase
from src.contexts.personal_tasks.application.use_cases.query_user_tasks import QueryUserTasksUseCase
from src.contexts.personal_tasks.application.use_cases.register_task import RegisterTaskUseCase
from src.contexts.personal_tasks.application.use_cases.update_task import UpdateTaskUseCase
from src.contexts.personal_tasks.domain.models.task import Task
from src.contexts.personal_tasks.domain.repositories.task_repository import TaskRepository


class FakeTaskRepository(TaskRepository):
    """Fake repository for testing"""

    def __init__(self):
        self.tasks: dict = {}

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
        today = datetime.now(UTC).date()
        return [
            t for t in self.tasks.values()
            if t.assignee_user_id == user_id
            and t.due_at
            and t.due_at.date() == today
        ]

    async def list_overdue(self, user_id: str):
        now = datetime.now(UTC)
        return [
            t for t in self.tasks.values()
            if t.assignee_user_id == user_id
            and t.due_at
            and t.due_at < now
        ]

    async def delete(self, task_id):
        if task_id in self.tasks:
            del self.tasks[task_id]


class TestTaskTools:
    """Test suite for TaskTools adapter"""

    @pytest.fixture
    def repository(self) -> FakeTaskRepository:
        return FakeTaskRepository()

    @pytest.fixture
    def register_use_case(self, repository: FakeTaskRepository) -> RegisterTaskUseCase:
        return RegisterTaskUseCase(task_repository=repository)

    @pytest.fixture
    def complete_use_case(self, repository: FakeTaskRepository) -> CompleteTaskUseCase:
        return CompleteTaskUseCase(task_repository=repository)

    @pytest.fixture
    def update_use_case(self, repository: FakeTaskRepository) -> UpdateTaskUseCase:
        return UpdateTaskUseCase(task_repository=repository)

    @pytest.fixture
    def query_user_tasks_use_case(self, repository: FakeTaskRepository) -> QueryUserTasksUseCase:
        return QueryUserTasksUseCase(task_repository=repository)

    @pytest.fixture
    def query_due_tasks_use_case(self, repository: FakeTaskRepository) -> QueryDueTasksUseCase:
        return QueryDueTasksUseCase(task_repository=repository)

    @pytest.fixture
    def task_tools(
        self,
        register_use_case: RegisterTaskUseCase,
        complete_use_case: CompleteTaskUseCase,
        update_use_case: UpdateTaskUseCase,
        query_user_tasks_use_case: QueryUserTasksUseCase,
        query_due_tasks_use_case: QueryDueTasksUseCase,
    ) -> TaskTools:
        return TaskTools(
            register_task_use_case=register_use_case,
            complete_task_use_case=complete_use_case,
            update_task_use_case=update_use_case,
            query_user_tasks_use_case=query_user_tasks_use_case,
            query_due_tasks_use_case=query_due_tasks_use_case,
        )

    @pytest.mark.asyncio
    async def test_register_task(self, task_tools: TaskTools):
        """Test registering a task via MCP tool"""
        params = RegisterTaskParams(
            title="Test Task",
            assignee_user_id="U123",
            creator_user_id="U456",
            description="Test description"
        )

        result = await task_tools.register_task(params)

        assert "success" in result
        assert "task_id" in result
        assert "title" in result
        assert result["title"] == "Test Task"
        assert result["status"] == "pending"

    @pytest.mark.asyncio
    async def test_complete_task(
        self,
        task_tools: TaskTools,
        repository: FakeTaskRepository
    ):
        """Test completing a task via MCP tool"""
        # Create task first
        task = Task.create("Test Task", "U123", "U123")
        await repository.save(task)

        params = CompleteTaskParams(task_id=str(task.id))
        result = await task_tools.complete_task(params)

        assert result["success"] is True
        assert result["status"] == "completed"
        assert result["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_complete_task_not_found(self, task_tools: TaskTools):
        """Test completing non-existent task returns error"""
        params = CompleteTaskParams(task_id=str(uuid4()))
        result = await task_tools.complete_task(params)

        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_update_task(
        self,
        task_tools: TaskTools,
        repository: FakeTaskRepository
    ):
        """Test updating a task via MCP tool"""
        # Create task first
        task = Task.create("Old Title", "U123", "U123")
        await repository.save(task)

        params = UpdateTaskParams(
            task_id=str(task.id),
            title="New Title",
            description="New description"
        )
        result = await task_tools.update_task(params)

        assert result["success"] is True
        assert result["title"] == "New Title"
        assert result["description"] == "New description"

    @pytest.mark.asyncio
    async def test_update_task_not_found(self, task_tools: TaskTools):
        """Test updating non-existent task returns error"""
        params = UpdateTaskParams(
            task_id=str(uuid4()),
            title="New Title"
        )
        result = await task_tools.update_task(params)

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_query_user_tasks(
        self,
        task_tools: TaskTools,
        repository: FakeTaskRepository
    ):
        """Test querying user tasks via MCP tool"""
        # Create tasks
        task1 = Task.create("Task 1", "U123", "U123")
        task2 = Task.create("Task 2", "U123", "U123")
        task2.complete()

        await repository.save(task1)
        await repository.save(task2)

        params = QueryUserTasksParams(user_id="U123")
        result = await task_tools.query_user_tasks(params)

        assert "tasks" in result
        assert len(result["tasks"]) == 2

    @pytest.mark.asyncio
    async def test_query_user_tasks_with_status_filter(
        self,
        task_tools: TaskTools,
        repository: FakeTaskRepository
    ):
        """Test querying user tasks with status filter"""
        # Create tasks
        task1 = Task.create("Task 1", "U123", "U123")
        task2 = Task.create("Task 2", "U123", "U123")
        task2.complete()

        await repository.save(task1)
        await repository.save(task2)

        params = QueryUserTasksParams(user_id="U123", status="pending")
        result = await task_tools.query_user_tasks(params)

        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["status"] == "pending"

    @pytest.mark.asyncio
    async def test_query_due_today(
        self,
        task_tools: TaskTools,
        repository: FakeTaskRepository
    ):
        """Test querying tasks due today"""
        # Create task due today
        task = Task.create("Due Today", "U123", "U123", due_at=datetime.now(UTC))
        await repository.save(task)

        result = await task_tools.query_due_today(user_id="U123")

        assert "tasks" in result
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["title"] == "Due Today"

    @pytest.mark.asyncio
    async def test_query_overdue(
        self,
        task_tools: TaskTools,
        repository: FakeTaskRepository
    ):
        """Test querying overdue tasks"""
        # Create overdue task
        from datetime import timedelta
        past = datetime.now(UTC) - timedelta(days=1)
        task = Task.create("Overdue", "U123", "U123", due_at=past)
        await repository.save(task)

        result = await task_tools.query_overdue(user_id="U123")

        assert "tasks" in result
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["title"] == "Overdue"
