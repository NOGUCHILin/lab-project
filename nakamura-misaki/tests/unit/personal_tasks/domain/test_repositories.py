"""Unit tests for Repository interfaces"""

from datetime import datetime, UTC
from uuid import UUID

import pytest

from src.contexts.personal_tasks.domain.models.task import Task
from src.contexts.personal_tasks.domain.models.conversation import Conversation
from src.contexts.personal_tasks.domain.repositories.task_repository import TaskRepository
from src.contexts.personal_tasks.domain.repositories.conversation_repository import ConversationRepository
from src.shared_kernel.domain.value_objects.task_status import TaskStatus


class FakeTaskRepository(TaskRepository):
    """Fake implementation for testing interface"""

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
        tasks = [t for t in self.tasks.values() if t.assignee_user_id == user_id]
        if status:
            tasks = [t for t in tasks if t.status == status]
        return tasks

    async def list_due_today(self, user_id: str) -> list[Task]:
        today = datetime.now(UTC).date()
        return [
            t for t in self.tasks.values()
            if t.assignee_user_id == user_id
            and t.due_at is not None
            and t.due_at.date() == today
        ]

    async def list_overdue(self, user_id: str) -> list[Task]:
        return [
            t for t in self.tasks.values()
            if t.assignee_user_id == user_id and t.is_overdue()
        ]

    async def delete(self, task_id: UUID) -> None:
        if task_id in self.tasks:
            del self.tasks[task_id]


class FakeConversationRepository(ConversationRepository):
    """Fake implementation for testing interface"""

    def __init__(self):
        self.conversations: dict[UUID, Conversation] = {}

    async def save(self, conversation: Conversation) -> None:
        self.conversations[conversation.id] = conversation

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        return self.conversations.get(conversation_id)

    async def get_by_user_and_channel(
        self,
        user_id: str,
        channel_id: str
    ) -> Conversation | None:
        for conv in self.conversations.values():
            if conv.user_id == user_id and conv.channel_id == channel_id:
                return conv
        return None

    async def delete(self, conversation_id: UUID) -> None:
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]

    async def delete_expired(self) -> int:
        expired = [
            conv_id for conv_id, conv in self.conversations.items()
            if conv.is_expired()
        ]
        for conv_id in expired:
            del self.conversations[conv_id]
        return len(expired)


class TestTaskRepositoryInterface:
    """Test suite for TaskRepository interface"""

    @pytest.fixture
    def repository(self) -> FakeTaskRepository:
        return FakeTaskRepository()

    @pytest.mark.asyncio
    async def test_save_and_get_by_id(self, repository: FakeTaskRepository):
        """Test saving and retrieving a task"""
        task = Task.create("Test Task", "U123", "U123")

        await repository.save(task)
        retrieved = await repository.get_by_id(task.id)

        assert retrieved is not None
        assert retrieved.id == task.id
        assert retrieved.title == "Test Task"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository: FakeTaskRepository):
        """Test getting non-existent task returns None"""
        from uuid import uuid4
        result = await repository.get_by_id(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_list_by_user(self, repository: FakeTaskRepository):
        """Test listing tasks by user"""
        task1 = Task.create("Task 1", "U123", "U123")
        task2 = Task.create("Task 2", "U123", "U123")
        task3 = Task.create("Task 3", "U456", "U456")

        await repository.save(task1)
        await repository.save(task2)
        await repository.save(task3)

        user_tasks = await repository.list_by_user("U123")

        assert len(user_tasks) == 2
        assert all(t.assignee_user_id == "U123" for t in user_tasks)

    @pytest.mark.asyncio
    async def test_list_by_user_with_status_filter(self, repository: FakeTaskRepository):
        """Test listing tasks by user and status"""
        task1 = Task.create("Task 1", "U123", "U123")
        task2 = Task.create("Task 2", "U123", "U123")
        task2.complete()

        await repository.save(task1)
        await repository.save(task2)

        pending_tasks = await repository.list_by_user("U123", TaskStatus.PENDING)
        completed_tasks = await repository.list_by_user("U123", TaskStatus.COMPLETED)

        assert len(pending_tasks) == 1
        assert pending_tasks[0].status == TaskStatus.PENDING
        assert len(completed_tasks) == 1
        assert completed_tasks[0].status == TaskStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_delete(self, repository: FakeTaskRepository):
        """Test deleting a task"""
        task = Task.create("Test Task", "U123", "U123")
        await repository.save(task)

        await repository.delete(task.id)
        retrieved = await repository.get_by_id(task.id)

        assert retrieved is None


class TestConversationRepositoryInterface:
    """Test suite for ConversationRepository interface"""

    @pytest.fixture
    def repository(self) -> FakeConversationRepository:
        return FakeConversationRepository()

    @pytest.mark.asyncio
    async def test_save_and_get_by_id(self, repository: FakeConversationRepository):
        """Test saving and retrieving a conversation"""
        conv = Conversation.create("U123", "C456")

        await repository.save(conv)
        retrieved = await repository.get_by_id(conv.id)

        assert retrieved is not None
        assert retrieved.id == conv.id
        assert retrieved.user_id == "U123"

    @pytest.mark.asyncio
    async def test_get_by_user_and_channel(self, repository: FakeConversationRepository):
        """Test getting conversation by user and channel"""
        conv = Conversation.create("U123", "C456")
        await repository.save(conv)

        retrieved = await repository.get_by_user_and_channel("U123", "C456")

        assert retrieved is not None
        assert retrieved.id == conv.id

    @pytest.mark.asyncio
    async def test_get_by_user_and_channel_not_found(
        self,
        repository: FakeConversationRepository
    ):
        """Test getting non-existent conversation returns None"""
        result = await repository.get_by_user_and_channel("U999", "C999")

        assert result is None

    @pytest.mark.asyncio
    async def test_delete(self, repository: FakeConversationRepository):
        """Test deleting a conversation"""
        conv = Conversation.create("U123", "C456")
        await repository.save(conv)

        await repository.delete(conv.id)
        retrieved = await repository.get_by_id(conv.id)

        assert retrieved is None

    @pytest.mark.asyncio
    async def test_delete_expired(self, repository: FakeConversationRepository):
        """Test deleting expired conversations"""
        conv1 = Conversation.create("U123", "C456", ttl_hours=24)
        conv2 = Conversation.create("U789", "C012", ttl_hours=24)

        # Manually expire conv1
        conv1.expires_at = datetime.now(UTC)

        await repository.save(conv1)
        await repository.save(conv2)

        deleted_count = await repository.delete_expired()

        assert deleted_count == 1
        assert await repository.get_by_id(conv1.id) is None
        assert await repository.get_by_id(conv2.id) is not None
