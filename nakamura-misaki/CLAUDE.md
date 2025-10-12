# Nakamura-Misaki Project Assistant

あなたはNakamura-Misakiプロジェクトの開発アシスタントです。
このプロジェクトは汎用リマインダーサービスとして、複数ユーザーに対応した設定可能なシステムです。

## プロジェクト概要
- **目的**: 汎用的なスケジュールリマインダーサービス
- **技術スタック**: Python, FastAPI, APScheduler
- **特徴**: マルチユーザー対応、REST API、Webhook対応

## 開発ガイドライン

### アーキテクチャ原則
- **設定駆動**: ハードコードを避け、config.yamlで管理
- **汎用性重視**: 特定ユーザー専用にしない
- **拡張可能**: 新機能を追加しやすい設計
- **API ファースト**: REST APIを中心とした設計

### コード規約
- **命名規則**: snake_case（Python標準）
- **型ヒント**: 可能な限り型アノテーションを使用
- **ドキュメント**: docstringで関数の説明を記載
- **エラーハンドリング**: 適切な例外処理

## ディレクトリ構造
```
nakamura-misaki/
├── src/               # ソースコード
│   ├── main*.py      # FastAPIアプリケーション
│   ├── *_service.py  # サービスロジック
│   └── *_parser.py   # パーサーモジュール
├── config/           # 設定ファイル
├── data/            # データファイル
└── tests/           # テストコード（将来）
```

## 主要機能

### 現在実装済み
- ✅ マルチユーザー対応
- ✅ REST API (10+ エンドポイント)
- ✅ Webhook受信
- ✅ スケジュール解析
- ✅ Slackリマインダー送信

### 今後の拡張予定
- [ ] APScheduler本格統合
- [ ] Next.js Web UI
- [ ] Discord/Email通知
- [ ] データベース連携
- [ ] 認証システム

## API エンドポイント

### スケジュール管理
- `GET /api/schedules` - スケジュール一覧
- `GET /api/schedules/today` - 今日の予定
- `GET /api/schedules/upcoming` - 今後の予定

### リマインダー操作
- `POST /api/reminders/send` - 手動送信
- `POST /api/reminders/quick` - クイック送信
- `POST /api/reminders/check` - 即時チェック

### Webhook
- `POST /webhook/slack` - Slackイベント受信

## テスト方法
```bash
# 基本テスト
python3 src/reminder_service.py --test

# サーバー起動
python3 src/simple_server.py

# API テスト
curl http://localhost:8010/api/schedules
```

## 注意事項
- **環境変数**: `.env`ファイルでSlackトークンを管理
- **ポート**: 8000-8010の範囲で動作
- **依存関係**: 標準ライブラリのみ（uvicorn不要版あり）

## AIアシスタントへの指示

### やるべきこと
- コードの汎用性を保つ
- 設定ファイルで柔軟に対応
- APIドキュメントを充実させる
- エラーメッセージを分かりやすく

### やってはいけないこと
- 特定ユーザー向けのハードコード
- 設定なしで動かない実装
- セキュリティを無視した実装
- テストなしでの大規模変更

## 関連プロジェクト
- **mementomoris**: 元となった個人向けプロジェクト
- **dashboard**: 統合ダッシュボード（連携予定）

---
*このプロジェクトはmementomorisから派生した汎用版です。*