"""Slack User Sync Service - Syncs Slack API user data to database"""

import logging
from datetime import UTC, datetime

from src.adapters.secondary.slack_adapter import SlackAdapter
from src.domain.repositories.slack_user_repository import SlackUserRepository
from src.domain.slack_user import SlackUser

logger = logging.getLogger(__name__)


class SlackUserSyncService:
    """Service for synchronizing Slack user data to database cache"""

    def __init__(self, slack_adapter: SlackAdapter, slack_user_repository: SlackUserRepository):
        """Initialize sync service

        Args:
            slack_adapter: SlackAdapter for calling Slack API
            slack_user_repository: Repository for persisting user data
        """
        self.slack_adapter = slack_adapter
        self.slack_user_repository = slack_user_repository

    async def sync_users(self) -> dict[str, int | str]:
        """Sync users from Slack API to database

        Returns:
            Dictionary with sync result statistics
        """
        logger.info("Starting Slack user sync")

        # Fetch users from Slack API
        try:
            response = await self.slack_adapter.users_list()
        except Exception as e:
            logger.error(f"Failed to fetch users from Slack API: {e}", exc_info=True)
            return {"status": "error", "message": str(e), "synced_count": 0}

        if not response.get("ok"):
            error = response.get("error", "unknown")
            logger.error(f"Slack API error: {error}")
            return {"status": "error", "message": f"Slack API error: {error}", "synced_count": 0}

        members = response.get("members", [])
        logger.info(f"Fetched {len(members)} users from Slack API")

        # Convert to domain entities
        now = datetime.now(UTC)
        users = []

        for member in members:
            try:
                user = SlackUser(
                    user_id=member["id"],
                    name=member.get("name", ""),
                    real_name=member.get("real_name"),
                    display_name=member.get("profile", {}).get("display_name") or member.get("name", ""),
                    email=member.get("profile", {}).get("email"),
                    is_admin=member.get("is_admin", False),
                    is_bot=member.get("is_bot", False),
                    deleted=member.get("deleted", False),
                    slack_created_at=datetime.fromtimestamp(member.get("updated", 0), tz=UTC),
                    synced_at=now,
                    created_at=now,
                    updated_at=now,
                )
                users.append(user)
            except Exception as e:
                logger.warning(f"Failed to convert user {member.get('id', 'unknown')}: {e}")
                continue

        # Save to database
        try:
            await self.slack_user_repository.save_all(users)
            logger.info(f"Successfully synced {len(users)} users to database")
            return {"status": "success", "synced_count": len(users), "total_fetched": len(members)}
        except Exception as e:
            logger.error(f"Failed to save users to database: {e}", exc_info=True)
            return {"status": "error", "message": str(e), "synced_count": 0}
