"""TaskDependency Entity Unit Tests

Tests for src/contexts/task_dependencies/domain/entities/task_dependency.py

Following TDD Strategy (AAA Pattern):
- Arrange: Setup test data
- Act: Execute method under test
- Assert: Verify results
"""

from datetime import datetime
from uuid import UUID, uuid4

import pytest

from src.contexts.task_dependencies.domain.entities.task_dependency import TaskDependency
from src.contexts.task_dependencies.domain.value_objects.dependency_type import (
    DependencyType,
)


class TestTaskDependencyCreate:
    """TaskDependency.create() factory method tests"""

    def test_create_dependency_with_valid_task_ids(self):
        """依存関係作成 - 有効なタスクID"""
        # Arrange
        blocking_task_id = uuid4()
        blocked_task_id = uuid4()

        # Act
        dependency = TaskDependency.create(blocking_task_id=blocking_task_id, blocked_task_id=blocked_task_id)

        # Assert
        assert isinstance(dependency.id, UUID)
        assert dependency.blocking_task_id == blocking_task_id
        assert dependency.blocked_task_id == blocked_task_id
        assert dependency.dependency_type == DependencyType.BLOCKS
        assert isinstance(dependency.created_at, datetime)

    def test_create_dependency_with_same_task_ids_raises_error(self):
        """自己依存でエラー（blocking_task_id == blocked_task_id）"""
        # Arrange
        task_id = uuid4()

        # Act & Assert
        with pytest.raises(ValueError, match="Task cannot depend on itself"):
            TaskDependency.create(blocking_task_id=task_id, blocked_task_id=task_id)

    def test_create_dependency_with_explicit_type(self):
        """依存関係タイプを明示的に指定"""
        # Arrange
        blocking_task_id = uuid4()
        blocked_task_id = uuid4()

        # Act
        dependency = TaskDependency.create(
            blocking_task_id=blocking_task_id,
            blocked_task_id=blocked_task_id,
            dependency_type=DependencyType.BLOCKS,
        )

        # Assert
        assert dependency.dependency_type == DependencyType.BLOCKS


class TestTaskDependencyReconstruct:
    """TaskDependency.reconstruct() tests (for Repository)"""

    def test_reconstruct_from_db(self):
        """DBから復元"""
        # Arrange
        dependency_id = uuid4()
        blocking_task_id = uuid4()
        blocked_task_id = uuid4()
        created_at = datetime(2025, 10, 26, 12, 0, 0)

        # Act
        dependency = TaskDependency.reconstruct(
            id=dependency_id,
            blocking_task_id=blocking_task_id,
            blocked_task_id=blocked_task_id,
            dependency_type=DependencyType.BLOCKS,
            created_at=created_at,
        )

        # Assert
        assert dependency.id == dependency_id
        assert dependency.blocking_task_id == blocking_task_id
        assert dependency.blocked_task_id == blocked_task_id
        assert dependency.dependency_type == DependencyType.BLOCKS
        assert dependency.created_at == created_at


class TestTaskDependencyEquality:
    """TaskDependency equality tests"""

    def test_dependencies_with_same_id_are_equal(self):
        """同じIDの依存関係は等価"""
        # Arrange
        dependency_id = uuid4()
        blocking_task_id = uuid4()
        blocked_task_id = uuid4()

        # Act
        dep1 = TaskDependency.reconstruct(
            id=dependency_id,
            blocking_task_id=blocking_task_id,
            blocked_task_id=blocked_task_id,
            dependency_type=DependencyType.BLOCKS,
            created_at=datetime.now(),
        )
        dep2 = TaskDependency.reconstruct(
            id=dependency_id,
            blocking_task_id=blocking_task_id,
            blocked_task_id=blocked_task_id,
            dependency_type=DependencyType.BLOCKS,
            created_at=datetime.now(),
        )

        # Assert
        assert dep1 == dep2
        assert hash(dep1) == hash(dep2)

    def test_dependencies_with_different_ids_are_not_equal(self):
        """異なるIDの依存関係は非等価"""
        # Arrange
        blocking_task_id = uuid4()
        blocked_task_id = uuid4()

        # Act
        dep1 = TaskDependency.create(blocking_task_id=blocking_task_id, blocked_task_id=blocked_task_id)
        dep2 = TaskDependency.create(blocking_task_id=blocking_task_id, blocked_task_id=blocked_task_id)

        # Assert
        assert dep1 != dep2


class TestTaskDependencyStringRepresentation:
    """TaskDependency string representation tests"""

    def test_str_representation(self):
        """文字列表現が正しい"""
        # Arrange
        blocking_task_id = uuid4()
        blocked_task_id = uuid4()

        # Act
        dependency = TaskDependency.create(blocking_task_id=blocking_task_id, blocked_task_id=blocked_task_id)

        # Assert
        str_repr = str(dependency)
        assert str(blocking_task_id)[:8] in str_repr
        assert str(blocked_task_id)[:8] in str_repr
        assert "blocks" in str_repr


class TestTaskDependencyImmutability:
    """TaskDependency immutability tests"""

    def test_dependency_is_immutable(self):
        """依存関係はImmutable（変更不可）"""
        # Arrange
        dependency = TaskDependency.create(blocking_task_id=uuid4(), blocked_task_id=uuid4())

        # Act & Assert - 属性変更しようとするとエラー
        with pytest.raises(AttributeError):
            dependency.blocking_task_id = uuid4()  # type: ignore

        with pytest.raises(AttributeError):
            dependency.blocked_task_id = uuid4()  # type: ignore
