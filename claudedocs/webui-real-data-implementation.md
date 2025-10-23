# nakamura-misaki Web UI - 実データ実装計画

**目的**: MockデータからPostgreSQL実データへの移行 + Anthropic Context Engineering準拠のプロンプト管理UI実装

**最終更新**: 2025-10-23

---

## 🎯 プロジェクト概要

### 現状の問題

| エンドポイント | 現状 | 問題 |
|------------|------|------|
| `GET /api/tasks` | ✅ DB実装あり | ❌ MockデータをWeb UIに返却 |
| `GET /api/users` | ❌ DB実装なし | ❌ Mockデータのみ |
| `GET /api/sessions` | ✅ conversationsテーブルあり | ❌ Mockデータ返却 |
| `GET /api/logs/errors` | ❌ DB実装なし | ❌ 空配列返却 |
| `GET /api/admin/prompts` | ❌ エンドポイント自体が存在しない | ❌ 404エラー |

**重大な問題**: 本番環境で**Mockデータ**が動作中（Yahoo広告タスクがDBに存在するのに、Web UIには表示されない）

---

## 🏗️ アーキテクチャ設計

### Anthropic Context Engineering原則の適用

**核心概念**: 「最小限かつ高信号なトークンセットで目標達成の確率を最大化する」

#### 設計方針

| データ種別 | 管理方法 | 理由 |
|---------|---------|------|
| **Tasks** | PostgreSQL | 業務データ、永続化必須 |
| **Conversations/Sessions** | PostgreSQL + 圧縮機能 | Anthropic推奨「構造化ノート」パターン |
| **Users** | Slack API + PostgreSQL Cache | Hybrid Approach（将来拡張対応） |
| **Error Logs** | PostgreSQL | 監視・分析用 |
| **Prompts** | PostgreSQL + Context Settings | **コンテキストエンジニアリングUI実装** |

### プロンプト管理の革新的アプローチ

**従来**: ファイルにプロンプトを保存 → 開発者がAnthropicの原則を知っている前提

**新アプローチ**: UI自体がAnthropicの原則を実装 → 自然と最適化されたプロンプトが生成される

**UI機能例**:
- トークン数リアルタイム表示 → "最小限の高信号トークン"を視覚化
- 圧縮設定スライダー → 会話圧縮タイミングを調整可能
- Few-shot例管理（最大5件制限） → "厳選された代表例"を強制
- XMLタグ補助 → 構造化プロンプトを促進
- 明確性スコア → AI分析で曖昧表現を検出

---

## 📐 データベース設計

### 1. users テーブル（Hybrid User Management）

```sql
CREATE TABLE users (
  user_id VARCHAR(100) PRIMARY KEY,  -- Slack User ID

  -- Slack同期フィールド（定期更新）
  name VARCHAR(100),
  real_name VARCHAR(200),
  display_name VARCHAR(200),
  email VARCHAR(255),
  avatar_url TEXT,
  is_bot BOOLEAN DEFAULT false,
  deleted BOOLEAN DEFAULT false,

  -- 独自拡張フィールド（将来対応）
  preferences JSONB,          -- ユーザー設定
  custom_fields JSONB,        -- カスタムフィールド
  role VARCHAR(50),           -- 独自ロール管理
  department VARCHAR(100),    -- 部署情報

  -- メタデータ
  slack_synced_at TIMESTAMPTZ,  -- 最終Slack同期時刻
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_deleted ON users(deleted) WHERE NOT deleted;
```

**実装戦略**:
- Web UI初回アクセス時にSlack APIから取得してDB保存
- 定期的にSlack APIと同期（1日1回など）
- 独自フィールド（preferences等）はDB管理

---

### 2. error_logs テーブル

