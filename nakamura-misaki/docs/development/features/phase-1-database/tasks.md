# Phase 1: Database - Tasks

## Implementation Checklist

### 1. Database Setup

- [ ] **1.1** NixOS設定追加: `modules/services/registry/nakamura-misaki-db.nix`
  - [ ] PostgreSQL 16有効化
  - [ ] pgvector extension追加
  - [ ] 初期データベース作成（`nakamura_misaki`）
  - [ ] ユーザー作成・権限付与
- [ ] **1.2** NixOS再ビルド・デプロイ
  ```bash
  cd nixos-config
  nix flake check
  git add modules/services/registry/nakamura-misaki-db.nix
  git commit -m "feat: Add PostgreSQL 16 + pgvector"
  git push origin main
  ```
- [ ] **1.3** PostgreSQL動作確認
  ```bash
  ssh home-lab-01
  sudo -u postgres psql -c "SELECT version();"
  sudo -u postgres psql nakamura_misaki -c "CREATE EXTENSION IF NOT EXISTS vector;"
  ```

### 2. Schema Creation

- [ ] **2.1** `src/infrastructure/database/schema.py` 作成
  - [ ] SQLAlchemy Table定義（tasks, handoffs, notes, sessions）
  - [ ] Index定義
  - [ ] Constraint定義
- [ ] **2.2** Migration script作成: `scripts/init_db.py`
  ```python
  async def init_database():
      # CREATE TABLE IF NOT EXISTS ...
      # CREATE INDEX IF NOT EXISTS ...
  ```
- [ ] **2.3** Migration実行
  ```bash
  uv run python scripts/init_db.py
  ```
- [ ] **2.4** スキーマ確認
  ```bash
  ssh home-lab-01
  sudo -u postgres psql nakamura_misaki -c "\dt"
  sudo -u postgres psql nakamura_misaki -c "\d tasks"
  ```

### 3. Repository Implementation

#### 3.1 Task Repository
- [ ] **3.1.1** `src/adapters/secondary/postgresql_task_repository.py` 作成
  - [ ] `create(task: Task) -> Task`
  - [ ] `get(task_id: UUID) -> Task | None`
  - [ ] `update(task: Task) -> Task`
  - [ ] `delete(task_id: UUID) -> None`
  - [ ] `list_by_user(user_id: str, status: str | None) -> list[Task]`
  - [ ] `list_due_today(user_id: str) -> list[Task]`
  - [ ] `_map_to_entity(row) -> Task`

#### 3.2 Handoff Repository
- [ ] **3.2.1** `src/adapters/secondary/postgresql_handoff_repository.py` 作成
  - [ ] `create(handoff: Handoff) -> Handoff`
  - [ ] `get(handoff_id: UUID) -> Handoff | None`
  - [ ] `list_by_to_user(user_id: str) -> list[Handoff]`
  - [ ] `list_pending_reminders() -> list[Handoff]`
  - [ ] `mark_reminded(handoff_id: UUID) -> None`

#### 3.3 Note Repository (with Vector Search)
- [ ] **3.3.1** `src/adapters/secondary/postgresql_note_repository.py` 作成
  - [ ] `save(note: Note) -> Note`
  - [ ] `search(query: str, user_id: str, limit: int) -> list[Note]`
  - [ ] `list_by_session(session_id: str) -> list[Note]`
  - [ ] `_generate_embedding(text: str) -> list[float]`
- [ ] **3.3.2** OpenAI Client追加
  ```python
  from openai import AsyncOpenAI
  client = AsyncOpenAI(api_key=settings.openai_api_key)
  ```

#### 3.4 Session Repository
- [ ] **3.4.1** `src/adapters/secondary/postgresql_session_repository.py` 作成
  - [ ] `create(session: Session) -> Session`
  - [ ] `get(session_id: str) -> Session | None`
  - [ ] `update_last_active(session_id: str) -> None`
  - [ ] `delete_inactive(days: int) -> int`

### 4. Connection Management

- [ ] **4.1** `src/infrastructure/database/manager.py` 作成
  - [ ] `DatabaseManager` クラス
  - [ ] Async Engine作成（pool_size=10, max_overflow=20）
  - [ ] `get_session()` contextmanager
  - [ ] `close()` エンジンクローズ
- [ ] **4.2** `src/infrastructure/di.py` 更新
  - [ ] `build_task_repository()` 追加
  - [ ] `build_note_repository()` 追加
  - [ ] `build_handoff_repository()` 追加
  - [ ] `build_session_repository()` 追加

