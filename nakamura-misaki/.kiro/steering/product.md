# Product: nakamura-misaki v4.0.0

## Product Vision

nakamura-misakiは、Slackワークスペース内で活動する**仮想チームメンバー**です。従来のSlack Botとは異なり、ユーザートークンを使用して人間の従業員と同じレベルで振る舞います。

### Core Identity

- **Name**: 中村美咲（Nakamura Misaki）
- **Personality**: 攻殻機動隊の草薙素子少佐（新人バージョン）
  - 冷静、論理的、無駄がない
  - 的確な指摘をする
  - 間違いは指摘し、代替案を提示
  - 謙虚だが確実
- **Role**: Task Manager & Information Hub

## Target Users

### Primary Users
- **開発チームメンバー**: タスク管理・ハンドオフ・リマインダーを必要とする
- **プロジェクトマネージャー**: チームの状況把握・タスク割り当て

### User Scenarios

#### Scenario 1: Morning Task Assignment
**User**: Project Manager
**Need**: 今日のチーム全員のタスクを一括割り当て

```
PM: @中村美咲 今日のタスク割り当て
nakamura-misaki:
  ✅ タスク割り当て完了
  - @野口凜: API統合テスト (期限: 15:00)
  - @田中太郎: ドキュメント更新 (期限: 18:00)
  - @佐藤花子: UI改善レビュー (期限: 16:00)
```

#### Scenario 2: Task Handoff
**User**: Developer
**Need**: 作業途中でタスクを次の人に引き継ぎ

```
Developer: @中村美咲 「API統合」のタスク、明日から田中さんに引き継ぎ
nakamura-misaki:
  📝 ハンドオフ登録完了

  引き継ぎ内容:
  - タスク: API統合テスト
  - 担当: 野口凜 → 田中太郎
  - 開始予定: 明日 9:00
  - 現在の進捗: 認証部分完了、決済API未実装

  明日朝8:50に @田中太郎 にリマインダー送信します。
```

#### Scenario 3: Internal Information Query
**User**: Team Member
**Need**: 過去の決定事項を確認

```
User: @中村美咲 先週のDB移行の決定事項は？
nakamura-misaki:
  📖 過去のノートから検索しました

  【2025-10-07の決定事項】
  - DB: PostgreSQL 16
  - Vector DB: Supabase pgvector
  - 移行日: 2025-10-15（月）
  - 担当: 野口凜

  詳細が必要な場合はお知らせください。
```

## Key Features

### v4.0.0 Core Features

#### 1. Task Management
- タスク登録・更新・削除
- 期限管理・リマインダー
- 進捗トラッキング
- チーム全体のタスク一覧表示

#### 2. Handoff Management
- 作業引き継ぎの記録
- 次の担当者へのリマインダー
- 進捗状況の引き継ぎ
- 多日にわたるプロジェクトの管理

#### 3. Internal Information Management
- 決定事項の記録（Anthropic Structured Note-Taking）
- 過去のノートからの検索
- セッション間での記憶保持
- 自然言語での情報検索

#### 4. Team Hub
- チーム全体の状況把握
- メンバー別タスク一覧
- 今日のタスク・明日のタスク
- ボトルネックの検出

### What nakamura-misaki is NOT

❌ **Technical Support Bot**: コードレビュー・バグ修正は行わない
❌ **Code Execution**: コード実行環境は持たない
❌ **External Tool Integration**: 外部API連携は最小限（Slack/Claude のみ）
❌ **Passive Bot**: 指示待ちではなく、問題を指摘し代替案を提示

## Success Metrics

### v4.0.0 Launch Criteria

1. **Task Management**:
   - タスク登録・更新・削除が正常動作
   - 期限リマインダーが時間通りに送信される
   - チーム全体のタスク一覧が正確に表示される

2. **Handoff Management**:
   - ハンドオフ登録が記録される
   - 次の担当者へのリマインダーが送信される
   - 進捗情報が引き継がれる

3. **Personality Test**:
   - 草薙素子風の応答スタイルが実現されている
   - 間違いを指摘し代替案を提示する
   - 無駄な前置きなく的確に応答する

4. **Information Retrieval**:
   - 過去のノートから情報検索できる
   - セッション間で記憶が保持される

## Future Roadmap (v5.0+)

- **Multi-workspace Support**: 複数のSlackワークスペース対応
- **Custom Personality**: ユーザーごとの性格カスタマイズ
- **Advanced Analytics**: タスク完了率・ボトルネック分析
- **External Integrations**: GitHub Issues, Notion, Linear等との連携
