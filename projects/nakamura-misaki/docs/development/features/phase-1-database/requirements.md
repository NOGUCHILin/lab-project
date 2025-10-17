# Phase 1: Database - Requirements

## Overview

ファイルベースのデータ管理からPostgreSQL + pgvectorへ移行する。タスク・ハンドオフ・ノートの永続化を実現し、Phase 2以降の基盤を構築する。

## User Stories

### Story 1: データ永続化

**As a** nakamura-misaki運用者
**I want** タスク・ハンドオフ・ノートがPostgreSQLに保存される
**So that** サービス再起動後もデータが保持される

**Acceptance Criteria**:
- [ ] タスクがPostgreSQLに保存される（CRUD操作）
- [ ] ハンドオフがPostgreSQLに保存される
- [ ] ノート（Anthropic Note-Taking）がPostgreSQLに保存される
- [ ] サービス再起動後もデータが保持される

### Story 2: ノート検索（Vector Search）

**As a** チームメンバー
**I want** 過去のノートを自然言語で検索できる
**So that** 重要な決定事項を素早く見つけられる

**Acceptance Criteria**:
- [ ] ノートテキストがベクトル化される（pgvector）
- [ ] 自然言語クエリで類似ノートを検索できる
- [ ] 検索結果は関連度順に並ぶ
- [ ] 検索速度は1秒以内

**Example**:
```
User: DBの決定事項は？
nakamura-misaki:
  📖 過去のノートから検索（Vector Search）

  【2025-10-07】DB移行の決定
  - PostgreSQL 16
  - Supabase pgvector
  - 移行日: 2025-10-15

  【2025-09-20】DB選定の議論
  - 候補: PostgreSQL, MongoDB
  - 結論: PostgreSQL採用
```

### Story 3: データ移行（File → PostgreSQL）

**As a** nakamura-misaki運用者
**I want** 既存ファイルのデータをPostgreSQLに移行する
**So that** 過去のデータが失われない

**Acceptance Criteria**:
- [ ] 既存ノートファイル（`data/notes/*.json`）をPostgreSQLにインポート
- [ ] 既存セッションファイル（`data/sessions/*.json`）をPostgreSQLにインポート
- [ ] 移行後、ファイルは削除される
- [ ] 移行スクリプトは冪等（再実行可能）

## Functional Requirements

### FR-1: Database Schema

#### Tables

**tasks**:
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,
    assignee_user_id TEXT NOT NULL,  -- Slack User ID
    creator_user_id TEXT NOT NULL,   -- Slack User ID
    status TEXT NOT NULL DEFAULT 'pending',  -- pending, in_progress, completed, cancelled
    due_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tasks_assignee ON tasks(assignee_user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_at ON tasks(due_at);
```

**handoffs**:
```sql
CREATE TABLE handoffs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    from_user_id TEXT NOT NULL,
    to_user_id TEXT NOT NULL,
    progress_note TEXT,  -- 現在の進捗状況
    next_steps TEXT,     -- 次のステップ
    handoff_at TIMESTAMP NOT NULL,  -- 引き継ぎ予定日時
    reminded_at TIMESTAMP,           -- リマインダー送信済み日時
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_handoffs_to_user ON handoffs(to_user_id);
CREATE INDEX idx_handoffs_handoff_at ON handoffs(handoff_at);
```

**notes** (Anthropic Structured Note-Taking):
```sql
CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1536),  -- pgvector: OpenAI text-embedding-3-small
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notes_session ON notes(session_id);
CREATE INDEX idx_notes_user ON notes(user_id);
CREATE INDEX idx_notes_embedding ON notes USING ivfflat (embedding vector_cosine_ops);  -- Vector Search
```

**sessions** (Claude Code Session管理):
```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,  -- Claude Code Session ID
    user_id TEXT NOT NULL,
    workspace_path TEXT NOT NULL,
    last_active_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_last_active ON sessions(last_active_at);
```

### FR-2: Repository Implementation

- `PostgreSQLTaskRepository` (implements `TaskRepository`)
- `PostgreSQLHandoffRepository` (implements `HandoffRepository`)
- `PostgreSQLNoteRepository` (implements `NoteRepository`)
- `PostgreSQLSessionRepository` (implements `SessionRepository`)

### FR-3: Vector Search

- Claude API経由でEmbedding生成（追加コストなし）
- ノート保存時に自動的にembedding生成
- 検索時は類似度（cosine similarity）でランキング

### FR-4: Migration Script

- `scripts/migrate_to_postgresql.py`
- 既存ファイル（`data/notes/*.json`, `data/sessions/*.json`）をPostgreSQLにインポート
- 冪等性（既にインポート済みのデータはスキップ）

## Non-Functional Requirements

### NFR-1: Performance
- タスク検索: 100ms以内
- ノート検索（Vector Search）: 1秒以内
- データベース接続プール: 10-20接続

### NFR-2: Reliability
- トランザクション管理（ACID保証）
- 接続エラー時のリトライ（最大3回）
- デッドロック検知と再実行

### NFR-3: Scalability
- 10,000タスクまで対応
- 100,000ノートまで対応
- Vector Search indexing (ivfflat)

### NFR-4: Security
- DATABASE_URL環境変数で管理（sops-nix暗号化）
- SQLインジェクション対策（SQLAlchemy ORM使用）
- 最小権限の原則（DBユーザーはCRUDのみ）

## Success Metrics

### Phase 1完了基準

1. **Database Setup**:
   - [ ] PostgreSQL 16がNixOSで起動
   - [ ] pgvector extensionが有効
   - [ ] 全テーブルが作成される

2. **Repository Implementation**:
   - [ ] 全CRUD操作が正常動作
   - [ ] トランザクション管理が正常動作
   - [ ] エラーハンドリングが正常動作

3. **Vector Search**:
   - [ ] ノート保存時にembedding生成
   - [ ] 検索が1秒以内に完了
   - [ ] 検索結果が関連度順に並ぶ

4. **Data Migration**:
   - [ ] 既存ファイルが全てPostgreSQLにインポート
   - [ ] 移行後、nakamura-misakiが正常動作
   - [ ] 移行前後でデータ欠損なし

## Out of Scope (Phase 1では実装しない)

- ❌ タスクAPI実装（Phase 2）
- ❌ ハンドオフAPI実装（Phase 3）
- ❌ Admin UI（Phase 4）
- ❌ PostgreSQLのバックアップ・リストア（運用フェーズ）
- ❌ Read Replica（スケール時に検討）

**Phase 1のスコープ**: データベーススキーマ作成、Repository実装、データ移行のみ