### 5. Environment Configuration

- [ ] **5.1** `.env.example` 更新
  ```bash
  # Database
  DATABASE_URL=postgresql+asyncpg://nakamura_misaki:password@localhost:5432/nakamura_misaki

  # OpenAI (Vector Search)
  OPENAI_API_KEY=sk-...
  ```
- [ ] **5.2** NixOS secrets設定（sops-nix）
  ```bash
  cd nixos-config
  sops secrets/nakamura-misaki.yaml
  # DATABASE_URL, OPENAI_API_KEY を追加
  ```
- [ ] **5.3** NixOS設定で環境変数読み込み
  ```nix
  systemd.services.nakamura-misaki-api = {
    environment = {
      DATABASE_URL = config.sops.secrets."nakamura-misaki/database_url".path;
      OPENAI_API_KEY = config.sops.secrets."nakamura-misaki/openai_api_key".path;
    };
  };
  ```

### 6. Data Migration

- [ ] **6.1** `scripts/migrate_to_postgresql.py` 作成
  - [ ] `migrate_notes()`: `data/notes/*.json` → PostgreSQL
  - [ ] `migrate_sessions()`: `data/sessions/*.json` → PostgreSQL
  - [ ] 冪等性確保（既存データスキップ）
  - [ ] 進捗表示（プログレスバー）
- [ ] **6.2** バックアップ作成
  ```bash
  cd /Users/noguchilin/dev/lab-project/nakamura-misaki
  tar -czf data_backup_$(date +%Y%m%d).tar.gz data/
  ```
- [ ] **6.3** Migration実行
  ```bash
  uv run python scripts/migrate_to_postgresql.py
  ```
- [ ] **6.4** データ確認
  ```bash
  ssh home-lab-01
  sudo -u postgres psql nakamura_misaki -c "SELECT COUNT(*) FROM notes;"
  sudo -u postgres psql nakamura_misaki -c "SELECT COUNT(*) FROM sessions;"
  ```
- [ ] **6.5** ファイル削除（バックアップ確認後）
  ```bash
  rm -rf data/notes/ data/sessions/
  ```

### 7. Testing

#### 7.1 Unit Tests
- [ ] **7.1.1** `tests/unit/test_postgresql_task_repository.py`
  - [ ] `test_create_task`
  - [ ] `test_get_task`
  - [ ] `test_update_task`
  - [ ] `test_delete_task`
  - [ ] `test_list_by_user`
  - [ ] `test_list_due_today`
- [ ] **7.1.2** `tests/unit/test_postgresql_note_repository.py`
  - [ ] `test_save_note_with_embedding`
  - [ ] `test_vector_search`
  - [ ] `test_search_returns_top_k`
- [ ] **7.1.3** `tests/unit/test_database_manager.py`
  - [ ] `test_connection_pool`
  - [ ] `test_session_lifecycle`
  - [ ] `test_connection_error_retry`

#### 7.2 Integration Tests
- [ ] **7.2.1** `tests/integration/test_database_migration.py`
  - [ ] `test_migrate_notes_from_file`
  - [ ] `test_migrate_sessions_from_file`
  - [ ] `test_migration_idempotent`
- [ ] **7.2.2** `tests/integration/test_postgresql_integration.py`
  - [ ] `test_task_crud_workflow`
  - [ ] `test_handoff_crud_workflow`
  - [ ] `test_note_vector_search_workflow`

#### 7.3 Performance Tests
- [ ] **7.3.1** `tests/performance/test_database_performance.py`
  - [ ] `test_task_query_performance`: 100ms以内
  - [ ] `test_vector_search_performance`: 1秒以内
  - [ ] `test_batch_insert_performance`: 1000件/秒以上

### 8. Documentation

- [ ] **8.1** `docs/IMPLEMENTATION_PLAN.md` 更新
  - [ ] Phase 1の実装状況記録
- [ ] **8.2** `claudedocs/database-schema.md` 作成
  - [ ] ER図
  - [ ] Table説明
  - [ ] Index戦略
  - [ ] Vector Search使い方

### 9. Deployment

- [ ] **9.1** ローカルテスト
  ```bash
  uv run pytest tests/unit/test_postgresql_*.py -v
  uv run pytest tests/integration/test_database_*.py -v
  ```