```sql
CREATE TABLE error_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- エラー識別
  error_hash VARCHAR(64) NOT NULL,  -- SHA256(message + stack)
  message TEXT NOT NULL,
  stack TEXT,

  -- 発生コンテキスト
  url TEXT,
  user_agent TEXT,
  user_id VARCHAR(100),  -- どのユーザーで発生したか
  session_id UUID,       -- どのセッションで発生したか
  context JSONB,         -- 追加情報（リクエストパラメータ等）

  -- 集計情報
  occurrence_count INT DEFAULT 1,
  first_seen TIMESTAMPTZ NOT NULL,
  last_seen TIMESTAMPTZ NOT NULL,

  -- メタデータ
  resolved BOOLEAN DEFAULT false,  -- 解決済みフラグ
  resolved_at TIMESTAMPTZ,
  resolved_by VARCHAR(100),
  notes TEXT,  -- 解決メモ

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_error_logs_hash ON error_logs(error_hash);
CREATE INDEX idx_error_logs_last_seen ON error_logs(last_seen DESC);
CREATE INDEX idx_error_logs_resolved ON error_logs(resolved) WHERE NOT resolved;
CREATE INDEX idx_error_logs_user ON error_logs(user_id);
```

**用途**:
- 重複エラーの自動集約（error_hash）
- ユーザー別エラー追跡
- 未解決エラーのモニタリング

---

### 3. prompts テーブル（Context Engineering対応）

```sql
CREATE TABLE prompts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- プロンプト識別
  name VARCHAR(100) NOT NULL UNIQUE,
  category VARCHAR(50),
  description TEXT,

  -- プロンプト内容
  system_prompt TEXT NOT NULL,
  version VARCHAR(50) NOT NULL,
  is_active BOOLEAN DEFAULT true,

  -- Anthropic原則に基づくメタデータ
  token_count INT,                    -- トークン数
  clarity_score DECIMAL(3,1),         -- 明確性スコア（1-10）
  uses_xml_tags BOOLEAN DEFAULT false, -- XML構造化
  uses_few_shot BOOLEAN DEFAULT false, -- Few-shot使用

  -- コンテキスト最適化設定（重要！）
  context_settings JSONB DEFAULT '{
    "compression_threshold": 8000,
    "compression_strength": "medium",
    "preserve_notes": true,
    "max_few_shot_examples": 3,
    "enable_thinking": false
  }',

  -- バージョン管理
  parent_id UUID,

  -- 監査ログ
  created_by VARCHAR(100) NOT NULL,
  updated_by VARCHAR(100),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  FOREIGN KEY (parent_id) REFERENCES prompts(id) ON DELETE SET NULL
);

CREATE INDEX idx_prompts_name_active ON prompts(name, is_active) WHERE is_active;
CREATE INDEX idx_prompts_category ON prompts(category);
```

---

### 4. prompt_few_shot_examples テーブル

```sql
CREATE TABLE prompt_few_shot_examples (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  prompt_id UUID REFERENCES prompts(id) ON DELETE CASCADE,

  -- Few-shot例
  input_example TEXT NOT NULL,
  output_example TEXT NOT NULL,

  -- 多様性管理
  diversity_tag VARCHAR(50),  -- "edge_case", "typical", "complex"
  order_index INT,            -- 表示順

  -- 評価
  effectiveness_score DECIMAL(3,1),  -- この例の効果（A/Bテスト結果）

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_few_shot_prompt ON prompt_few_shot_examples(prompt_id, order_index);
```

---

### 5. context_compression_logs テーブル

```sql
CREATE TABLE context_compression_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID REFERENCES conversations(id),

  -- 圧縮前後の情報
  original_token_count INT,
  compressed_token_count INT,
  compression_ratio DECIMAL(5,2),  -- 圧縮率

  -- 圧縮内容
  summary TEXT,
  preserved_notes JSONB,  -- 保持した重要情報

  -- パフォーマンス評価
  quality_score DECIMAL(3,1),  -- 圧縮後の応答品質

  compressed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_compression_logs_conversation ON context_compression_logs(conversation_id);
CREATE INDEX idx_compression_logs_compressed_at ON context_compression_logs(compressed_at DESC);
```

