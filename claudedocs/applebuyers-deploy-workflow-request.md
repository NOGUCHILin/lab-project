# デプロイワークフローの追加依頼

## 背景・目的

現在、NixOS サーバー上でプレビュー環境を運用しています。別ホスト（ローカル開発環境など）から `main` ブランチに push した際、NixOS サーバー側のコードが自動更新されず、プレビュー環境と不整合が発生します。この問題を解決するため、自動デプロイワークフローを追加してください。

## プロジェクト構成

**モノレポ構成**:
```
applebuyers_application/          # リポジトリルート
├── public-site/                  # Next.js 公開サイト（記事サイト）← 対象
│   ├── content/                  # 記事ファイル
│   └── ...
├── podman-compose.yml
└── .env
```

**対象プロジェクト**: `public-site/` ディレクトリ（Next.js 公開サイト）

## 現在のブランチ運用

### main ブランチ
- **役割**: 本番環境用ブランチ
- **リモート push**: あり
- **デプロイ先**: Vercel（本番サイト）
- **トリガー**: main への push で Vercel デプロイが自動実行

### content-draft ブランチ
- **役割**: 記事作成・プレビュー専用ブランチ（ローカル専用）
- **リモート push**: なし（リモートには push しない）
- **使用場所**: NixOS サーバー上のみ
- **目的**: ライターが記事を書く作業ブランチ

## NixOS サーバー環境

### プレビューサイト
- **URL**: `https://home-lab-01.tail4ed625.ts.net:13006`
- **表示ブランチ**: content-draft（作業中の記事 + 最新の開発コード）
- **サービス名**: `applebuyers-site.service`
- **プロジェクトパス**: `~/projects/applebuyers_application/public-site`（モノレポ内のサブディレクトリ）

### コードサーバー（2種類）
1. **ライター用**: content-draft ブランチ、`public-site/content/` ディレクトリのみ表示、Git 操作なし
2. **開発用**: main ブランチ、`public-site/` フルプロジェクト、Git 操作専用（commit/merge/push）

## 作業フロー

### エンジニアによる開発
1. ローカルまたは NixOS サーバーで開発
2. main ブランチに commit & push（リモート）
3. **Vercel デプロイ自動実行**
4. **【問題】NixOS サーバーの main が古いまま**
5. **【問題】content-draft も古い main ベースのまま → ライターが古いコードでプレビュー**

### ライターによる記事作成
1. NixOS サーバーのライター用コードサーバーで記事作成（content-draft、`public-site/content/` 配下）
2. エンジニアがプレビュー確認
3. OK なら content-draft → main にマージ（開発用コードサーバーで操作）
4. main を push（リモート）
5. **Vercel デプロイ自動実行**
6. **【問題】NixOS サーバーの content-draft が古いまま → 次の記事作成時に不整合**

## 必要な実装

### デプロイワークフローの追加

**トリガー**: main ブランチへの push

**処理内容**:
1. Vercel デプロイ（既存、変更なし）
2. NixOS サーバーで以下を実行:
   ```bash
   cd ~/projects/applebuyers_application/public-site
   git fetch origin
   git checkout main
   git pull origin main
   git checkout content-draft
   git merge main --no-edit --strategy-option theirs  # コンフリクト時は main 優先
   sudo systemctl restart applebuyers-site.service
   ```

**期待される結果**:
- NixOS サーバーの main ブランチが常に最新
- content-draft ブランチも常に最新の開発コード + 作業中の記事
- プレビューサイトが常に最新状態

### 技術仕様

#### 接続情報
- **NixOS サーバーホスト**: `home-lab-01.tail4ed625.ts.net`
- **SSH 接続方法**: Tailscale 経由（`ssh nixos`）
- **Tailscale 認証**: OAuth（既存の lab-project リポジトリと同じ認証情報を使用）

#### 必要な GitHub Secrets
以下のシークレットを設定済みと想定してください（未設定の場合は通知してください）:
- `TS_OAUTH_CLIENT_ID`: Tailscale OAuth クライアント ID
- `TS_OAUTH_SECRET`: Tailscale OAuth シークレット

#### ワークフローファイル
`.github/workflows/deploy-preview.yml` を作成してください。

#### 実装時の注意点
1. **作業ディレクトリ**: リポジトリルートではなく `public-site/` ディレクトリで Git 操作を実行
2. **マージコンフリクト対応**: content-draft への main マージ時にコンフリクトが発生する可能性があります。コンフリクト時は `--strategy-option theirs` で main を優先してください。
3. **ブランチ状態確認**: マージ前に content-draft の状態を確認し、未コミットの変更がある場合はスキップまたはエラー通知してください。
4. **サービス再起動**: `systemctl restart` は sudo 権限が必要ですが、NixOS サーバー側で権限設定済みです。

## 実装後の確認項目

1. main ブランチに push → GitHub Actions が起動
2. NixOS サーバーで確認:
   ```bash
   cd ~/projects/applebuyers_application/public-site
   git log main --oneline -5       # main が最新
   git log content-draft --oneline -5  # main の変更がマージされている
   ```
3. プレビューサイト（`https://home-lab-01.tail4ed625.ts.net:13006`）で最新コードが反映されている

---

以上の内容で、デプロイワークフローを実装してください。不明点があれば質問してください。
