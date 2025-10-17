"""Unit tests for Task API routes"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.contexts.personal_tasks.adapters.primary.api.routes.tasks import create_task_router
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


@pytest.fixture
def repository() -> FakeTaskRepository:
    return FakeTaskRepository()


@pytest.fixture
def app(repository: FakeTaskRepository) -> FastAPI:
    """Create FastAPI app with task routes"""
    app = FastAPI()

    # Create use cases
    register_use_case = RegisterTaskUseCase(task_repository=repository)
    complete_use_case = CompleteTaskUseCase(task_repository=repository)
    update_use_case = UpdateTaskUseCase(task_repository=repository)
    query_user_tasks_use_case = QueryUserTasksUseCase(task_repository=repository)
    query_due_tasks_use_case = QueryDueTasksUseCase(task_repository=repository)

    # Create and include router
    router = create_task_router(
        register_task_use_case=register_use_case,
        complete_task_use_case=complete_use_case,
        update_task_use_case=update_use_case,
        query_user_tasks_use_case=query_user_tasks_use_case,
        query_due_tasks_use_case=query_due_tasks_use_case,
    )
    app.include_router(router)

    return app


@pytest.mark.asyncio
async def test_register_task(app: FastAPI):
    """Test POST /tasks - Register a new task"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/tasks",
            json={
                "title": "Test Task",
                "assignee_user_id": "U123",
                "creator_user_id": "U456",
                "description": "Test description"
            }
        )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["status"] == "pending"
    assert "id" in data


@pytest.mark.asyncio
async def test_complete_task(app: FastAPI, repository: FakeTaskRepository):
    """Test PATCH /tasks/{task_id}/complete - Complete a task"""
    # Create task first
    task = Task.create("Test Task", "U123", "U123")
    await repository.save(task)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.patch(f"/tasks/{task.id}/complete")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["completed_at"] is not None


@pytest.mark.asyncio
async def test_complete_task_not_found(app: FastAPI):
    """Test PATCH /tasks/{task_id}/complete - Task not found"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.patch(f"/tasks/{uuid4()}/complete")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_task(app: FastAPI, repository: FakeTaskRepository):
    """Test PATCH /tasks/{task_id} - Update a task"""
    # Create task first
    task = Task.create("Old Title", "U123", "U123")
    await repository.save(task)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.patch(
            f"/tasks/{task.id}",
            json={"title": "New Title", "description": "New description"}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["description"] == "New description"


@pytest.mark.asyncio
async def test_update_task_not_found(app: FastAPI):
    """Test PATCH /tasks/{task_id} - Task not found"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.patch(
            f"/tasks/{uuid4()}",
            json={"title": "New Title"}
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_query_user_tasks(app: FastAPI, repository: FakeTaskRepository):
    """Test GET /tasks - Query user tasks"""
    # Create tasks
    task1 = Task.create("Task 1", "U123", "U123")
    task2 = Task.create("Task 2", "U123", "U123")
    await repository.save(task1)
    await repository.save(task2)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/tasks?user_id=U123")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_query_user_tasks_with_status_filter(
    app: FastAPI,
    repository: FakeTaskRepository
):
    """Test GET /tasks?status=pending - Query with status filter"""
    # Create tasks
    task1 = Task.create("Task 1", "U123", "U123")
    task2 = Task.create("Task 2", "U123", "U123")
    task2.complete()
    await repository.save(task1)
    await repository.save(task2)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/tasks?user_id=U123&status=pending")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "pending"


@pytest.mark.asyncio
async def test_query_due_today(app: FastAPI, repository: FakeTaskRepository):
    """Test GET /tasks/due-today - Query tasks due today"""
    # Create task due today
    task = Task.create("Due Today", "U123", "U123", due_at=datetime.now(UTC))
    await repository.save(task)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/tasks/due-today?user_id=U123")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Due Today"


@pytest.mark.asyncio
async def test_query_overdue(app: FastAPI, repository: FakeTaskRepository):
    """Test GET /tasks/overdue - Query overdue tasks"""
    # Create overdue task
    from datetime import timedelta
    past = datetime.now(UTC) - timedelta(days=1)
    task = Task.create("Overdue", "U123", "U123", due_at=past)
    await repository.save(task)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/tasks/overdue?user_id=U123")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Overdue"
