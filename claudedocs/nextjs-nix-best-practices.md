# Next.js + Nix ベストプラクティス

Next.jsアプリケーションをNixでビルド・デプロイする際の重要な注意点とベストプラクティス

---

## ⚠️ 重要：`NEXT_PUBLIC_*` 環境変数はビルド時に埋め込まれる

### 問題

Next.jsの`NEXT_PUBLIC_*`環境変数は**ビルド時**にJavaScriptバンドルに埋め込まれます。**ランタイムでの設定は無効です。**

❌ **間違った実装**:
```nix
# NixOSモジュール
systemd.services.my-nextjs-app = {
  environment = {
    NEXT_PUBLIC_API_URL = "https://api.example.com";  # ← 遅すぎる！
  };
};
```

この設定では、Next.jsビルドは既に完了しており、`NEXT_PUBLIC_API_URL`はデフォルト値（例: `localhost:8000`）のまま埋め込まれています。

### 症状

- Web UIがAPI URLとして`localhost:8000`を使用
- ブラウザコンソールに`ERR_CONNECTION_REFUSED`エラー
- `configuration.nix`で`apiUrl`を変更しても反映されない
- サービス再起動では解決しない（再ビルドが必要）

---

## ✅ 解決策：Nixパッケージのパラメータ化

### 実装パターン

```nix
# Web UI flake.nix
{
  outputs = { self, nixpkgs }:
    let
      # パラメータ化された関数として定義
      mkWebUI = { apiUrl }: pkgs.buildNpmPackage {
        pname = "my-nextjs-app";

        # ビルド時に環境変数を注入
        buildPhase = ''
          export NEXT_PUBLIC_API_URL="${apiUrl}"
          npm run build
        '';
      };
    in
    {
      # デフォルトパッケージ（ローカルテスト用）
      packages.${system}.default = mkWebUI {
        apiUrl = "http://localhost:8000";
      };

      # NixOSモジュール
      nixosModules.default = { config, lib, ... }:
        let
          cfg = config.services.my-nextjs-app;
          # cfg.apiUrl でビルド
          webui-pkg = mkWebUI { apiUrl = cfg.apiUrl; };
        in
        {
          options.services.my-nextjs-app = {
            apiUrl = lib.mkOption {
              type = lib.types.str;
              description = "API URL (injected at build time)";
            };
          };

          config = {
            systemd.services.my-nextjs-app = {
              serviceConfig.WorkingDirectory = "${webui-pkg}";
            };
          };
        };
    };
}
```

### 動作原理

```
1. configuration.nix で apiUrl を設定
   services.my-nextjs-app.apiUrl = "https://api.example.com";

2. NixOSモジュールが mkWebUI を呼び出し
   webui-pkg = mkWebUI { apiUrl = "https://api.example.com"; }

3. Nixが新しいderivation（ビルド）を作成
   → buildPhase で NEXT_PUBLIC_API_URL="https://api.example.com"
   → npm run build
   → 新しいJavaScriptバンドル（API URL埋め込み済み）

4. systemd サービスが新しいパッケージを使用
```

### メリット

✅ `apiUrl`変更 → 自動的に再ビルドされる
✅ Nix purity原則に準拠（同じ入力→同じ出力）
✅ 宣言的で予測可能
✅ 手動のバージョンバンプ不要

---

## 📝 Nix Purity 原則

**「同じ入力 → 必ず同じ出力」を保証する原則**

```bash
# ❌ Impure（不純） - 実行環境に依存
builtins.getEnv "HOME"  # ユーザーによって異なる
date                     # 時刻に依存

# ✅ Pure（純粋） - 明示的な入力
mkWebUI = { apiUrl }: ...  # apiUrl が入力として宣言されている
```

### 重要なポイント

- **ビルド入力を明示的に宣言**する
- **環境変数に暗黙的に依存しない**
- パラメータ化することで、**Nixが変更を検知して再ビルド**

---

## 🧪 ローカルテスト戦略

**本番デプロイ前に必ずローカルでテスト**

### 1. Next.js 開発サーバーでテスト

```bash
cd projects/my-nextjs-app

# 環境変数を設定して開発サーバー起動
NEXT_PUBLIC_API_URL=https://api.example.com npm run dev

# ブラウザで http://localhost:3000 にアクセス
# - API呼び出しが正しいURLに向いているか確認
# - ブラウザコンソールでエラーがないか確認
```

### 2. Next.js ビルドテスト

```bash
# 本番ビルドをローカルで実行
NEXT_PUBLIC_API_URL=https://api.example.com npm run build

# ビルド成功を確認
# → 型エラー、ビルドエラーがないことを確認
```

### 3. Nix ビルド検証

```bash
cd nixos-config

# 構文チェック
nix flake check

# 個別パッケージのビルド（デプロイせずに）
nix build .#packages.x86_64-linux.my-nextjs-app

# システム全体のビルド（デプロイせずに）
nix build .#nixosConfigurations.home-lab-01.config.system.build.toplevel
```

### 4. deploy-rs Dry-Run

```bash
cd nixos-config

# 何が変更されるかシミュレート（実際にはデプロイしない）
deploy --dry-activate --ssh-user root .#home-lab-01
```

---

## 🔁 CI/CD: 自動テストの設定

### pre-push フックの設定

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      # Next.js ビルドテスト
      - id: nextjs-build
        name: Next.js Web UI build check
        entry: bash -c 'cd projects/my-nextjs-app && npm ci && npm run build'
        language: system
        files: ^projects/my-nextjs-app/
        stages: [push]

      # Python テスト（該当する場合）
      - id: pytest-all
        name: pytest-all
        entry: bash -c 'cd projects/my-app && uv run pytest tests/ -v'
        language: system
        files: ^projects/my-app/
        stages: [push]
```

### 動作

```bash
git commit -m "fix: Update API URL"  # ← pre-commit（軽量チェック）
git push origin main                 # ← pre-push（Next.jsビルド実行）
                                     #   失敗したらプッシュがキャンセル
```

---

## 🔍 トラブルシューティング

### 問題: 設定変更が反映されない

**症状**: `configuration.nix`で`apiUrl`を変更してもWeb UIが古いURLを使用

**原因**: Next.jsビルドが再実行されていない

**確認**:
```bash
# 本番環境で確認
ssh home-lab-01
journalctl -u my-nextjs-app.service | grep NEXT_PUBLIC_API_URL
```

**解決策**:
1. パッケージがパラメータ化されているか確認（上記パターン参照）
2. NixOS再ビルドを強制: `nixos-rebuild switch --flake .#home-lab-01`

### 問題: ビルドが遅い / タイムアウト

**症状**: GitHub Actionsでデプロイが失敗、400MBのRustクレートをビルド

**原因**: deploy-rsをソースからビルドしている

**解決策**:
```yaml
# .github/workflows/deploy.yml
- name: Install deploy-rs
  run: nix profile install nixpkgs#deploy-rs  # バイナリキャッシュから取得

- name: Deploy
  run: deploy .#home-lab-01  # nix run ではなく deploy コマンドを直接使用
```

---

## 参考リソース

- [Next.js Environment Variables](https://nextjs.org/docs/app/building-your-application/configuring/environment-variables)
- [NixOS Wiki: Node.js](https://wiki.nixos.org/w/index.php?title=Node.js)
- [Nix Flakes](https://nixos.wiki/wiki/Flakes)
- [lab-project CLAUDE.md](../CLAUDE.md)

---

最終更新: 2025-10-23
