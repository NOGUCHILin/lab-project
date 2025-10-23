# lab-project

NixOS統合環境 - 全プロジェクト・NixOS設定を統合管理

## 🎯 Repository概要

複数のWebサービス（dashboard, nakamura-misaki, code-server等）とそれらを動かすNixOS設定を一元管理。mainブランチへのpushで自動的にGitHub Actions経由でNixOS本番環境にデプロイ。

---

## 🚀 よく使うコマンド

<example name="ローカルテスト">
```bash
cd nixos-config
nix flake check  # 構文チェック
nix fmt          # フォーマット
```
</example>

<example name="デプロイ">
```bash
# mainブランチにpushで自動デプロイ
git push origin main

# デプロイ状況確認
gh run watch
```
</example>

<example name="サービス管理（本番環境）">
```bash
# SSH接続
ssh home-lab-01

# サービス状態確認
systemctl status nakamura-misaki-api.service
journalctl -u nakamura-misaki-api.service -f

# Tailscale公開状態確認
tailscale serve status
tailscale funnel status

# サービス一覧とヘルスチェック
check-services
```
</example>

---

## ⚠️ 重要な制約

<instructions>
**必ず遵守すべきルール**:

- **宣言的設定を優先**: 手動での設定変更は避け、必ずNixOS設定ファイルに反映
- **Tailscale Funnel制限**: ポート443, 8443, 10000のみサポート
- **Service Registry**: 新サービス追加時は必ず `default.nix` に登録
- **秘密情報管理**: sops-nix経由で必ず暗号化
- **デプロイは自動**: mainへのpushで自動デプロイされるため、テストは慎重に

**Next.js固有の制約**:
- ⚠️ **NEXT_PUBLIC_*変数はビルド時に埋め込まれる** - ランタイム設定は無効、Nixパッケージのパラメータ化が必須（詳細: `claudedocs/nextjs-nix-best-practices.md`）
- ⚠️ **本番デプロイ前に必ずローカルでビルドテスト** - `npm run build` 成功を確認、pre-push フックが自動実行

**禁止事項**:
- ❌ 手動でのsystemctl設定変更（NixOS再ビルドで上書きされる）
- ❌ プレーンテキストでの秘密情報コミット
- ❌ Funnel非対応ポート（443/8443/10000以外）での外部公開
- ❌ テスト不十分なままmainブランチへpush
- ❌ Next.jsのNEXT_PUBLIC_*変数をsystemd environmentで設定（ビルド時に注入が必要）
</instructions>

---

## 🏗️ Service Registry Pattern

**すべてのサービスは `nixos-config/modules/services/registry/default.nix` で一元管理**

<instructions>
新サービス追加時は以下の手順を厳守：

1. `nixos-config/modules/services/registry/` に `.nix` ファイル作成
2. `default.nix` の `services` リストに登録
3. `configuration.nix` の `imports` に追加
4. Tailscale公開設定を決定（Funnel or Serve）

**重要な制約**:
- ポート番号は `nixos-config/modules/core/port-management.nix` で一元管理
- 既存ポートとの競合を必ず確認
- Funnelはポート443/8443/10000のみサポート
- その他のポートはServeで公開（Tailscaleネットワーク内のみ）
</instructions>

<example name="新API追加（Funnel公開）">
**シナリオ**: Slack Webhook受信用の外部公開API

```nix
# nixos-config/modules/services/registry/webhook-api.nix
{
  port = 10001;
  path = "/webhook";
  name = "Webhook API";
  description = "外部Webhook受信用API";
  healthCheck = "/health";
  icon = "🔌";
}
```

Registry登録・Tailscale設定・デプロイの詳細は `claudedocs/service-registry.md` を参照
</example>

<example name="ポート競合エラー">
**シナリオ**: 既存ポート3000でサービスを追加しようとした場合

```nix
# ❌ エラー例
{ port = 3000; name = "New Service"; }
```

**結果**: NixOS再ビルド時にポート競合エラー

**解決策**:
1. `nixos-config/modules/core/port-management.nix` で空きポートを確認
2. 未使用ポート（例: 3006）を選択
</example>

---

## 📐 アーキテクチャ

### リポジトリ構造

```
lab-project/                     # リポジトリルート
├── nixos-config/                # NixOS設定（flake.nixはここ）
│   ├── flake.nix               # NixOS設定のエントリーポイント
│   ├── hosts/home-lab-01/      # ホスト固有設定
│   │   └── configuration.nix
│   └── modules/                # 再利用可能なモジュール
│       ├── core/               # 基盤設定（ポート管理、SSH等）
│       ├── networking/         # Tailscale VPN
│       └── services/registry/  # サービス定義
├── projects/                    # 各Webサービスのソースコード
│   ├── dashboard/
│   ├── nakamura-misaki/
│   └── ...
└── claudedocs/                  # 詳細ドキュメント（タスク指向）
```

**重要**: NixOSコマンドは`nixos-config/`ディレクトリで実行する必要があります。

### Flake-based NixOS Configuration

- **flake.nix**: `nixos-config/flake.nix`がエントリーポイント
- **ホスト定義**: `nixos-config/hosts/home-lab-01/configuration.nix`
- **モジュール構成**:
  - `modules/core/`: 基盤設定（ポート管理、SSH、ファイアウォール、シークレット）
  - `modules/networking/`: Tailscale VPN設定
  - `modules/services/registry/`: サービス定義（各サービス毎にnixファイル）

### Tailscale Exposure

| 公開方式 | 用途 | ポート制限 |
|---------|------|-----------|
| **Funnel** | インターネット公開 | 443/8443/10000のみ |
| **Serve** | Tailscaleネットワーク内のみ | なし |

設定は `nixos-config/modules/services/tailscale-direct.nix` で宣言的に管理

### 主要ポート

| ポート | サービス | 公開方式 |
|--------|---------|---------|
| 3000 | Dashboard | Serve (HTTPS 443経由) |
| 3002 | nakamura-misaki Admin UI | Serve |
| 10000 | nakamura-misaki API | Funnel |
| 8889-8891 | code-server | Serve |

詳細は `nixos-config/modules/core/port-management.nix` 参照

---

## 📚 詳細ドキュメント

プロジェクト固有の詳細情報は `claudedocs/` を参照：

| ファイル | 内容 |
|---------|------|
| `service-registry.md` | Service Registryパターンの完全実装ガイド（7ステップ、トラブルシューティング等） |
| `nextjs-nix-best-practices.md` | **重要** Next.js+Nix統合のベストプラクティス（NEXT_PUBLIC_*変数、ビルド時注入、ローカルテスト戦略） |
| `deployment.md` | デプロイワークフローの詳細 |
| `troubleshooting.md` | 一般的なトラブルシューティング |

---

最終更新: 2025-10-23（Next.js+Nixベストプラクティス追加）
