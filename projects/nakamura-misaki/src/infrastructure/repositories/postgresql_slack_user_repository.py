"""PostgreSQL SlackUser Repository implementation"""

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, String, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.domain.repositories.slack_user_repository import SlackUserRepository
from src.domain.slack_user import SlackUser


class Base(DeclarativeBase):
    """SQLAlchemy declarative base"""

    pass


class SlackUserModel(Base):
    """SQLAlchemy model for SlackUser"""

    __tablename__ = "slack_users"

    user_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    real_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    slack_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PostgreSQLSlackUserRepository(SlackUserRepository):
    """PostgreSQL implementation of SlackUserRepository"""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def save_all(self, users: list[SlackUser]) -> None:
        """Save or update multiple users (upsert)

        Args:
            users: List of SlackUser domain entities to save
        """
        if not users:
            return

        # Convert domain entities to dictionaries for bulk upsert
        user_dicts = [
            {
                "user_id": user.user_id,
                "name": user.name,
                "real_name": user.real_name,
                "display_name": user.display_name,
                "email": user.email,
                "is_admin": user.is_admin,
                "is_bot": user.is_bot,
                "deleted": user.deleted,
                "slack_created_at": user.slack_created_at,
                "synced_at": user.synced_at,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            }
            for user in users
        ]

        # PostgreSQL upsert using ON CONFLICT DO UPDATE
        stmt = insert(SlackUserModel).values(user_dicts)
        stmt = stmt.on_conflict_do_update(
            index_elements=["user_id"],
            set_={
                "name": stmt.excluded.name,
                "real_name": stmt.excluded.real_name,
                "display_name": stmt.excluded.display_name,
                "email": stmt.excluded.email,
                "is_admin": stmt.excluded.is_admin,
                "is_bot": stmt.excluded.is_bot,
                "deleted": stmt.excluded.deleted,
                "slack_created_at": stmt.excluded.slack_created_at,
                "synced_at": stmt.excluded.synced_at,
                "updated_at": stmt.excluded.updated_at,
            },
        )

        await self.session.execute(stmt)

    async def find_all_active(self) -> list[SlackUser]:
        """Find all non-deleted users

        Returns:
            List of active SlackUser domain entities
        """
        stmt = select(SlackUserModel).where(SlackUserModel.deleted == False).order_by(SlackUserModel.name)  # noqa: E712

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    async def find_by_id(self, user_id: str) -> SlackUser | None:
        """Find user by Slack user ID

        Args:
            user_id: Slack user ID

        Returns:
            SlackUser domain entity or None if not found
        """
        stmt = select(SlackUserModel).where(SlackUserModel.user_id == user_id)

        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    def _to_domain(self, model: SlackUserModel) -> SlackUser:
        """Convert database model to domain entity

        Args:
            model: SQLAlchemy SlackUserModel

        Returns:
            SlackUser domain entity
        """
        return SlackUser(
            user_id=model.user_id,
            name=model.name,
            real_name=model.real_name,
            display_name=model.display_name,
            email=model.email,
            is_admin=model.is_admin,
            is_bot=model.is_bot,
            deleted=model.deleted,
            slack_created_at=model.slack_created_at,
            synced_at=model.synced_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
