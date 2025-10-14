# Phase 1: Database - Design

## System Architecture

### Current (Phase 0)

```
SlackEvent → ClaudeAdapter → JsonNoteRepository → File (data/notes/*.json)
                           → JsonSessionRepository → File (data/sessions/*.json)
```

### Target (Phase 1)

```
SlackEvent → ClaudeAdapter → PostgreSQLNoteRepository → PostgreSQL (notes table)
                           → PostgreSQLSessionRepository → PostgreSQL (sessions table)
                           → PostgreSQLTaskRepository → PostgreSQL (tasks table)
                           → PostgreSQLHandoffRepository → PostgreSQL (handoffs table)
```

## Database Design

### Entity Relationship Diagram

```mermaid
erDiagram
    tasks ||--o{ handoffs : "has"
    tasks {
        uuid id PK
        text title
        text description
        text assignee_user_id
        text creator_user_id
        text status
        timestamp due_at
        timestamp completed_at
        timestamp created_at
        timestamp updated_at
    }
    handoffs {
        uuid id PK
        uuid task_id FK
        text from_user_id
        text to_user_id
        text progress_note
        text next_steps
        timestamp handoff_at
        timestamp reminded_at
        timestamp created_at
    }
    notes {
        uuid id PK
        text session_id
        text user_id
        text content
        vector embedding
        timestamp created_at
    }
    sessions {
        text id PK
        text user_id
        text workspace_path
        timestamp last_active_at
        timestamp created_at
    }
```

### Schema Details

#### tasks table

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,
    assignee_user_id TEXT NOT NULL,  -- Slack User ID (例: U01ABC123)
    creator_user_id TEXT NOT NULL,   -- 作成者のSlack User ID
    status TEXT NOT NULL DEFAULT 'pending',  -- pending, in_progress, completed, cancelled
    due_at TIMESTAMP,                -- 期限（NULL可: 期限なしタスク）
    completed_at TIMESTAMP,          -- 完了日時
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_status CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled'))
);

CREATE INDEX idx_tasks_assignee ON tasks(assignee_user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_at ON tasks(due_at) WHERE due_at IS NOT NULL;  -- Partial index
CREATE INDEX idx_tasks_updated_at ON tasks(updated_at);
```

**Status Transitions**:
- `pending` → `in_progress` (作業開始)
- `in_progress` → `completed` (完了)
- `in_progress` → `pending` (作業中断)
- Any → `cancelled` (キャンセル)

#### handoffs table

```sql
CREATE TABLE handoffs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,  -- NULL可（タスク以外の引き継ぎ）
    from_user_id TEXT NOT NULL,      -- 引き継ぎ元
    to_user_id TEXT NOT NULL,        -- 引き継ぎ先
    progress_note TEXT,              -- 現在の進捗状況
    next_steps TEXT,                 -- 次のステップ・注意点
    handoff_at TIMESTAMP NOT NULL,   -- 引き継ぎ予定日時
    reminded_at TIMESTAMP,           -- リマインダー送信済み日時
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_handoffs_to_user ON handoffs(to_user_id);
CREATE INDEX idx_handoffs_handoff_at ON handoffs(handoff_at);
CREATE INDEX idx_handoffs_reminded ON handoffs(reminded_at) WHERE reminded_at IS NULL;  -- 未送信のみ
```

#### notes table (Anthropic Structured Note-Taking)

```sql
CREATE EXTENSION IF NOT EXISTS vector;  -- pgvector

CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL,        -- Claude Code Session ID
    user_id TEXT NOT NULL,           -- Slack User ID
    content TEXT NOT NULL,           -- ノート本文
    embedding VECTOR(1024),          -- Claude API Embedding (1024次元、追加コストなし)
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notes_session ON notes(session_id);
CREATE INDEX idx_notes_user ON notes(user_id);
CREATE INDEX idx_notes_created_at ON notes(created_at);

-- Vector Search用インデックス（ivfflat: 高速だが近似検索）
CREATE INDEX idx_notes_embedding ON notes USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);  -- lists: クラスタ数（100,000ノート想定）
```

**Embedding生成**:
- Claude API Embedding（追加コストなし）
- 1024次元
- Anthropic APIで直接生成

#### sessions table

```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,             -- Claude Code Session ID
    user_id TEXT NOT NULL,           -- Slack User ID
    workspace_path TEXT NOT NULL,    -- Claude Code Workspace Path
    last_active_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_last_active ON sessions(last_active_at);
```

**Session Cleanup**:
- 30日間アクティビティなし → 自動削除（Cron Job）

## Repository Implementation

### PostgreSQLTaskRepository

```python
from src.domain.repositories.task_repository import TaskRepository
from src.domain.models.task import Task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