---

### 6. conversation_notes テーブル（構造化ノート）

```sql
CREATE TABLE conversation_notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,

  -- ノート内容
  note_type VARCHAR(50) NOT NULL,  -- "decision", "bug", "requirement", "architecture"
  content TEXT NOT NULL,

  -- メタデータ
  importance INT DEFAULT 5,  -- 1-10（重要度）
  referenced_count INT DEFAULT 0,  -- 参照された回数

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notes_conversation ON conversation_notes(conversation_id);
CREATE INDEX idx_notes_type ON conversation_notes(note_type);
CREATE INDEX idx_notes_importance ON conversation_notes(importance DESC);
```

---

### 7. conversations テーブルへの拡張

```sql
-- 既存テーブルに追加カラム
ALTER TABLE conversations
ADD COLUMN summary TEXT,              -- 要約コンテキスト
ADD COLUMN token_count INT DEFAULT 0, -- トークン数追跡
ADD COLUMN compressed_at TIMESTAMPTZ; -- 最終圧縮時刻
```

---

## 🚀 実装計画（6フェーズ）

### Phase 1: Mock削除 + 実DB接続 🔴 **最優先**

**目的**: 本番環境のMockデータを即座に実データに置き換え

**実装内容**:

#### 1.1 Tasks API（既存Repository活用）

**ファイル**: `src/adapters/primary/api/routes/webui.py`

```python
from ....contexts.personal_tasks.infrastructure.repositories.postgresql_task_repository import (
    PostgreSQLTaskRepository,
)
from ....infrastructure.database.manager import get_db

@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(db: AsyncSession = Depends(get_db)) -> list[TaskResponse]:
    """List all tasks (real data from PostgreSQL)"""
    repo = PostgreSQLTaskRepository(db)
    tasks = await repo.find_all()

    return [
        TaskResponse(
            id=str(task.id),
            user_id=task.assignee_user_id,
            title=task.title,
            due_date=task.due_at.isoformat() if task.due_at else "",
            status=task.status.value,
            progress=0,  # TODO: 進捗率の計算ロジック追加
            description=task.description or "",
            created_by=task.creator_user_id,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
        )
        for task in tasks
    ]
```

#### 1.2 Sessions API（conversationsテーブル活用）

```python
from ....contexts.conversations.infrastructure.repositories.postgresql_conversation_repository import (
    PostgreSQLConversationRepository,
)

@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)) -> list[SessionResponse]:
    """List all sessions (from conversations table)"""
    repo = PostgreSQLConversationRepository(db)
    conversations = await repo.find_all(limit=50)

    return [
        SessionResponse(
            session_id=str(conv.conversation_id),
            user_id=conv.user_id,
            created_at=conv.created_at.isoformat(),
            last_active=conv.last_message_at.isoformat(),
            title=f"Conversation with {conv.user_id}",  # TODO: タイトル生成
            message_count=len(conv.messages),
            is_active=(datetime.now(UTC) - conv.last_message_at).total_seconds() < 3600,
        )
        for conv in conversations
    ]
```

#### 1.3 Users API（Slack API呼び出し）

```python
from ....adapters.primary.dependencies import get_slack_adapter

@router.get("/users", response_model=list[UserResponse])
async def list_users() -> list[UserResponse]:
    """List all users (from Slack API)"""
    slack = get_slack_adapter()
    users_result = await slack.users_list()

    if not users_result.get("ok"):
        raise HTTPException(status_code=500, detail="Failed to fetch users from Slack")

    return [
        UserResponse(
            user_id=user["id"],
            name=user.get("name", ""),
            real_name=user.get("real_name", ""),
            display_name=user.get("profile", {}).get("display_name", ""),
            email=user.get("profile", {}).get("email", ""),
            is_admin=user.get("is_admin", False),
            is_bot=user.get("is_bot", False),
            created_at=datetime.fromtimestamp(user.get("updated", 0), tz=UTC).isoformat(),
        )
        for user in users_result.get("members", [])
        if not user.get("deleted", False)
    ]
```

