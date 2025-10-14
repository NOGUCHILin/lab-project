# nakamura-misaki 実装計画

**更新日**: 2025-10-13
**ステータス**: 技術選定中

---

## 🎯 プロジェクト概要

### nakamura-misakiとは
チームに加わったばかりの新人社員として振る舞うAIエージェント。
タスク管理・引き継ぎ管理・リマインダー・社内情報管理を担当する。

### 人格設定
- **ベース**: 攻殻機動隊の草薙素子少佐
- **立場**: 新入り（謙虚だが的確）
- **性格**: 冷静、論理的、無駄がない、間違いは指摘する

---

## 📋 要件定義

### 朝の業務
1. 各メンバーの昨日までの進捗確認
2. 今日のタスク割り当ての最適化
3. 優先度の見直し提案
4. マネージャーへの日次レポート作成

### タスク対応
- **自分でできるタスク**: そのまま実行
- **他メンバーが担当すべきタスク**: 最適な担当者にアサイン + 理由を説明

### 引き継ぎ管理
- 数日かかるプロジェクトの進捗を可視化
- 担当者変更時に詳細な引き継ぎドキュメントを自動生成
- 「どこまで完了したか」「次に何をすべきか」を明確化

### 社内情報管理
- プロジェクトドキュメントの管理
- 過去の類似タスク検索
- 設計決定の記録

---

## 🏗️ アーキテクチャ設計

### ハイブリッド型情報管理

#### 1. 構造化データ（Database）
**用途**: タスク、引き継ぎ、メンバー情報、リマインダー

**候補技術**:
- ✅ PostgreSQL（検討中）
- ⏳ SQLite（検討中）
- ⏳ Redis（検討中）

**テーブル設計案**:
```sql
-- タスク管理
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL, -- 'todo', 'in_progress', 'review', 'done'
    assignee_id TEXT NOT NULL,
    priority INTEGER DEFAULT 3, -- 1(高) to 5(低)
    due_date TIMESTAMP,
    dependencies TEXT[], -- 依存するタスクIDの配列
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 引き継ぎ管理
CREATE TABLE handoffs (
    id UUID PRIMARY KEY,
    project_name TEXT NOT NULL,
    from_user TEXT NOT NULL,
    to_user TEXT NOT NULL,
    progress_percentage INTEGER DEFAULT 0,
    status TEXT NOT NULL, -- 'active', 'completed'
    summary TEXT,
    next_actions TEXT,
    document_path TEXT, -- Markdownドキュメントへのパス
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- メンバー情報
CREATE TABLE members (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT, -- 'engineer', 'designer', 'manager', etc.
    skills TEXT[], -- スキルセット
    availability TEXT DEFAULT 'available', -- 'available', 'busy', 'leave'
    created_at TIMESTAMP DEFAULT NOW()
);

-- リマインダー
CREATE TABLE reminders (
    id UUID PRIMARY KEY,
    target_user TEXT NOT NULL,
    message TEXT NOT NULL,
    remind_at TIMESTAMP NOT NULL,
    status TEXT DEFAULT 'pending', -- 'pending', 'sent', 'cancelled'
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 2. 非構造化データ（Markdown + Vector DB）
**用途**: プロジェクトドキュメント、引き継ぎ詳細、設計決定

**候補技術**:
- ✅ Markdown（確定）
- ⏳ Supabase pgvector（検討中）
- ⏳ 専用Vector DB（検討中）

**ディレクトリ構造**:
```
.nakamura_knowledge/
├── projects/
│   ├── project_a.md
│   └── project_b.md
├── handoffs/
│   ├── 2025-10-13_project_a_handoff.md
│   └── 2025-10-12_project_b_handoff.md
└── decisions/
    └── 2025-10_architecture_decisions.md
