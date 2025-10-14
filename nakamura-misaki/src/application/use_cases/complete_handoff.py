"""CompleteHandoffUseCase - ハンドオフ完了"""

from uuid import UUID

from src.application.dto.handoff_dto import HandoffDTO
from src.domain.repositories.handoff_repository import HandoffRepository


class CompleteHandoffUseCase:
    """ハンドオフ完了ユースケース"""

    def __init__(self, handoff_repository: HandoffRepository):
        self._handoff_repository = handoff_repository

    async def execute(self, handoff_id: UUID) -> HandoffDTO:
        """ハンドオフを完了"""
        handoff = await self._handoff_repository.get(handoff_id)

        if handoff is None:
            raise ValueError(f"Handoff not found: {handoff_id}")

        if not handoff.is_pending():
            raise ValueError(f"Handoff is already completed: {handoff_id}")

        completed_handoff = await self._handoff_repository.complete(handoff_id)

        return HandoffDTO.from_entity(completed_handoff)
