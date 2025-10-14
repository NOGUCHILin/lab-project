"""QueryHandoffsByUserUseCase - ユーザーのハンドオフ一覧取得"""

from src.application.dto.handoff_dto import HandoffDTO
from src.domain.repositories.handoff_repository import HandoffRepository


class QueryHandoffsByUserUseCase:
    """ユーザーのハンドオフ一覧取得ユースケース"""

    def __init__(self, handoff_repository: HandoffRepository):
        self._handoff_repository = handoff_repository

    async def execute(self, user_id: str) -> list[HandoffDTO]:
        """引き継ぎ先ユーザーのハンドオフ一覧を取得"""
        handoffs = await self._handoff_repository.list_by_to_user(user_id)

        return [HandoffDTO.from_entity(handoff) for handoff in handoffs]
