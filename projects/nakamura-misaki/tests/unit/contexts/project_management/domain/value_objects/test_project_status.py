"""ProjectStatus Value Object Unit Tests

Tests for src/contexts/project_management/domain/value_objects/project_status.py
"""

from src.contexts.project_management.domain.value_objects.project_status import ProjectStatus


class TestProjectStatus:
    """ProjectStatus enum tests"""

    def test_project_status_values(self):
        """ProjectStatusの値確認"""
        # Assert
        assert ProjectStatus.ACTIVE.value == "active"
        assert ProjectStatus.COMPLETED.value == "completed"
        assert ProjectStatus.ARCHIVED.value == "archived"

    def test_project_status_string_conversion(self):
        """ProjectStatusの文字列変換"""
        # Assert
        assert str(ProjectStatus.ACTIVE) == "active"
        assert str(ProjectStatus.COMPLETED) == "completed"
        assert str(ProjectStatus.ARCHIVED) == "archived"

    def test_project_status_from_string(self):
        """文字列からProjectStatus作成"""
        # Act
        status = ProjectStatus("active")

        # Assert
        assert status == ProjectStatus.ACTIVE
