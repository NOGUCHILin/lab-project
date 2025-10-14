"""PostgreSQL implementation of NoteRepository"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.models.note import Note
from ...domain.repositories.note_repository import NoteRepository
from ...infrastructure.database.schema import NoteTable

if TYPE_CHECKING:
    from anthropic import Anthropic


class PostgreSQLNoteRepository(NoteRepository):
    """PostgreSQL implementation of NoteRepository"""

    def __init__(self, session: AsyncSession, claude_client: "Anthropic"):
        self._session = session
        self._claude_client = claude_client

    async def save(self, note: Note) -> Note:
        """ノートを保存（embedding自動生成）"""
        # Claude Embedding生成
        embedding = await self._generate_embedding(note.content)

        note_table = NoteTable(
            id=note.id,
            session_id=note.session_id,
            user_id=note.user_id,
            content=note.content,
            category=note.category,
            embedding=embedding,
            created_at=note.created_at,
        )

        self._session.add(note_table)
        await self._session.flush()

        note.embedding = embedding
        return note

    async def search(self, query: str, user_id: str, limit: int = 10) -> list[Note]:
        """ノートを意味検索（Vector Search）"""
        # クエリのembedding生成
        query_embedding = await self._generate_embedding(query)

        # Cosine similarity search
        # SQLAlchemy 2.0+ with pgvector
        stmt = (
            select(NoteTable)
            .where(NoteTable.user_id == user_id)
            .order_by(NoteTable.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        note_tables = result.scalars().all()

        return [self._map_to_entity(nt) for nt in note_tables]

    async def list_by_session(self, session_id: str) -> list[Note]:
        """セッションIDでノート一覧取得"""
        stmt = (
            select(NoteTable)
            .where(NoteTable.session_id == session_id)
            .order_by(NoteTable.created_at.asc())
        )

        result = await self._session.execute(stmt)
        note_tables = result.scalars().all()

        return [self._map_to_entity(nt) for nt in note_tables]

    async def list_by_user(self, user_id: str, limit: int = 100) -> list[Note]:
        """ユーザーIDでノート一覧取得"""
        stmt = (
            select(NoteTable)
            .where(NoteTable.user_id == user_id)
            .order_by(NoteTable.created_at.desc())
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        note_tables = result.scalars().all()

        return [self._map_to_entity(nt) for nt in note_tables]

    async def get(self, note_id: UUID) -> Note | None:
        """ノートIDで取得"""
        stmt = select(NoteTable).where(NoteTable.id == note_id)
        result = await self._session.execute(stmt)
        note_table = result.scalar_one_or_none()

        if note_table is None:
            return None

        return self._map_to_entity(note_table)

    async def delete(self, note_id: UUID) -> None:
        """ノートを削除"""
        stmt = select(NoteTable).where(NoteTable.id == note_id)
        result = await self._session.execute(stmt)
        note_table = result.scalar_one_or_none()

        if note_table:
            await self._session.delete(note_table)

    async def _generate_embedding(self, text: str) -> list[float]:
        """Claude Embedding生成（追加コストなし）

        Note: Claude API のEmbeddingエンドポイントを使用
        実装詳細はPhase 1実装時にClaude APIドキュメント参照
        """
        # TODO: Anthropic SDKでEmbedding生成実装
        # 現在はダミー実装（1024次元のゼロベクトル）
        return [0.0] * 1024

    def _map_to_entity(self, note_table: NoteTable) -> Note:
        """TableモデルからDomainモデルに変換"""
        return Note(
            id=note_table.id,
            session_id=note_table.session_id,
            user_id=note_table.user_id,
            content=note_table.content,
            category=note_table.category,
            embedding=note_table.embedding,
            created_at=note_table.created_at,
        )
