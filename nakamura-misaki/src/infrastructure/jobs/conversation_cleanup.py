"""Conversation TTL cleanup job

Periodically removes expired conversations based on TTL.
"""

import asyncio
import logging

from ...contexts.personal_tasks.domain.repositories.conversation_repository import ConversationRepository

logger = logging.getLogger(__name__)


class ConversationCleanupJob:
    """Background job to clean up expired conversations"""

    def __init__(
        self,
        conversation_repository: ConversationRepository,
        ttl_hours: int = 24,
        cleanup_interval_minutes: int = 60,
    ):
        """Initialize cleanup job

        Args:
            conversation_repository: Conversation repository
            ttl_hours: Time-to-live in hours
            cleanup_interval_minutes: How often to run cleanup
        """
        self._repository = conversation_repository
        self._ttl_hours = ttl_hours
        self._cleanup_interval = cleanup_interval_minutes * 60  # Convert to seconds
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        """Start the cleanup job"""
        if self._running:
            logger.warning("Cleanup job already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._run())
        logger.info(
            f"Conversation cleanup job started (TTL: {self._ttl_hours}h, interval: {self._cleanup_interval}s)"
        )

    async def stop(self) -> None:
        """Stop the cleanup job"""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Conversation cleanup job stopped")

    async def _run(self) -> None:
        """Main cleanup loop"""
        while self._running:
            try:
                await self._cleanup_expired_conversations()
                await asyncio.sleep(self._cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup job: {e}", exc_info=True)
                # Continue running even if cleanup fails
                await asyncio.sleep(self._cleanup_interval)

    async def _cleanup_expired_conversations(self) -> None:
        """Remove expired conversations"""
        try:
            deleted_count = await self._repository.delete_expired(self._ttl_hours)
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired conversations (TTL: {self._ttl_hours}h)")
        except Exception as e:
            logger.error(f"Failed to clean up conversations: {e}", exc_info=True)
            raise
