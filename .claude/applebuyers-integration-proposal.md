# AppleBuyers Public Site統合提案

**日付**: 2025-10-07
**提案者**: noguchilin
**目的**: applebuyers_application/public-siteをlab-projectで管理し、ライター向けcode-server環境を提供

---

## 📋 背景・課題

### 現状
- **applebuyers_application**: 別管理のモノレポ（admin-app, api-service, public-site含む）
- **public-site**: Next.js 15で構築された公開買取サイト
- **ライター要件**:
  - 非エンジニアが記事（Markdown）を作成
  - code-serverで編集
  - `yarn dev`でリアルタイムプレビュー（ポート13005）
  - 画像アップロード（ドラッグ&ドロップ）

### 課題
- public-siteだけをNixOSに配置したい
- lab-projectの統一管理に組み込みたい
- 元リポジトリ（applebuyers_application）との同期が必要
- できるだけシンプルな構成にしたい

---

## 💡 検討中の実装案

### 案1: Git Submodule + Sparse Checkout
```
lab-project/
└── projects/
    └── applebuyers-public-site/     # Git submodule
        └── public-site/              # sparse-checkout
            ├── content/articles/     # ライターが編集
            ├── src/
            ├── package.json
            └── service.nix
```

**メリット**:
- ✅ lab-projectで統一管理
- ✅ 元リポジトリと同期可能
- ✅ NixOS自動デプロイに統合

**デメリット**:
- ❌ submodule操作が複雑
- ❌ ライターの変更を元リポジトリに反映する手順が必要

---

### 案2: Sparse Checkout（submoduleなし）
```
~/projects/applebuyers_application/
└── public-site/                     # sparse-checkout
```

**メリット**:
- ✅ シンプル
- ✅ 元リポジトリと直接同期

**デメリット**:
- ❌ lab-projectの管理外
- ❌ 統一されたデプロイフローに乗せられない

---

### 案3: Syncthing自動同期
```
[ローカルMac]
~/dev/applebuyers_application/public-site/
  ↓ Syncthing
[NixOS]
~/projects/applebuyers-public-site/
```

**メリット**:
- ✅ 自動同期
- ✅ 設定簡単

**デメリット**:
- ❌ lab-projectの管理外
- ❌ Git履歴が二重管理になる

---

## 🎯 理想的な構成

### 求める要件
1. **統一管理**: lab-projectのprojects/配下で管理
2. **自動デプロイ**: GitHub Actions → NixOS自動更新
3. **ライター環境**: code-server + yarn dev
4. **元リポジトリ同期**: applebuyers_applicationとの双方向同期

### 技術スタック
- **フレームワーク**: Next.js 15
- **パッケージ管理**: pnpm
- **ポート**: 13005（固定）
- **記事管理**: Markdown（`content/articles/`）
- **画像管理**: `content/images/articles/`

---

## 🤔 質問・相談事項

### 1. アーキテクチャ選択
どの案が最も適切だと思いますか？他に良い方法はありますか？

### 2. Git Submodule運用
もしsubmoduleを使う場合、ライターの編集をどう元リポジトリに反映すべきですか？
- PRベースのワークフロー？
- 自動同期スクリプト？

### 3. NixOS設定
service.nixの配置場所はどこが適切ですか？
- `projects/applebuyers-public-site/service.nix`
- `projects/applebuyers-public-site/public-site/service.nix`

### 4. ディレクトリ構成
lab-projectのprojects/配下に配置する場合、どういう名前が良いですか？
- `applebuyers-public-site/`
- `applebuyers-website/`
- `public-site/`

### 5. 既存サービスとの統合
既存のdashboard（ポート3000）やnakamura-misaki（ポート8010）と同様の扱いで良いですか？

---

## 📝 現在の実装状況

### 完了
- ✅ NixOSにcode-serverが稼働中（ポート8889）
- ✅ ライター向けセットアップガイド作成（`~/sync-general/applebuyers-article-setup.md`）
- ✅ 記事テンプレート準備済み

### 未完了
- ⏳ public-siteのNixOS配置
- ⏳ lab-projectへの統合
- ⏳ service.nix作成
- ⏳ 自動デプロイ設定

---

## 🔄 次のアクション

あなたの意見・提案を聞いて、最適な実装方法を決定したいです。

特に以下について教えてください：
1. **推奨アーキテクチャ**: どの案が最適か？
2. **実装手順**: 具体的なステップ
3. **注意点**: 見落としている問題点
4. **代替案**: もっと良い方法があれば

よろしくお願いします！
