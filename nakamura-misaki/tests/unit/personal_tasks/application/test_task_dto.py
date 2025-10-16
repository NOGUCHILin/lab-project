"""Unit tests for Task DTOs"""

from datetime import UTC, datetime, timedelta

from src.contexts.personal_tasks.application.dto.task_dto import CreateTaskDTO, TaskDTO, UpdateTaskDTO
from src.contexts.personal_tasks.domain.models.task import Task
from src.shared_kernel.domain.value_objects.task_status import TaskStatus


class TestCreateTaskDTO:
    """Test suite for CreateTaskDTO"""

    def test_create_dto_with_minimum_fields(self):
        """Test creating DTO with only required fields"""
        dto = CreateTaskDTO(
            title="Complete Phase 1",
            assignee_user_id="U12345",
            creator_user_id="U12345"
        )

        assert dto.title == "Complete Phase 1"
        assert dto.assignee_user_id == "U12345"
        assert dto.creator_user_id == "U12345"
        assert dto.description is None
        assert dto.due_at is None

    def test_create_dto_with_all_fields(self):
        """Test creating DTO with all optional fields"""
        due_date = datetime.now(UTC) + timedelta(days=1)
        dto = CreateTaskDTO(
            title="Complete Phase 1",
            assignee_user_id="U12345",
            creator_user_id="U67890",
            description="Implement Bounded Context",
            due_at=due_date
        )

        assert dto.title == "Complete Phase 1"
        assert dto.description == "Implement Bounded Context"
        assert dto.creator_user_id == "U67890"
        assert dto.due_at == due_date


class TestTaskDTO:
    """Test suite for TaskDTO"""

    def test_create_dto_from_domain_model(self):
        """Test creating DTO from Task domain model"""
        task = Task.create(
            title="Test Task",
            assignee_user_id="U12345",
            creator_user_id="U67890",
            description="Test description"
        )

        dto = TaskDTO.from_domain(task)

        assert dto.id == task.id
        assert dto.title == "Test Task"
        assert dto.description == "Test description"
        assert dto.assignee_user_id == "U12345"
        assert dto.creator_user_id == "U67890"
        assert dto.status == "pending"
        assert dto.due_at is None
        assert dto.completed_at is None
        assert dto.created_at == task.created_at
        assert dto.updated_at == task.updated_at

    def test_dto_with_completed_task(self):
        """Test DTO for completed task"""
        task = Task.create("Test Task", "U12345", "U12345")
        task.complete()

        dto = TaskDTO.from_domain(task)

        assert dto.status == "completed"
        assert dto.completed_at is not None

    def test_dto_with_due_date(self):
        """Test DTO for task with due date"""
        due_date = datetime.now(UTC) + timedelta(days=1)
        task = Task.create("Test Task", "U12345", "U12345", due_at=due_date)

        dto = TaskDTO.from_domain(task)

        assert dto.due_at == due_date

    def test_dto_list_from_domain_list(self):
        """Test creating DTO list from domain model list"""
        tasks = [
            Task.create("Task 1", "U123", "U123"),
            Task.create("Task 2", "U123", "U123"),
            Task.create("Task 3", "U123", "U123")
        ]

        dtos = [TaskDTO.from_domain(t) for t in tasks]

        assert len(dtos) == 3
        assert dtos[0].title == "Task 1"
        assert dtos[1].title == "Task 2"
        assert dtos[2].title == "Task 3"


class TestUpdateTaskDTO:
    """Test suite for UpdateTaskDTO"""

    def test_update_dto_with_title_only(self):
        """Test update DTO with only title"""
        dto = UpdateTaskDTO(title="Updated Title")

        assert dto.title == "Updated Title"
        assert dto.description is None
        assert dto.status is None
        assert dto.due_at is None

    def test_update_dto_with_all_fields(self):
        """Test update DTO with all fields"""
        due_date = datetime.now(UTC) + timedelta(days=2)
        dto = UpdateTaskDTO(
            title="Updated Title",
            description="Updated description",
            status=TaskStatus.IN_PROGRESS,
            due_at=due_date
        )

        assert dto.title == "Updated Title"
        assert dto.description == "Updated description"
        assert dto.status == TaskStatus.IN_PROGRESS
        assert dto.due_at == due_date

    def test_update_dto_allows_none_values(self):
        """Test that UpdateTaskDTO allows None for optional updates"""
        dto = UpdateTaskDTO()

        assert dto.title is None
        assert dto.description is None
        assert dto.status is None
        assert dto.due_at is None

    def test_update_dto_with_status_change(self):
        """Test update DTO for status change"""
        dto = UpdateTaskDTO(status=TaskStatus.COMPLETED)

        assert dto.status == TaskStatus.COMPLETED
        assert dto.title is None  # Other fields unchanged
