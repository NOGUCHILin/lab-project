# Phase 1: Specify - Context基盤構築

**nakamura-misaki v6.0.0 - Phase 1実装の仕様定義**

---

## 🎯 プロジェクト概要

### 背景

nakamura-misaki v5.1.0は個人タスク管理AIアシスタント（Slack Bot）として動作している。
今後、業務タスク管理機能（staff-task-system）を統合するため、
**DDD Bounded Context + Clean Architecture**による再構築が必要。

Phase 1では、既存コードをBounded Context構造に移行し、将来の拡張に備える。

### ビジョン

- **保守性**: ドメインが明確に分離され、変更の影響範囲が限定される
- **拡張性**: 新しいContextを追加しやすい構造
- **テスト容易性**: 各層が独立しており、テストが書きやすい
- **一貫性**: アーキテクチャパターンが統一されている

---

## 📖 Feature 1: Personal Tasks Context移行

### User Story

```
As a: システム開発者
I want to: 既存のnakamura-misakiコードをBounded Context構造に移行したい
So that: 将来の機能拡張（Work Tasks統合）に備えられる
```

### Why（なぜこの機能が必要か）

1. **現状の問題点**
   - 既存コードは単一の`src/`ディレクトリに全て配置されている
   - ドメイン境界が不明確
   - 新しいContext（Work Tasks）を追加する余地がない

2. **解決策**
   - DDD Bounded Contextパターンを適用
   - `contexts/personal_tasks/`として分離
   - Clean Architecture 4層構造を明確化

3. **期待される効果**
   - ドメインの独立性向上
   - テストの書きやすさ向上
   - 将来のWork Tasks追加が容易に

---

## ✅ Acceptance Criteria（受け入れ基準）

### 1. ディレクトリ構造の移行

**Given**: 既存の`src/`ディレクトリにコードが配置されている

**When**: Phase 1実装完了後

**Then**: 以下のディレクトリ構造になっている

```
nakamura-misaki/
├── src/
│   ├── contexts/
│   │   └── personal_tasks/
│   │       ├── domain/
│   │       │   ├── models/
│   │       │   │   ├── task.py
│   │       │   │   └── conversation.py
│   │       │   ├── repositories/
│   │       │   │   ├── task_repository.py
│   │       │   │   └── conversation_repository.py
│   │       │   └── services/
│   │       │       └── claude_agent_service.py
│   │       │
│   │       ├── application/
│   │       │   ├── use_cases/
│   │       │   │   ├── register_task.py
│   │       │   │   ├── complete_task.py
│   │       │   │   ├── update_task.py
│   │       │   │   └── query_user_tasks.py
│   │       │   └── dto/
│   │       │       └── task_dto.py
│   │       │
│   │       ├── adapters/
│   │       │   ├── primary/
│   │       │   │   ├── api/
│   │       │   │   │   └── routes/
│   │       │   │   │       └── slack.py
│   │       │   │   ├── slack_event_handler.py
│   │       │   │   └── tools/
│   │       │   │       └── task_tools.py
│   │       │   └── secondary/
│   │       │       ├── postgresql_task_repository.py
│   │       │       └── postgresql_conversation_repository.py
│   │       │
│   │       └── infrastructure/
│   │           ├── di_container.py
│   │           ├── database.py
│   │           └── config.py
│   │
│   └── shared_kernel/
│       ├── domain/
│       │   └── value_objects/
│       │       ├── user_id.py
│       │       └── task_status.py
│       └── infrastructure/
│           ├── claude_client.py
│           └── slack_client.py
│
└── tests/
    ├── unit/
    │   ├── personal_tasks/
    │   │   ├── domain/
    │   │   ├── application/
    │   │   └── adapters/
    │   └── shared_kernel/
    └── integration/
        └── personal_tasks/
```

**検証方法**:
- [ ] `find src/ -name "*.py" | wc -l` でファイル数が変わらない
- [ ] 全ファイルが新構造に配置されている

---

### 2. 既存機能の維持

**Given**: nakamura-misaki v5.1.0が稼働している

**When**: Phase 1実装完了後

**Then**: 以下の全機能が正常動作する

#### 2.1 タスク作成機能
```
ユーザー: 「明日までにレポート書く」
Bot: タスクを登録しました
- ID: xxx
- タイトル: レポート書く
- 期限: 2025-10-17
```

**検証**:
- [ ] Slack Botにメッセージ送信
- [ ] タスクがDBに保存される
- [ ] 応答メッセージが返る

#### 2.2 タスク完了機能
```
ユーザー: 「レポート終わった」
Bot: タスクを完了にしました
```

**検証**:
- [ ] タスクステータスが"completed"になる
- [ ] completed_atが記録される

#### 2.3 タスク一覧機能
```
ユーザー: 「今日のタスク」
Bot: 今日のタスク:
- [ ] レポート書く（期限: 明日）
```

**検証**:
- [ ] 未完了タスク一覧が表示される
- [ ] 期限順にソートされる

#### 2.4 タスク更新機能
```
ユーザー: 「レポートの期限を明後日にして」
Bot: 期限を更新しました
```

