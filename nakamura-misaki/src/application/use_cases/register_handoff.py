"""RegisterHandoffUseCase - ハンドオフ登録"""

from datetime import datetime

from src.application.dto.handoff_dto import CreateHandoffDTO, HandoffDTO
from src.domain.models.handoff import Handoff
from src.domain.repositories.handoff_repository import HandoffRepository


class RegisterHandoffUseCase:
    """ハンドオフ登録ユースケース"""

    def __init__(self, handoff_repository: HandoffRepository):
        self._handoff_repository = handoff_repository

    async def execute(self, dto: CreateHandoffDTO) -> HandoffDTO:
        """ハンドオフを登録"""
        if dto.handoff_at < datetime.now():
            raise ValueError("Handoff time must be in the future")

        if not dto.progress_note:
            raise ValueError("Progress note cannot be empty")

        handoff = Handoff(
            task_id=dto.task_id,
            from_user_id=dto.from_user_id,
            to_user_id=dto.to_user_id,
            progress_note=dto.progress_note,
            handoff_at=dto.handoff_at,
        )

        created_handoff = await self._handoff_repository.create(handoff)

        return HandoffDTO.from_entity(created_handoff)
