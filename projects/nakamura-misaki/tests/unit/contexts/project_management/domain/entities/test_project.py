"""Project Entity Unit Tests

Tests for src/contexts/project_management/domain/entities/project.py

Following TDD Strategy (AAA Pattern):
- Arrange: Setup test data
- Act: Execute method under test
- Assert: Verify results
"""

from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest

from src.contexts.project_management.domain.entities.project import Project
from src.contexts.project_management.domain.value_objects.project_status import ProjectStatus


class TestProjectCreate:
    """Project.create() factory method tests"""

    def test_create_project_with_minimum_required_fields(self):
        """プロジェクト作成 - 必須フィールドのみ"""
        # Arrange
        name = "新規プロジェクト"
        owner_user_id = "U123456"

        # Act
        project = Project.create(name=name, owner_user_id=owner_user_id)

        # Assert
        assert isinstance(project.project_id, UUID)
        assert project.name == name
        assert project.owner_user_id == owner_user_id
        assert project.status == ProjectStatus.ACTIVE
        assert project.description is None
        assert project.deadline is None
        assert len(project.task_ids) == 0
        assert isinstance(project.created_at, datetime)
        assert isinstance(project.updated_at, datetime)

    def test_create_project_with_all_fields(self):
        """プロジェクト作成 - 全フィールド指定"""
        # Arrange
        name = "完全指定プロジェクト"
        owner_user_id = "U123456"
        description = "詳細説明"
        deadline = datetime.now() + timedelta(days=30)

        # Act
        project = Project.create(
            name=name,
            owner_user_id=owner_user_id,
            description=description,
            deadline=deadline,
        )

        # Assert
        assert project.name == name
        assert project.owner_user_id == owner_user_id
        assert project.description == description
        assert project.deadline == deadline

    def test_create_project_with_empty_name_raises_error(self):
        """空のプロジェクト名でエラー"""
        # Arrange
        name = ""
        owner_user_id = "U123456"

        # Act & Assert
        with pytest.raises(ValueError, match="name cannot be empty"):
            Project.create(name=name, owner_user_id=owner_user_id)

    def test_create_project_with_whitespace_only_name_raises_error(self):
        """空白のみのプロジェクト名でエラー"""
        # Arrange
        name = "   "
        owner_user_id = "U123456"

        # Act & Assert
        with pytest.raises(ValueError, match="name cannot be empty"):
            Project.create(name=name, owner_user_id=owner_user_id)

    def test_create_project_with_empty_owner_raises_error(self):
        """空のオーナーIDでエラー"""
        # Arrange
        name = "テストプロジェクト"
        owner_user_id = ""

        # Act & Assert
        with pytest.raises(ValueError, match="owner_user_id cannot be empty"):
            Project.create(name=name, owner_user_id=owner_user_id)


class TestProjectAddTask:
    """Project.add_task() tests"""

    def test_add_task_to_empty_project(self):
        """空のプロジェクトにタスク追加"""
        # Arrange
        project = Project.create(name="Test", owner_user_id="U123")
        task_id = uuid4()

        # Act
        project.add_task(task_id)

        # Assert
        assert task_id in project.task_ids
        assert len(project.task_ids) == 1

    def test_add_multiple_tasks_maintains_order(self):
        """複数タスク追加で順序維持"""
        # Arrange
        project = Project.create(name="Test", owner_user_id="U123")
        task_id_1 = uuid4()
        task_id_2 = uuid4()
        task_id_3 = uuid4()

        # Act
        project.add_task(task_id_1)
        project.add_task(task_id_2)
        project.add_task(task_id_3)

        # Assert
        assert project.task_ids == [task_id_1, task_id_2, task_id_3]

    def test_add_duplicate_task_raises_error(self):
        """重複タスク追加でエラー"""
        # Arrange
        project = Project.create(name="Test", owner_user_id="U123")
        task_id = uuid4()
        project.add_task(task_id)

        # Act & Assert
        with pytest.raises(ValueError, match="is already in the project"):
            project.add_task(task_id)


