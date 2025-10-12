# Nakamura-Misaki Project

汎用リマインダーサービス - マルチユーザー対応のスケジュール管理・通知システム

## 概要

Nakamura-Misakiは、複数ユーザーに対応した設定可能なリマインダーサービスです。REST API、Webhook、Slack連携を提供し、柔軟なスケジュール管理を実現します。

## 特徴

- 🌐 **マルチユーザー対応** - 複数ユーザーの個別設定管理
- 🚀 **REST API** - 豊富なAPIエンドポイント（10+）
- 🔗 **Webhook対応** - 外部サービスとの連携
- 💬 **Slack統合** - Slackボット機能とリマインダー送信
- 🤖 **Claude Code統合** - AI支援による開発サポート
- ⚙️ **設定駆動** - yamlファイルによる柔軟な設定管理

## 技術スタック

- **Python 3.12**: メインプログラミング言語
- **HTTP Server**: 標準ライブラリベースの軽量サーバー
- **APScheduler**: スケジュール管理（統合予定）
- **Slack API**: Webhook・リマインダー連携
- **Claude Code**: AI開発アシスタント
- **NixOS**: 宣言的サービス管理

## プロジェクト構造

```
nakamura-misaki/
├── src/                          # ソースコード
│   ├── simple_server.py         # メインHTTPサーバー
│   ├── claude_agent_simple.py   # Claude統合エージェント
│   ├── reminder_service.py      # リマインダーサービス
│   └── schedule_parser.py       # スケジュール解析
├── config/                      # 設定ファイル
│   ├── config.yaml             # メイン設定
│   └── users/                  # ユーザー別設定
├── data/                       # データファイル
│   └── schedules/              # スケジュールデータ
├── logs/                       # ログファイル
├── tests/                      # テストコード（将来）
├── .env                        # 環境変数
├── CLAUDE.md                   # プロジェクト指示書
└── README.md                   # このファイル
```

## インストール・起動

### システム要件

- NixOS環境
- Python 3.12+
- Slack API トークン
- Claude Code CLI

### 環境設定

1. 環境変数ファイル作成:
```bash
cp .env.template .env
# .envファイルを編集してSlackトークンを設定
```

2. 必要ディレクトリ作成:
```bash
mkdir -p data/schedules logs config/users
```

### 起動方法

#### NixOS サービス（推奨）
```bash
# 宣言的設定でサービス有効化
sudo nixos-rebuild switch --flake ~/nixos-config
```

#### 直接起動（開発時）
```bash
cd /home/noguchilin/projects/nakamura-misaki
python3 src/simple_server.py
```

### 動作確認

```bash
# ヘルスチェック
curl http://localhost:8010/

# API動作確認
curl http://localhost:8010/api/schedules

# Slack連携確認（Tailscale Funnel使用）
# https://[your-tailscale-hostname]:8010/webhook/slack
```

## API エンドポイント

### 基本情報
- `GET /` - サービス状態確認
- `GET /health` - ヘルスチェック

### スケジュール管理
- `GET /api/schedules` - 全スケジュール取得
- `GET /api/schedules/today` - 今日の予定
- `GET /api/schedules/upcoming` - 今後の予定
- `POST /api/schedules` - スケジュール追加

### リマインダー操作
- `POST /api/reminders/send` - 手動リマインダー送信
- `POST /api/reminders/quick` - クイック送信
- `POST /api/reminders/check` - 即時チェック

### Claude統合
- `POST /api/claude/chat` - Claude Code連携チャット

### Webhook
- `POST /webhook/slack` - Slack Webhook受信

## 設定

### メイン設定（config/config.yaml）
```yaml
service:
  name: "Nakamura-Misaki"
  port: 8010
  debug: false

slack:
  webhook_url: "https://hooks.slack.com/..."
  default_channel: "#general"

schedule:
  timezone: "Asia/Tokyo"
  reminder_advance: 300  # 5分前
```

### ユーザー設定（config/users/[user_id].yaml）
```yaml
user_id: "U1234567890"
name: "ユーザー名"
timezone: "Asia/Tokyo"
notification:
  slack_channel: "#reminders"
  advance_minutes: [10, 5]
schedules:
  - name: "定期ミーティング"
    time: "10:00"
    days: ["Monday", "Wednesday"]
```

## Slack連携

### ボット設定

1. Slack Appを作成
2. 以下の権限を追加:
   - `chat:write`
   - `channels:read`
   - `users:read`

3. Webhook URLを設定:
   ```
   https://[your-tailscale-hostname]:8010/webhook/slack
   ```

### 対応コマンド

- `こんにちは` - 基本応答
- Claude Code連携コマンド - AI支援機能

## 開発

### コード規約

- **命名規則**: snake_case（Python標準）
- **型ヒント**: 可能な限り型アノテーション使用
- **ドキュメント**: docstringで関数説明
- **エラーハンドリング**: 適切な例外処理

### 開発ガイドライン

1. **設定駆動**: ハードコードを避ける
2. **汎用性重視**: 特定ユーザー専用にしない
3. **API ファースト**: REST APIを中心とした設計
4. **拡張可能**: 新機能追加しやすい設計

### テスト

```bash
# 基本テスト
python3 src/reminder_service.py --test

# サーバーテスト
curl -X POST http://localhost:8010/api/reminders/check
```

## 運用

### ログ確認

```bash
# サービスログ
sudo journalctl -u nakamura-misaki.service -f

# アプリケーションログ
tail -f logs/app.log
```

### トラブルシューティング

#### サービス起動しない
1. 設定ファイル確認
2. 環境変数確認
3. ポート競合確認

#### Slack連携エラー
1. トークン確認
2. 権限確認
3. Webhook URL確認

#### Claude Code連携エラー
1. Claude CLI設定確認
2. PATH設定確認
3. 認証状態確認

## ロードマップ

### v2.1 (計画中)
- [ ] APScheduler本格統合
- [ ] データベース連携（SQLite）
- [ ] Web UI（Next.js）

### v2.2 (将来)
- [ ] Discord通知対応
- [ ] Email通知対応
- [ ] 認証システム
- [ ] マルチテナント対応

### v3.0 (構想)
- [ ] 機械学習によるスケジュール最適化
- [ ] カレンダー連携（Google Calendar, Outlook）
- [ ] モバイルアプリ

## ライセンス

MIT License

## 関連プロジェクト

- **mementomoris**: 元となった個人向けプロジェクト
- **dashboard**: 統合ダッシュボード（連携予定）

## 貢献

1. Issueを作成
2. Feature branchを作成
3. 変更を実装
4. Pull Requestを作成

## サポート

- 技術的な質問: プロジェクトIssues
- バグ報告: プロジェクトIssues
- Claude Code統合: AI支援機能を活用

---

*このプロジェクトはmementomorisから派生した汎用版として、Claude Code統合により開発効率を向上させています。*