- [ ] **9.2** Git Commit
  ```bash
  git add src/adapters/secondary/postgresql_*.py src/infrastructure/database/ scripts/
  git commit -m "feat: Implement Phase 1 - PostgreSQL + pgvector"
  ```
- [ ] **9.3** GitHub Push（自動デプロイ）
  ```bash
  git push origin main
  ```
- [ ] **9.4** NixOS再起動（PostgreSQL起動確認）
  ```bash
  ssh home-lab-01
  sudo systemctl restart nakamura-misaki-api.service
  journalctl -u nakamura-misaki-api.service -f
  ```

### 10. Validation

- [ ] **10.1** PostgreSQL接続確認
  ```bash
  ssh home-lab-01
  sudo -u postgres psql nakamura_misaki -c "SELECT COUNT(*) FROM tasks;"
  ```
- [ ] **10.2** Slackで動作確認（ノート検索）
  - [ ] 質問: "DB移行の決定事項は？"
  - [ ] Vector Searchが動作することを確認
- [ ] **10.3** パフォーマンス確認
  - [ ] タスク検索: 100ms以内
  - [ ] Vector Search: 1秒以内

### 11. Post-Deployment

- [ ] **11.1** メトリクス確認
  - [ ] Connection Pool使用率
  - [ ] Query Performance (p50/p95/p99)
  - [ ] Vector Search時間
- [ ] **11.2** バックアップ設定確認
  ```bash
  ssh home-lab-01
  systemctl status postgresql-backup.service
  ```
- [ ] **11.3** Old Repository削除（DI設定から）
  - [ ] `JsonNoteRepository` 削除
  - [ ] `JsonSessionRepository` 削除

### 12. Rollback Plan (問題発生時のみ)

- [ ] **12.1** DI設定を戻す
  ```python
  # src/infrastructure/di.py
  # PostgreSQLTaskRepository → JsonTaskRepository に戻す
  ```
- [ ] **12.2** ファイルベースデータをリストア
  ```bash
  tar -xzf data_backup_YYYYMMDD.tar.gz
  ```
- [ ] **12.3** 再デプロイ
  ```bash
  git add src/infrastructure/di.py
  git commit -m "fix: Rollback to file-based repository"
  git push origin main
  ```

## Estimated Timeline

| Task | Estimated Time | Dependencies |
|------|----------------|--------------|
| 1. Database Setup | 2 hours | - |
| 2. Schema Creation | 2 hours | 1 |
| 3. Repository Implementation | 6 hours | 2 |
| 4. Connection Management | 2 hours | 2 |
| 5. Environment Configuration | 1 hour | 1 |
| 6. Data Migration | 3 hours | 3, 4 |
| 7. Testing | 4 hours | 3, 4, 6 |
| 8. Documentation | 1 hour | - |
| 9. Deployment | 1 hour | 7 |
| 10. Validation | 1 hour | 9 |
| 11. Post-Deployment | 1 hour | 10 |
| **Total** | **24 hours** | - |

## Dependencies

- ✅ NixOS環境（home-lab-01）
- ✅ sops-nix（秘密情報管理）
- ⏳ OpenAI API Key（Vector Search用）
- ⏳ PostgreSQL 16
- ⏳ pgvector extension

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| データ移行失敗 | High | Medium | バックアップ作成、冪等性確保、ロールバックプラン |
| Vector Search遅い | Medium | Low | ivfflat index、lists調整、クエリ最適化 |
| Connection Pool枯渇 | High | Low | pool_size/max_overflow調整、タイムアウト設定 |
| OpenAI API障害 | Medium | Low | Embedding生成失敗時はテキスト検索にフォールバック |

## Success Criteria

Phase 1は以下を満たせば完了：

1. **Database Setup**:
   - [ ] PostgreSQL 16 + pgvectorが正常動作
   - [ ] 全テーブル・インデックスが作成される

2. **Repository Implementation**:
   - [ ] 全CRUD操作が正常動作
   - [ ] Vector Searchが1秒以内に完了

3. **Data Migration**:
   - [ ] 既存ファイルが全てPostgreSQLにインポート
   - [ ] データ欠損なし

4. **Testing**:
   - [ ] 単体テスト: 80%以上カバレッジ
   - [ ] 統合テスト: 全パス成功
   - [ ] パフォーマンステスト: 目標値達成

5. **Deployment**:
   - [ ] NixOSで正常動作
   - [ ] エラーなし
