"""Handoff management tools for Claude Tool Use."""

from typing import Any
from uuid import UUID

from ....application.dto.handoff_dto import HandoffDTO
from ....application.use_cases.complete_handoff import CompleteHandoffUseCase
from ....application.use_cases.query_handoffs_by_user import QueryHandoffsByUserUseCase
from ....application.use_cases.register_handoff import RegisterHandoffUseCase
from .base_tool import BaseTool


class RegisterHandoffTool(BaseTool):
    """ハンドオフ登録Tool.

    タスクを別のユーザーに引き継ぐ。
    """

    def __init__(self, register_handoff_use_case: RegisterHandoffUseCase, user_id: str):
        """Initialize RegisterHandoffTool.

        Args:
            register_handoff_use_case: RegisterHandoffUseCase instance
            user_id: Current user's Slack user ID
        """
        self._register_handoff_use_case = register_handoff_use_case
        self._user_id = user_id

    @property
    def name(self) -> str:
        return "register_handoff"

    @property
    def description(self) -> str:
        return "タスクを別のユーザーに引き継ぐ（ハンドオフ）"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "引き継ぐタスクのID（UUID）",
                },
                "to_user_id": {
                    "type": "string",
                    "description": "引き継ぎ先のユーザーID（Slack User ID）",
                },
                "note": {
                    "type": "string",
                    "description": "引き継ぎメモ・説明（任意）",
                },
            },
            "required": ["task_id", "to_user_id"],
        }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """ハンドオフ登録を実行.

        Args:
            task_id: タスクID（UUID）
            to_user_id: 引き継ぎ先ユーザーID
            note: 引き継ぎメモ（任意）

        Returns:
            dict: {"success": True, "data": {...}} or {"success": False, "error": "..."}
        """
        try:
            task_id_str = kwargs["task_id"]
            to_user_id = kwargs["to_user_id"]
            note = kwargs.get("note", "")

            # Parse UUID
            try:
                task_id = UUID(task_id_str)
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid task ID format: {task_id_str}",
                }

            # Execute use case
            handoff = await self._register_handoff_use_case.execute(
                task_id=task_id,
                from_user_id=self._user_id,
                to_user_id=to_user_id,
                note=note,
            )

            return {
                "success": True,
                "data": self._handoff_dto_to_dict(handoff),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _handoff_dto_to_dict(self, handoff_dto: HandoffDTO) -> dict[str, Any]:
        """Convert HandoffDTO to dict.

        Args:
            handoff_dto: HandoffDTO

        Returns:
            dict: JSON-serializable handoff data
        """
        return {
            "id": str(handoff_dto.id),
            "task_id": str(handoff_dto.task_id),
            "from_user_id": handoff_dto.from_user_id,
            "to_user_id": handoff_dto.to_user_id,
            "note": handoff_dto.note,
            "status": handoff_dto.status,
            "created_at": handoff_dto.created_at.isoformat(),
        }


class ListHandoffsTool(BaseTool):
    """ハンドオフ一覧取得Tool.

    ユーザーに関連するハンドオフ一覧を取得する。
    """

    def __init__(self, query_handoffs_use_case: QueryHandoffsByUserUseCase, user_id: str):
        """Initialize ListHandoffsTool.

        Args:
            query_handoffs_use_case: QueryHandoffsByUserUseCase instance
            user_id: Current user's Slack user ID
        """
        self._query_handoffs_use_case = query_handoffs_use_case
        self._user_id = user_id

    @property
    def name(self) -> str:
        return "list_handoffs"

    @property
    def description(self) -> str:
        return "ハンドオフ一覧を取得する（自分が送ったor受け取った引き継ぎ）"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["pending", "completed"],
                    "description": "フィルタするステータス（任意）",
                },
            },
        }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """ハンドオフ一覧を取得.

        Args:
            status: ステータスフィルタ（任意）

        Returns:
            dict: {"success": True, "data": {"handoffs": [...], "count": N}}
        """
        try:
            status = kwargs.get("status")

            handoffs = await self._query_handoffs_use_case.execute(
                user_id=self._user_id,
                status=status,
            )

            return {
                "success": True,
                "data": {
                    "handoffs": [self._handoff_dto_to_dict(h) for h in handoffs],
                    "count": len(handoffs),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _handoff_dto_to_dict(self, handoff_dto: HandoffDTO) -> dict[str, Any]:
        """Convert HandoffDTO to dict.

        Args:
            handoff_dto: HandoffDTO

        Returns:
            dict: JSON-serializable handoff data
        """
        return {
            "id": str(handoff_dto.id),
            "task_id": str(handoff_dto.task_id),
            "from_user_id": handoff_dto.from_user_id,
            "to_user_id": handoff_dto.to_user_id,
            "note": handoff_dto.note,
            "status": handoff_dto.status,
            "created_at": handoff_dto.created_at.isoformat(),
        }


class CompleteHandoffTool(BaseTool):
    """ハンドオフ完了Tool.

    受け取ったハンドオフを完了済みにする。
    """

    def __init__(self, complete_handoff_use_case: CompleteHandoffUseCase, user_id: str):
        """Initialize CompleteHandoffTool.

        Args:
            complete_handoff_use_case: CompleteHandoffUseCase instance
            user_id: Current user's Slack user ID
        """
        self._complete_handoff_use_case = complete_handoff_use_case
        self._user_id = user_id

    @property
    def name(self) -> str:
        return "complete_handoff"

    @property
    def description(self) -> str:
        return "ハンドオフを完了済みにする"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "handoff_id": {
                    "type": "string",
                    "description": "ハンドオフID（UUID）",
                },
            },
            "required": ["handoff_id"],
        }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """ハンドオフ完了を実行.

        Args:
            handoff_id: ハンドオフID（UUID）

        Returns:
            dict: {"success": True, "data": {...}} or {"success": False, "error": "..."}
        """
        try:
            handoff_id_str = kwargs["handoff_id"]

            # Parse UUID
            try:
                handoff_id = UUID(handoff_id_str)
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid handoff ID format: {handoff_id_str}",
                }

            # Execute use case
            handoff = await self._complete_handoff_use_case.execute(
                handoff_id=handoff_id
            )

            return {
                "success": True,
                "data": self._handoff_dto_to_dict(handoff),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _handoff_dto_to_dict(self, handoff_dto: HandoffDTO) -> dict[str, Any]:
        """Convert HandoffDTO to dict.

        Args:
            handoff_dto: HandoffDTO

        Returns:
            dict: JSON-serializable handoff data
        """
        return {
            "id": str(handoff_dto.id),
            "task_id": str(handoff_dto.task_id),
            "from_user_id": handoff_dto.from_user_id,
            "to_user_id": handoff_dto.to_user_id,
            "note": handoff_dto.note,
            "status": handoff_dto.status,
            "created_at": handoff_dto.created_at.isoformat(),
        }