**成果物**:
- ✅ Tasks → 実DB（Yahoo広告タスクが表示される）
- ✅ Sessions → conversationsテーブル
- ✅ Users → Slack API（リアルタイム）

**テスト方法**:
```bash
# ローカルでビルド確認
cd projects/nakamura-misaki/web-ui
npm run build

# デプロイ前確認
curl https://home-lab-01.tail4ed625.ts.net:10000/api/tasks
```

---

### Phase 2: 新規テーブル設計 + Migration作成

**目的**: users, error_logs, prompts関連テーブルの作成

**実装内容**:

#### 2.1 Alembic Migration作成

**ファイル**: `projects/nakamura-misaki/migrations/versions/YYYYMMDD_add_webui_tables.py`

```python
"""Add Web UI tables: users, error_logs, prompts, prompt_few_shot_examples, context_compression_logs, conversation_notes

Revision ID: XXXXXX
Revises: YYYYYY
Create Date: 2025-10-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# ... migration code
```

**実行コマンド**:
```bash
cd projects/nakamura-misaki
alembic revision --autogenerate -m "add_webui_tables"
alembic upgrade head
```

**検証**:
```bash
ssh home-lab-01 'psql -U nakamura_misaki -d nakamura_misaki -c "\dt"'
```

---

### Phase 3: Repository層実装

**目的**: 各テーブルへのCRUD操作を実装

#### 3.1 UserRepository

**ファイル**: `src/contexts/users/infrastructure/repositories/postgresql_user_repository.py`

```python
class PostgreSQLUserRepository(UserRepository):
    """PostgreSQL implementation with Slack sync"""

    async def sync_from_slack(self, slack_users: list[dict]) -> None:
        """Slack APIからユーザーを同期"""
        for user_data in slack_users:
            user = await self.find_by_id(user_data["id"])
            if user:
                await self.update(user_data)
            else:
                await self.create(user_data)
```

#### 3.2 ErrorLogRepository

**ファイル**: `src/contexts/error_logs/infrastructure/repositories/postgresql_error_log_repository.py`

```python
class PostgreSQLErrorLogRepository(ErrorLogRepository):
    """Error log repository with deduplication"""

    async def log_or_increment(self, error_data: dict) -> ErrorLog:
        """エラーハッシュで重複チェック、既存なら発生回数を増加"""
        error_hash = hashlib.sha256(
            f"{error_data['message']}{error_data.get('stack', '')}".encode()
        ).hexdigest()

        existing = await self.find_by_hash(error_hash)
        if existing:
            existing.occurrence_count += 1
            existing.last_seen = datetime.now(UTC)
            return await self.update(existing)
        else:
            return await self.create({**error_data, "error_hash": error_hash})
```

#### 3.3 PromptRepository

**ファイル**: `src/contexts/prompts/infrastructure/repositories/postgresql_prompt_repository.py`

```python
class PostgreSQLPromptRepository(PromptRepository):
    """Prompt repository with versioning and context settings"""

    async def create_version(self, prompt_id: UUID, updated_by: str) -> Prompt:
        """新しいバージョンを作成（親プロンプトを参照）"""
        parent = await self.find_by_id(prompt_id)
        new_version = Prompt(
            name=parent.name,
            system_prompt=parent.system_prompt,
            version=self._increment_version(parent.version),
            parent_id=parent.id,
            created_by=updated_by,
        )
        return await self.create(new_version)
```

---

### Phase 4: API実装（Repository連携）

**目的**: Web UI APIをRepository経由で実データ返却

#### 4.1 Error Logs API