class PostgreSQLTaskRepository(TaskRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, task: Task) -> Task:
        """タスク作成"""
        stmt = insert(tasks_table).values(
            id=task.id,
            title=task.title,
            description=task.description,
            assignee_user_id=task.assignee_user_id,
            creator_user_id=task.creator_user_id,
            status=task.status,
            due_at=task.due_at,
        ).returning(tasks_table)

        result = await self._session.execute(stmt)
        await self._session.commit()
        return self._map_to_entity(result.fetchone())

    async def get(self, task_id: UUID) -> Task | None:
        """タスク取得"""
        stmt = select(tasks_table).where(tasks_table.c.id == task_id)
        result = await self._session.execute(stmt)
        row = result.fetchone()
        return self._map_to_entity(row) if row else None

    async def update(self, task: Task) -> Task:
        """タスク更新"""
        stmt = update(tasks_table).where(
            tasks_table.c.id == task.id
        ).values(
            title=task.title,
            description=task.description,
            assignee_user_id=task.assignee_user_id,
            status=task.status,
            due_at=task.due_at,
            completed_at=task.completed_at,
            updated_at=datetime.utcnow(),
        ).returning(tasks_table)

        result = await self._session.execute(stmt)
        await self._session.commit()
        return self._map_to_entity(result.fetchone())

    async def delete(self, task_id: UUID) -> None:
        """タスク削除"""
        stmt = delete(tasks_table).where(tasks_table.c.id == task_id)
        await self._session.execute(stmt)
        await self._session.commit()

    async def list_by_user(self, user_id: str, status: str | None = None) -> list[Task]:
        """ユーザーのタスク一覧"""
        stmt = select(tasks_table).where(tasks_table.c.assignee_user_id == user_id)
        if status:
            stmt = stmt.where(tasks_table.c.status == status)
        stmt = stmt.order_by(tasks_table.c.due_at.asc().nullslast())

        result = await self._session.execute(stmt)
        return [self._map_to_entity(row) for row in result.fetchall()]

    def _map_to_entity(self, row) -> Task:
        """DB行 → Entityマッピング"""
        return Task(
            id=row.id,
            title=row.title,
            description=row.description,
            assignee_user_id=row.assignee_user_id,
            creator_user_id=row.creator_user_id,
            status=row.status,
            due_at=row.due_at,
            completed_at=row.completed_at,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
```

### PostgreSQLNoteRepository (with Vector Search)

```python
from src.domain.repositories.note_repository import NoteRepository
from src.domain.models.note import Note
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

class PostgreSQLNoteRepository(NoteRepository):
    def __init__(self, session: AsyncSession, claude_client):
        self._session = session
        self._claude_client = claude_client

    async def save(self, note: Note) -> Note:
        """ノート保存（embedding自動生成）"""
        # Claude Embedding生成
        embedding = await self._generate_embedding(note.content)

        stmt = insert(notes_table).values(
            id=note.id,
            session_id=note.session_id,
            user_id=note.user_id,
            content=note.content,
            embedding=embedding,
        ).returning(notes_table)

        result = await self._session.execute(stmt)
        await self._session.commit()
        return self._map_to_entity(result.fetchone())

    async def search(self, query: str, user_id: str, limit: int = 5) -> list[Note]:
        """Vector Search（類似ノート検索）"""
        # Query embeddingを生成
        query_embedding = await self._generate_embedding(query)

        # Cosine similarity検索（pgvector）
        stmt = select(
            notes_table,
            text("1 - (embedding <=> :query_embedding) AS similarity")
        ).where(
            notes_table.c.user_id == user_id
        ).order_by(
            text("embedding <=> :query_embedding")
        ).limit(limit)

        result = await self._session.execute(stmt, {"query_embedding": query_embedding})
        return [self._map_to_entity(row) for row in result.fetchall()]

    async def _generate_embedding(self, text: str) -> list[float]:
        """Claude Embedding生成（追加コストなし）"""
        # Note: Claude API Embeddingエンドポイントを使用
        # 実装詳細はPhase 1実装時にClaude APIドキュメント参照
        response = await self._claude_client.embeddings.create(
            input=text,
        )
        return response.embedding
```

## Connection Management

### SQLAlchemy Async Engine

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

class DatabaseManager:
    def __init__(self, database_url: str):
        self._engine = create_async_engine(
            database_url,
            echo=False,  # Productionではfalse
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # 接続確認
            pool_recycle=3600,   # 1時間でコネクション再利用
        )
        self._session_maker = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def get_session(self) -> AsyncSession:
        """セッション取得（contextmanager）"""
        async with self._session_maker() as session:
            yield session

    async def close(self):
        """エンジンクローズ"""
        await self._engine.dispose()
```

### Dependency Injection

```python
# src/infrastructure/di.py

from src.adapters.secondary.postgresql_task_repository import PostgreSQLTaskRepository

async def build_task_repository() -> TaskRepository:
    """Task Repository DI"""
    db_manager = DatabaseManager(settings.database_url)
    async with db_manager.get_session() as session:
        return PostgreSQLTaskRepository(session)
```

## Data Migration

### Migration Script

```python
# scripts/migrate_to_postgresql.py

import asyncio
import json
from pathlib import Path
from src.infrastructure.database import DatabaseManager

async def migrate_notes():
    """ノートをFile → PostgreSQLに移行"""
    db_manager = DatabaseManager(settings.database_url)
    note_repo = PostgreSQLNoteRepository(db_manager.get_session())

    notes_dir = Path("data/notes")
    for note_file in notes_dir.glob("*.json"):
        with open(note_file) as f:
            note_data = json.load(f)

        # PostgreSQLに保存（embedding自動生成）
        await note_repo.save(Note(
            session_id=note_data["session_id"],
            user_id=note_data["user_id"],
            content=note_data["content"],
        ))

        print(f"✅ Migrated: {note_file.name}")

    # 移行完了後、ファイル削除
    for note_file in notes_dir.glob("*.json"):
        note_file.unlink()

async def migrate_sessions():
    """セッションをFile → PostgreSQLに移行"""
    # 同様の処理

if __name__ == "__main__":
    asyncio.run(migrate_notes())
    asyncio.run(migrate_sessions())
```

## Environment Variables

```bash
# Database (Phase 1で追加)
DATABASE_URL=postgresql+asyncpg://nakamura_misaki:password@localhost:5432/nakamura_misaki

# OpenAI (Vector Search用)
OPENAI_API_KEY=sk-...

# Supabase (オプション: Supabase使用時)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGc...
```

## NixOS Configuration

```nix
# modules/services/registry/nakamura-misaki-db.nix

{ config, pkgs, ... }:

{
  services.postgresql = {
    enable = true;
    package = pkgs.postgresql_16;
    enableTCPIP = true;

    # pgvector extension
    extraPlugins = with pkgs.postgresql16Packages; [ pgvector ];

    initialScript = pkgs.writeText "init.sql" ''
      CREATE DATABASE nakamura_misaki;
      \c nakamura_misaki;
      CREATE EXTENSION IF NOT EXISTS vector;

      CREATE USER nakamura_misaki WITH PASSWORD 'password';
      GRANT ALL PRIVILEGES ON DATABASE nakamura_misaki TO nakamura_misaki;
    '';
  };

  # Backup (オプション)
  services.postgresqlBackup = {
    enable = true;
    databases = [ "nakamura_misaki" ];
  };
}
```

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_postgresql_task_repository.py

@pytest.mark.asyncio
async def test_create_task(db_session):
    """タスク作成"""
    repo = PostgreSQLTaskRepository(db_session)

    task = Task(
        title="API統合",
        assignee_user_id="U01ABC123",
        creator_user_id="U01ABC123",
        due_at=datetime(2025, 10, 15, 15, 0),
    )

    result = await repo.create(task)

    assert result.id is not None
    assert result.title == "API統合"
    assert result.status == "pending"

@pytest.mark.asyncio
async def test_vector_search(db_session, openai_client):
    """Vector Search"""
    repo = PostgreSQLNoteRepository(db_session, openai_client)

    # ノート保存
    await repo.save(Note(
        session_id="sess_123",
        user_id="U01ABC123",
        content="PostgreSQL 16を採用することに決定",
    ))

    # 検索
    results = await repo.search("DB決定", user_id="U01ABC123", limit=5)

    assert len(results) > 0
    assert "PostgreSQL" in results[0].content
```

### Integration Tests

```python
# tests/integration/test_database_migration.py

@pytest.mark.asyncio
async def test_migrate_notes_from_file():
    """ノート移行（File → PostgreSQL）"""
    # テストデータ作成
    note_file = Path("data/notes/test.json")
    note_file.write_text(json.dumps({
        "session_id": "sess_123",
        "user_id": "U01ABC123",
        "content": "テストノート",
    }))

    # 移行実行
    await migrate_notes()

    # PostgreSQLから確認
    repo = PostgreSQLNoteRepository(db_session, openai_client)
    notes = await repo.list_by_session("sess_123")

    assert len(notes) == 1
    assert notes[0].content == "テストノート"

    # ファイル削除確認
    assert not note_file.exists()
```

## Performance Optimization

### Index Strategy

- **Primary Key**: B-tree index（自動）
- **Foreign Key**: B-tree index
- **Timestamp検索**: B-tree index + Partial index（NULL除外）
- **Vector Search**: ivfflat index（近似検索）

### Query Optimization

- `EXPLAIN ANALYZE` で実行計画確認
- N+1問題回避（`joinedload` 使用）
- バッチ挿入（`bulk_insert_mappings`）

## Monitoring

### Metrics

- **Connection Pool**: active/idle connections
- **Query Performance**: p50/p95/p99 latency
- **Vector Search**: search time, embedding generation time

### Logging

```python
logger.info("Task created", extra={
    "task_id": str(task.id),
    "assignee": task.assignee_user_id,
    "duration_ms": duration,
})
```

## Rollback Plan

Phase 1でエラーが発生した場合:

1. `JsonTaskRepository` に戻す（DI設定変更）
2. PostgreSQLは起動したまま（Phase 2再挑戦用）
3. ファイルベースのデータは削除しない（バックアップ）
