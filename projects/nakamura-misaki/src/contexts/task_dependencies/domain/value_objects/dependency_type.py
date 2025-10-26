"""
DependencyType Value Object

タスク依存関係の種類を表すValue Object（Enum）
"""

from enum import Enum


class DependencyType(Enum):
    """タスク依存関係の種類

    Attributes:
        BLOCKS: タスクAがタスクBをブロックしている（Aが完了しないとBを開始できない）
    """

    BLOCKS = "blocks"

    @classmethod
    def from_string(cls, value: str) -> "DependencyType":
        """文字列からDependencyTypeに変換

        Args:
            value: 依存関係タイプの文字列（例: "blocks"）

        Returns:
            対応するDependencyTypeインスタンス

        Raises:
            ValueError: 無効な文字列の場合
        """
        try:
            return cls(value)
        except ValueError as e:
            raise ValueError(f"Invalid dependency type: {value}. Valid values: {[t.value for t in cls]}") from e

    def __str__(self) -> str:
        return f"DependencyType.{self.name}"