```python
@router.get("/logs/errors", response_model=list[ErrorLogResponse])
async def list_error_logs(
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> list[ErrorLogResponse]:
    """List recent error logs (real data)"""
    repo = PostgreSQLErrorLogRepository(db)
    errors = await repo.find_recent(limit=limit, resolved=False)
    return [ErrorLogResponse.from_entity(e) for e in errors]

@router.post("/logs/errors")
async def log_error(
    error_data: ErrorLogRequest,
    db: AsyncSession = Depends(get_db)
) -> ErrorLogResponse:
    """Log a new error (from Web UI)"""
    repo = PostgreSQLErrorLogRepository(db)
    error_log = await repo.log_or_increment(error_data.dict())
    return ErrorLogResponse.from_entity(error_log)
```

#### 4.2 Prompts API

```python
@router.get("/admin/prompts", response_model=list[PromptResponse])
async def list_prompts(db: AsyncSession = Depends(get_db)) -> list[PromptResponse]:
    """List all active prompts"""
    repo = PostgreSQLPromptRepository(db)
    prompts = await repo.find_active()
    return [PromptResponse.from_entity(p) for p in prompts]

@router.post("/admin/prompts")
async def update_prompt(
    prompt_data: PromptUpdateRequest,
    db: AsyncSession = Depends(get_db)
) -> PromptResponse:
    """Update prompt (creates new version)"""
    repo = PostgreSQLPromptRepository(db)
    prompt = await repo.create_version(
        prompt_id=prompt_data.id,
        updated_by=prompt_data.updated_by
    )
    return PromptResponse.from_entity(prompt)
```

---

### Phase 5: Prompt Editor UI実装

**目的**: Anthropic Context Engineering原則を実装したUI

#### 5.1 Prompt Editor Component

**ファイル**: `projects/nakamura-misaki/web-ui/src/app/prompts/page.tsx`

```typescript
// リアルタイムトークンカウンター
const [tokenCount, setTokenCount] = useState(0);

useEffect(() => {
  const count = estimateTokenCount(selectedPrompt?.system_prompt || '');
  setTokenCount(count);
}, [selectedPrompt?.system_prompt]);

// 明確性スコア分析
const analyzeClarityScore = async (prompt: string) => {
  const response = await fetch('/api/admin/prompts/analyze', {
    method: 'POST',
    body: JSON.stringify({ prompt }),
  });
  const { clarity_score } = await response.json();
  setClarityScore(clarity_score);
};
```

#### 5.2 Context Settings UI

**ファイル**: `web-ui/src/components/ContextSettingsPanel.tsx`

```typescript
<Card title="Context Optimization Settings">
  <Slider
    label="圧縮閾値（トークン数）"
    min={5000}
    max={15000}
    step={1000}
    value={contextSettings.compression_threshold}
    onChange={(val) => updateSettings({ compression_threshold: val })}
    helpText="Anthropic推奨: 8000トークン"
  />

  <RadioGroup
    label="要約強度"
    options={[
      { value: 'low', label: 'Low（詳細）' },
      { value: 'medium', label: 'Medium（推奨）' },
      { value: 'high', label: 'High（簡潔）' },
    ]}
    value={contextSettings.compression_strength}
    onChange={(val) => updateSettings({ compression_strength: val })}
  />
</Card>
```

---

### Phase 6: Context Compression実装

**目的**: 会話履歴の自動圧縮 + 構造化ノート

#### 6.1 Compression Service

**ファイル**: `src/contexts/conversations/domain/services/context_compressor.py`