class TestProjectRemoveTask:
    """Project.remove_task() tests"""

    def test_remove_task_from_project(self):
        """プロジェクトからタスク削除"""
        # Arrange
        project = Project.create(name="Test", owner_user_id="U123")
        task_id = uuid4()
        project.add_task(task_id)

        # Act
        project.remove_task(task_id)

        # Assert
        assert task_id not in project.task_ids
        assert len(project.task_ids) == 0

    def test_remove_task_from_multiple_tasks(self):
        """複数タスクから特定タスク削除"""
        # Arrange
        project = Project.create(name="Test", owner_user_id="U123")
        task_id_1 = uuid4()
        task_id_2 = uuid4()
        task_id_3 = uuid4()
        project.add_task(task_id_1)
        project.add_task(task_id_2)
        project.add_task(task_id_3)

        # Act
        project.remove_task(task_id_2)

        # Assert
        assert task_id_2 not in project.task_ids
        assert project.task_ids == [task_id_1, task_id_3]

    def test_remove_nonexistent_task_raises_error(self):
        """存在しないタスク削除でエラー"""
        # Arrange
        project = Project.create(name="Test", owner_user_id="U123")
        nonexistent_task_id = uuid4()

        # Act & Assert
        with pytest.raises(ValueError, match="is not in the project"):
            project.remove_task(nonexistent_task_id)


class TestProjectComplete:
    """Project.complete() tests"""

    def test_complete_active_project(self):
        """アクティブプロジェクトを完了"""
        # Arrange
        project = Project.create(name="Test", owner_user_id="U123")
        assert project.status == ProjectStatus.ACTIVE

        # Act
        project.complete()

        # Assert
        assert project.status == ProjectStatus.COMPLETED

    def test_complete_already_completed_project_is_idempotent(self):
        """既に完了済みプロジェクトの完了は冪等"""
        # Arrange
        project = Project.create(name="Test", owner_user_id="U123")
        project.complete()

        # Act (should not raise error)
        project.complete()

        # Assert
        assert project.status == ProjectStatus.COMPLETED


class TestProjectArchive:
    """Project.archive() tests"""

    def test_archive_active_project(self):
        """アクティブプロジェクトをアーカイブ"""
        # Arrange
        project = Project.create(name="Test", owner_user_id="U123")

        # Act
        project.archive()

        # Assert
        assert project.status == ProjectStatus.ARCHIVED

    def test_archive_completed_project(self):
        """完了済みプロジェクトをアーカイブ"""
        # Arrange
        project = Project.create(name="Test", owner_user_id="U123")
        project.complete()

        # Act
        project.archive()

        # Assert
        assert project.status == ProjectStatus.ARCHIVED

    def test_archive_already_archived_project_is_idempotent(self):
        """既にアーカイブ済みプロジェクトのアーカイブは冪等"""
        # Arrange
        project = Project.create(name="Test", owner_user_id="U123")
        project.archive()

        # Act
        project.archive()

        # Assert
        assert project.status == ProjectStatus.ARCHIVED


class TestProjectUpdateDetails:
    """Project.update_details() tests"""

    def test_update_project_name(self):
        """プロジェクト名を更新"""
        # Arrange
        project = Project.create(name="Old Name", owner_user_id="U123")
        new_name = "New Name"

        # Act
        project.update_details(name=new_name)

        # Assert
        assert project.name == new_name

    def test_update_project_description(self):
        """プロジェクト説明を更新"""
        # Arrange
        project = Project.create(name="Test", owner_user_id="U123")
        new_description = "新しい説明"

        # Act
        project.update_details(description=new_description)

        # Assert
        assert project.description == new_description

    def test_update_project_deadline(self):
        """プロジェクト期限を更新"""
        # Arrange
        project = Project.create(name="Test", owner_user_id="U123")
        new_deadline = datetime.now() + timedelta(days=60)

        # Act
        project.update_details(deadline=new_deadline)

        # Assert
        assert project.deadline == new_deadline

    def test_update_multiple_fields(self):
        """複数フィールドを同時更新"""
        # Arrange
        project = Project.create(name="Test", owner_user_id="U123")
        new_name = "Updated Name"
        new_description = "Updated Description"
        new_deadline = datetime.now() + timedelta(days=90)

        # Act
        project.update_details(
            name=new_name,
            description=new_description,
            deadline=new_deadline,
        )

        # Assert
        assert project.name == new_name
        assert project.description == new_description
        assert project.deadline == new_deadline

    def test_update_with_empty_name_raises_error(self):
        """空のプロジェクト名への更新でエラー"""
        # Arrange
        project = Project.create(name="Test", owner_user_id="U123")

        # Act & Assert
        with pytest.raises(ValueError, match="name cannot be empty"):
            project.update_details(name="")

    def test_update_without_changes_succeeds(self):
        """変更なしの更新は成功"""
        # Arrange
        project = Project.create(name="Test", owner_user_id="U123")
        original_name = project.name

        # Act
        project.update_details()

        # Assert
        assert project.name == original_name