```

#### 3. Anthropic Structured Note-Taking（実装済み）
```
.nakamura_notes/
├── code_changes/
├── decisions/
├── todos/
├── errors/
└── learnings/
```

---

## 🧠 System Prompt設計

### v4.0.0: 新人・草薙素子ver

**主要な変更点**:
1. 人格設定を草薙素子ベースに変更
2. 意見・反論・提案の基準を明確化
3. タスク管理・引き継ぎ管理の責務を追加
4. 動的変数を拡張（`{today_tasks}`, `{pending_handoffs}`, `{team_status}`）

**詳細**: [default.json](../config/prompts/default.json)（実装予定）

---

## 📊 実装フェーズ

### Phase 1: データベース設計・実装
**目的**: 構造化データの永続化基盤を構築

**タスク**:
- [ ] 技術選定（PostgreSQL vs SQLite vs Redis）
- [ ] NixOS configuration更新
- [ ] テーブル設計・マイグレーション
- [ ] Pythonアダプター実装
- [ ] テストデータ投入

**期間**: TBD

---

### Phase 2: System Prompt刷新
**目的**: 草薙素子ベースの人格を実装

**タスク**:
- [ ] [default.json](../config/prompts/default.json) v4.0.0作成
- [ ] 動的変数追加（`{today_tasks}`, `{pending_handoffs}`, `{team_status}`）
- [ ] [claude_adapter.py](../src/adapters/secondary/claude_adapter.py) 変数置換ロジック拡張
- [ ] Slackでの対話テスト

**期間**: TBD

---

### Phase 3: タスク管理機能
**目的**: タスク割り当て・引き継ぎ生成機能の実装

**タスク**:
- [ ] タスク割り当てAPI（`POST /api/tasks/assign`）
- [ ] 引き継ぎ生成API（`POST /api/handoffs/generate`）
- [ ] 日次レポートAPI（`GET /api/reports/daily`）
- [ ] リマインダー実行ジョブ（RQ Worker）
- [ ] admin-uiからのタスク管理画面

**期間**: TBD

---

### Phase 4: Vector DB統合
**目的**: 意味検索でプロジェクトドキュメントを活用

**タスク**:
- [ ] 技術選定（Supabase pgvector vs 専用Vector DB）
- [ ] ドキュメントのベクトル化パイプライン
- [ ] 類似タスク検索機能
- [ ] RAG統合（Anthropic Context Engineering）

**期間**: TBD

---

## 🔧 技術選定（検討中）

### 1. データベース選定

| 選択肢 | メリット | デメリット | 推奨度 |
|--------|----------|------------|--------|
| **PostgreSQL** | ・トランザクション信頼性<br>・複雑なクエリ対応<br>・pgvectorでVector DB統合可能 | ・運用コスト<br>・NixOS設定が必要 | ⭐⭐⭐⭐⭐ |
| **SQLite** | ・軽量<br>・設定不要<br>・ファイルベース | ・並行書き込み制約<br>・Vector DB統合不可 | ⭐⭐⭐ |
| **Redis** | ・高速<br>・RQ Workerと統合済み | ・永続化に工夫が必要<br>・複雑なクエリ不向き | ⭐⭐ |

**決定**: ✅ **PostgreSQL** - pgvectorでVector DB統合、複雑なクエリ対応

---

### 2. Vector DB選定

| 選択肢 | メリット | デメリット | 推奨度 |
|--------|----------|------------|--------|
| **Supabase pgvector** | ・PostgreSQLと統合<br>・既存インフラ活用 | ・パフォーマンス制約あり | ⭐⭐⭐⭐⭐ |
| **専用Vector DB**<br>(Pinecone/Weaviate) | ・高性能<br>・スケーラブル | ・追加コスト<br>・運用複雑化 | ⭐⭐⭐ |

**決定**: ✅ **Supabase pgvector** - PostgreSQLと統合、追加インフラ不要

---

### 3. 実装順序

| 選択肢 | メリット | デメリット | 推奨度 |
|--------|----------|------------|--------|
| **Phase 0→1→2→3→4** | ・リスク低い<br>・段階的検証 | ・時間がかかる | ⭐⭐⭐⭐⭐ |
| **並行実装** | ・速い<br>・効率的 | ・リスク高い<br>・統合が複雑 | ⭐⭐⭐ |

**決定**: ✅ **Phase 0から順番実装** - System Prompt刷新→DB→機能→Vector DB

---

### 4. System Prompt先行実装

| 選択肢 | メリット | デメリット | 推奨度 |
|--------|----------|------------|--------|
| **先に刷新（Phase 0）** | ・人格テスト可能<br>・フィードバック早い | ・機能はまだ使えない | ⭐⭐⭐⭐⭐ |
| **後回し** | ・機能完成後に調整 | ・人格のミスマッチリスク | ⭐⭐ |

**決定**: ✅ **Phase 0として先に刷新** - 人格テストを最優先

---

## 📝 次のアクション

1. **技術選定会議**: 上記4つの選択肢を決定
2. **実装開始**: 決定事項を反映してPhase開始
3. **ドキュメント更新**: 進捗に応じて本ドキュメントを更新

---

## 📚 参考資料

- [Anthropic Context Engineering Best Practices](https://docs.anthropic.com/)
- [nakamura-misaki Phase 3実装履歴](https://github.com/NOGUCHILin/lab-project/commit/9272926)
- [2025年10月時点のAIエージェント情報管理ベストプラクティス](調査済み・Gemini経由)