```python
class ContextCompressor:
    """Anthropic推奨のコンテキスト圧縮"""

    async def compress_if_needed(self, conversation: Conversation) -> Conversation:
        """トークン数がしきい値を超えたら圧縮"""
        if conversation.token_count < self.threshold:
            return conversation

        # 1. 重要な決定・バグ情報を抽出してnotesに保存
        important_notes = await self._extract_important_notes(conversation)
        for note in important_notes:
            await self.notes_repo.create(note)

        # 2. Claude APIで要約生成
        summary = await self.claude_api.summarize(
            messages=conversation.messages,
            strength=self.compression_strength,
        )

        # 3. 圧縮ログ記録
        await self.compression_log_repo.create({
            "conversation_id": conversation.id,
            "original_token_count": conversation.token_count,
            "compressed_token_count": len(summary.split()),
            "summary": summary,
            "preserved_notes": [n.dict() for n in important_notes],
        })

        # 4. 新しいconversation作成（要約を冒頭に）
        new_conversation = Conversation(
            user_id=conversation.user_id,
            channel_id=conversation.channel_id,
            messages=[Message.system(summary)],
        )
        return await self.conversation_repo.create(new_conversation)
```

#### 6.2 構造化ノート抽出

```python
async def _extract_important_notes(self, conversation: Conversation) -> list[Note]:
    """Claude APIで重要情報を抽出"""
    prompt = f"""
以下の会話から、以下のカテゴリの重要情報を抽出してください：
- 重要な決定事項 (decision)
- バグ情報 (bug)
- 要件定義 (requirement)
- アーキテクチャ設計 (architecture)

会話:
{conversation.to_text()}
"""

    response = await self.claude_api.analyze(prompt)
    return [Note.from_json(item) for item in response["notes"]]
```

---

## 📊 実装優先度

| Phase | 実装内容 | 優先度 | 所要時間 |
|-------|---------|--------|---------|
| **1** | Mock削除 + 実DB接続 | 🔴 最優先 | 2-3時間 |
| **2** | Migration作成 | 🟡 高 | 1時間 |
| **3** | Repository実装 | 🟡 高 | 3-4時間 |
| **4** | API実装 | 🟡 高 | 2-3時間 |
| **5** | Prompt Editor UI | 🟢 中 | 4-5時間 |
| **6** | Context Compression | 🟢 低 | 3-4時間 |

**合計見積もり**: 15-20時間

---

## 🧪 テスト戦略

### Phase 1のテスト

```bash
# 1. ローカルビルド確認
cd projects/nakamura-misaki/web-ui
npm run build

# 2. API動作確認（本番環境）
curl https://home-lab-01.tail4ed625.ts.net:10000/api/tasks
curl https://home-lab-01.tail4ed625.ts.net:10000/api/users
curl https://home-lab-01.tail4ed625.ts.net:10000/api/sessions

# 3. Web UI動作確認
# https://home-lab-01.tail4ed625.ts.net:3002 にアクセス
# → Yahoo広告タスクが表示されることを確認
```

### Phase 2-4のテスト

```bash
# Migration実行確認
ssh home-lab-01 'psql -U nakamura_misaki -d nakamura_misaki -c "SELECT * FROM users LIMIT 1;"'
ssh home-lab-01 'psql -U nakamura_misaki -d nakamura_misaki -c "SELECT * FROM prompts LIMIT 1;"'

# API動作確認
curl https://home-lab-01.tail4ed625.ts.net:10000/api/admin/prompts
curl https://home-lab-01.tail4ed625.ts.net:10000/api/logs/errors
```

---

## 📝 ドキュメント更新ポリシー

**このドキュメントは実装の進捗に合わせて更新します**

### 更新タイミング

1. **設計変更時**: DB設計やAPI仕様が変わった場合
2. **Phase完了時**: 各Phaseの完了状況を記録
3. **問題発生時**: 予期しない問題と解決策を追記
4. **最適化実施時**: パフォーマンス改善やリファクタリング後

### 更新履歴

| 日付 | 変更内容 | 担当 |
|------|---------|------|
| 2025-10-23 | 初版作成 | Claude |
| - | - | - |

---

## 🚀 次のアクション

**Phase 1: Mock削除 + 実DB接続を開始します**

1. `webui.py` の書き換え
2. ローカルビルド確認
3. デプロイ + 動作確認

**準備完了後、実装を開始します。**
