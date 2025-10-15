"""FastAPI Dependency Injection

Provides database sessions and other dependencies for API routes.
"""

from typing import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """データベースセッションを取得

    FastAPIの依存性注入で使用されるデータベースセッション提供関数。

    Args:
        request: FastAPI Request（app.stateから設定を取得）

    Yields:
        AsyncSession: データベースセッション
    """
    async_session_maker = request.app.state.async_session_maker
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