**検証**:
- [ ] タスクの期限が変更される
- [ ] updated_atが更新される

#### 2.5 AI Agent機能
```
ユーザー: 「タスクの状況教えて」
Bot: （AI判断でquery_user_tasks Toolを呼び出す）
```

**検証**:
- [ ] Claude APIが正常動作
- [ ] Tool呼び出しが成功
- [ ] 会話履歴が保存される

---

### 3. トークン消費量の維持

**Given**: v5.1.0のトークン消費量は約1800 tokens

**When**: Phase 1実装完了後

**Then**:
- [ ] トークン消費量が1800±100 tokens の範囲内
- [ ] System Promptが変更されていない
- [ ] Tool定義が変更されていない

**検証方法**:
```bash
# 本番環境でメッセージ送信
# ログからトークン消費量を確認
grep "input_tokens" /var/log/nakamura-misaki/app.log
```

---

### 4. テストカバレッジ

**Given**: 既存コードにテストが不足している

**When**: Phase 1実装完了後

**Then**:
- [ ] Domain層のカバレッジ80%以上
- [ ] Application層のカバレッジ70%以上
- [ ] 全テストがパスする

**検証方法**:
```bash
uv run pytest --cov=src --cov-report=term-missing
```

---

### 5. 依存性の方向

**Given**: Clean Architectureを採用する

**When**: Phase 1実装完了後

**Then**: 依存性の方向が以下の通りになっている

```
Adapters/Infrastructure
    ↓ (依存)
Application
    ↓ (依存)
Domain（誰にも依存しない）
```

**検証方法**:
- [ ] Domain層が他層のimportを含まない
- [ ] Application層がAdapters/Infrastructureをimportしていない
- [ ] DIContainerでのみ依存性注入が行われる

---

### 6. デプロイの成功

**Given**: NixOS本番環境で稼働している

**When**: Phase 1実装完了後

**Then**:
- [ ] GitHub ActionsでビルドとテストがパスNixOSにデプロイ成功
- [ ] サービスが正常起動
- [ ] Slack Botが応答する

**検証方法**:
```bash
# 本番環境で確認
ssh home-lab-01
systemctl status nakamura-misaki-api.service
journalctl -u nakamura-misaki-api.service -n 50
```

---

## 📊 成功の定義（Definition of Success）

Phase 1が成功したと判断する基準：

### 必須条件（Must Have）
- ✅ 全Acceptance Criteriaが満たされている
- ✅ 既存機能が全て正常動作する
- ✅ 全テストがパスする
- ✅ 本番環境にデプロイ成功

### 推奨条件（Should Have）
- ✅ トークン消費量が増加していない
- ✅ テストカバレッジが向上している
- ✅ コードの可読性が向上している

### オプション条件（Nice to Have）
- ✅ パフォーマンスが改善している
- ✅ ドキュメントが充実している

---

## 🚫 Non-Goals（対象外）

Phase 1では以下は**実装しない**：

- ❌ Work Tasks Contextの実装
- ❌ Anti-Corruption Layerの実装
- ❌ 新機能の追加
- ❌ パフォーマンス最適化
- ❌ UI/UXの変更
- ❌ データベーススキーマの変更

これらはPhase 2以降で実装する。

---

## 📈 成功指標（Success Metrics）

Phase 1完了後に測定する指標：

| 指標 | 目標値 | 測定方法 |
|------|-------|---------|
| **テスト実行時間** | 5秒以内 | `time uv run pytest` |
| **ビルド時間** | 3分以内 | GitHub Actions実行時間 |
| **デプロイ時間** | 5分以内 | NixOS再ビルド時間 |
| **レスポンス時間** | 3秒以内 | Slack Bot応答時間 |
| **トークン消費量** | 1800±100 | Claude APIログ |
| **テストカバレッジ** | 75%以上 | pytest-cov |

---

## 🎯 Phase 1完了の判定基準

以下の全てを満たした時点でPhase 1完了とする：

1. ✅ **全Acceptance Criteriaが満たされている**
   - ディレクトリ構造が正しい
   - 既存機能が全て動作
   - トークン消費量が維持されている
   - テストカバレッジが目標達成
   - 依存性の方向が正しい
   - デプロイ成功

2. ✅ **全テストがパスする**
   - Unit Tests: 100%パス
   - Integration Tests: 100%パス
   - E2E Tests（手動）: 全シナリオ成功

3. ✅ **本番環境で正常動作**
   - サービス起動成功
   - Slack Botが応答
   - エラーログなし

4. ✅ **ドキュメント更新完了**
   - INTEGRATION_PLAN.md更新
   - Phase 1実装記録作成
   - 次のPhaseへの引き継ぎ事項記載

---

## 📝 次のステップ

Phase 1完了後：
1. Phase 1実装記録を作成
2. Phase 2: Planの作成に進む
3. Work Tasks Context実装の準備

---

**作成日**: 2025-10-16
**作成者**: Claude Code
**レビュー**: 野口凜
**ステータス**: Draft → Review中
