"""SlackUser Repository Interface"""

from abc import ABC, abstractmethod

from src.domain.slack_user import SlackUser


class SlackUserRepository(ABC):
    """Repository interface for SlackUser persistence"""

    @abstractmethod
    async def save_all(self, users: list[SlackUser]) -> None:
        """Save or update multiple users (upsert)"""
        pass

    @abstractmethod
    async def find_all_active(self) -> list[SlackUser]:
        """Find all non-deleted users"""
        pass

    @abstractmethod
    async def find_by_id(self, user_id: str) -> SlackUser | None:
        """Find user by Slack user ID"""
        pass
