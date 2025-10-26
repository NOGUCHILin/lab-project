"""
DependencyType Value Object Unit Tests

TDD: Red Phase - 先にテストを書く
"""

import pytest

from src.contexts.task_dependencies.domain.value_objects.dependency_type import (
    DependencyType,
)


class TestDependencyType:
    """DependencyType Value Object のテスト"""

    def test_blocks_type_exists(self):
        """BLOCKS タイプが存在する"""
        assert DependencyType.BLOCKS.value == "blocks"

    def test_depends_on_type_exists(self):
        """DEPENDS_ON タイプが存在する（将来拡張用）"""
        # 現在は BLOCKS のみだが、将来的に DEPENDS_ON を追加予定
        # assert DependencyType.DEPENDS_ON.value == "depends_on"
        pass

    def test_from_string_blocks(self):
        """文字列 'blocks' から DependencyType.BLOCKS に変換できる"""
        dep_type = DependencyType.from_string("blocks")
        assert dep_type == DependencyType.BLOCKS

    def test_from_string_invalid_raises_error(self):
        """無効な文字列でエラーが発生する"""
        with pytest.raises(ValueError, match="Invalid dependency type"):
            DependencyType.from_string("invalid")

    def test_equality(self):
        """同じタイプのインスタンスは等価"""
        type1 = DependencyType.BLOCKS
        type2 = DependencyType.BLOCKS
        assert type1 == type2

    def test_string_representation(self):
        """文字列表現が正しい"""
        assert str(DependencyType.BLOCKS) == "DependencyType.BLOCKS"
