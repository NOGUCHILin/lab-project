# nakamura-misaki v4.0.0 - Architectural Proposal for NixOS Integration

最終更新: 2025-10-14

---

## 🎯 問題の本質

### 現在のアーキテクチャ

```
GitHub Actions
  ↓ (rsync)
~/projects/lab-project/nakamura-misaki/
  ↓ (python3 -m venv)
.venv/
  ↓ (pip install -e .)
依存関係インストール
  ↓
systemd service起動（ExecStart = .venv/bin/uvicorn）
```

**問題点**:
1. ❌ NixOS管理外のPython環境（.venv）
2. ❌ デプロイ時に毎回pip install実行
3. ❌ NixOS再ビルドと依存関係が切り離されている
4. ❌ 手動操作によるドリフトリスク
5. ❌ 再現性・不変性の原則違反

---

## ✅ 3つの解決策（推奨順）

---

## 案1: buildPythonApplication（最も堅牢）⭐

### アーキテクチャ

```
flake.nix
  ↓
packages.nakamura-misaki (Nix derivation)
  ↓ (buildPythonApplication)
/nix/store/xxx-nakamura-misaki-4.0.0/
  ├── bin/nakamura-api
  ├── lib/python3.12/site-packages/
  └── (全依存関係含む)
  ↓
systemd service起動（ExecStart = ${pkgs.nakamura-misaki}/bin/nakamura-api）
```

### 実装ステップ

#### Step 1: nakamura-misakiをNixパッケージ化

`nixos-config/packages/nakamura-misaki/default.nix`:

```nix
{ lib
, python3
, fetchFromGitHub
, postgresql
}:

python3.pkgs.buildPythonApplication rec {
  pname = "nakamura-misaki";
  version = "4.0.0";
  format = "pyproject";

  # ローカルソースを使用
  src = ../../../nakamura-misaki;

  nativeBuildInputs = with python3.pkgs; [
    hatchling  # pyproject.tomlのbuild-backend
  ];

  propagatedBuildInputs = with python3.pkgs; [
    fastapi
    uvicorn
    slack-bolt
    slack-sdk
    anthropic
    aiohttp
    psycopg
    sqlalchemy
    pgvector
    pydantic
    pydantic-settings
    python-dateutil
  ];

  # テストは別途CIで実行済みのためスキップ
  doCheck = false;

  meta = with lib; {
    description = "Task management AI assistant with Kusanagi Motoko personality";
    homepage = "https://github.com/NOGUCHILin/lab-project";
    license = licenses.mit;
    maintainers = [ "noguchilin" ];
  };
}
```

#### Step 2: flake.nixに登録

`nixos-config/flake.nix`:

```nix
{
  outputs = { self, nixpkgs, ... }: {
    packages.x86_64-linux.nakamura-misaki =
      nixpkgs.legacyPackages.x86_64-linux.callPackage ./packages/nakamura-misaki { };

    nixosConfigurations.home-lab-01 = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      specialArgs = {
        nakamura-misaki = self.packages.x86_64-linux.nakamura-misaki;
      };
      modules = [ ./hosts/home-lab-01/configuration.nix ];
    };
  };
}
```

#### Step 3: systemd serviceを書き換え

`modules/services/registry/nakamura-misaki-api.nix`:

```nix
{ config, pkgs, nakamura-misaki, ... }:

{
  systemd.services.nakamura-misaki-api = {
    description = "nakamura-misaki v4.0.0 API Server";
    after = [ "network-online.target" "postgresql.service" ];
    wants = [ "network-online.target" ];
    requires = [ "postgresql.service" ];
    wantedBy = [ "multi-user.target" ];

    serviceConfig = {
      Type = "simple";
      User = "noguchilin";
      Group = "users";
      Restart = "always";
      RestartSec = "5s";

      ExecStart = pkgs.writeShellScript "start-nakamura-api" ''
        set -e

        # Load secrets
        export SLACK_BOT_TOKEN=$(cat ${config.sops.secrets.slack_bot_token.path})
        export SLACK_SIGNING_SECRET=$(cat ${config.sops.secrets.slack_signing_secret.path})
        export ANTHROPIC_API_KEY=$(cat ${config.sops.secrets.anthropic_api_key.path})
        export DATABASE_URL="postgresql+asyncpg://nakamura_misaki@localhost:5432/nakamura_misaki"

        # C++ library path for numpy (required by pgvector)
        export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"

        # Start FastAPI server with uvicorn（Nixパッケージから直接実行）
        ${nakamura-misaki}/bin/uvicorn src.adapters.primary.api:app \
          --host 127.0.0.1 \
          --port 10000 \
          --log-level info
      '';
    };
  };

  services.tailscale.useRoutingFeatures = "both";
}
```

#### Step 4: GitHub Actionsを簡素化

`.github/workflows/deploy.yml`:

```yaml
# nakamura-misakiコード同期ステップは維持（rsyncでコード配置）
- name: Sync nakamura-misaki code
  uses: appleboy/ssh-action@master
  with:
    script: |
      # ... (rsync処理) ...

# ❌ 削除: venv作成・pip installステップ（不要になる）

# NixOS再ビルドで依存関係も自動解決
- name: Deploy NixOS configuration
  uses: appleboy/ssh-action@master
  with:
    script: |
      cd nixos-config
      sudo nixos-rebuild switch --flake .#home-lab-01
      # → この時点で nakamura-misaki パッケージがビルドされ
      #    /nix/store/ に配置される
```

### メリット・デメリット

| メリット | デメリット |
|---------|----------|
| ✅ 完全な再現性（flake.lock） | ❌ 初期セットアップが複雑 |
| ✅ 不変性（/nix/store） | ❌ 開発時の反映に再ビルド必要 |
| ✅ ロールバック可能 | ❌ Python生態系に不慣れな場合学習コスト |
| ✅ .venv不要 | |
| ✅ デプロイ高速化（ビルド済みバイナリ） | |

---

## 案2: python3.withPackages（中間案）

### アーキテクチャ

```
flake.nix
  ↓
pythonEnv = python3.withPackages (ps: [ ps.fastapi ps.uvicorn ... ])
  ↓
systemd service起動（ExecStart = ${pythonEnv}/bin/uvicorn）
```

### 実装ステップ

#### Step 1: Python環境をNixで定義

`modules/services/registry/nakamura-misaki-api.nix`:

```nix
{ config, pkgs, ... }:

let
  pythonEnv = pkgs.python3.withPackages (ps: with ps; [
    fastapi
    uvicorn
    slack-bolt
    slack-sdk
    anthropic
    aiohttp
    psycopg
    sqlalchemy
    pgvector
    pydantic
    pydantic-settings
    python-dateutil
  ]);
in
{
  systemd.services.nakamura-misaki-api = {
    description = "nakamura-misaki v4.0.0 API Server";
    after = [ "network-online.target" "postgresql.service" ];
    wants = [ "network-online.target" ];
    requires = [ "postgresql.service" ];
    wantedBy = [ "multi-user.target" ];

    serviceConfig = {
      Type = "simple";
      User = "noguchilin";
      Group = "users";
      WorkingDirectory = "/home/noguchilin/projects/lab-project/nakamura-misaki";
      Restart = "always";
      RestartSec = "5s";

      ExecStart = pkgs.writeShellScript "start-nakamura-api" ''
        set -e

        # Load secrets
        export SLACK_BOT_TOKEN=$(cat ${config.sops.secrets.slack_bot_token.path})
        export SLACK_SIGNING_SECRET=$(cat ${config.sops.secrets.slack_signing_secret.path})
        export ANTHROPIC_API_KEY=$(cat ${config.sops.secrets.anthropic_api_key.path})
        export DATABASE_URL="postgresql+asyncpg://nakamura_misaki@localhost:5432/nakamura_misaki"

        # C++ library path for numpy (required by pgvector)
        export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"

        # PYTHONPATHに現在のプロジェクトを追加
        export PYTHONPATH="/home/noguchilin/projects/lab-project/nakamura-misaki:$PYTHONPATH"

        # Start FastAPI server with uvicorn（Nix管理のPython環境）
        ${pythonEnv}/bin/uvicorn src.adapters.primary.api:app \
          --host 127.0.0.1 \
          --port 10000 \
          --log-level info
      '';
    };
  };

  services.tailscale.useRoutingFeatures = "both";
}
```

#### Step 2: GitHub Actionsを簡素化

`.github/workflows/deploy.yml`:

```yaml
# nakamura-misakiコード同期ステップは維持
- name: Sync nakamura-misaki code
  uses: appleboy/ssh-action@master
  with:
    script: |
      # ... (rsync処理) ...

# ❌ 削除: venv作成・pip installステップ（不要になる）

# NixOS再ビルドで依存関係も自動解決
- name: Deploy NixOS configuration
  uses: appleboy/ssh-action@master
  with:
    script: |
      cd nixos-config
      sudo nixos-rebuild switch --flake .#home-lab-01
```

### メリット・デメリット

| メリット | デメリット |
|---------|----------|
| ✅ .venv不要 | ⚠️ nakamura-misakiパッケージ化されていない |
| ✅ 依存関係Nix管理 | ⚠️ PYTHONPATHで動的にソース参照 |
| ✅ 案1より実装簡単 | ⚠️ 完全な不変性ではない |
| ✅ デプロイ簡素化 | |

---

## 案3: uv + nix-ld（実験的）

### アーキテクチャ

```
uv (Rust製パッケージマネージャ)
  ↓
.venv/ (uvが管理)
  ↓
nix-ld（標準ライブラリパスを提供）
  ↓
systemd service起動（uv run uvicorn）
```

### 実装ステップ

#### Step 1: uvをNixOSにインストール

`configuration.nix`:

```nix
{ config, pkgs, ... }:

{
  environment.systemPackages = with pkgs; [
    uv
  ];

  programs.nix-ld.enable = true;
  programs.nix-ld.libraries = with pkgs; [
    stdenv.cc.cc.lib
    zlib
    # 必要に応じて追加
  ];
}
```

#### Step 2: systemd serviceをuv経由に変更

`modules/services/registry/nakamura-misaki-api.nix`:

```nix
{ config, pkgs, ... }:

{
  systemd.services.nakamura-misaki-api = {
    description = "nakamura-misaki v4.0.0 API Server";
    after = [ "network-online.target" "postgresql.service" ];
    wants = [ "network-online.target" ];
    requires = [ "postgresql.service" ];
    wantedBy = [ "multi-user.target" ];

    serviceConfig = {
      Type = "simple";
      User = "noguchilin";
      Group = "users";
      WorkingDirectory = "/home/noguchilin/projects/lab-project/nakamura-misaki";
      Restart = "always";
      RestartSec = "5s";

      ExecStart = pkgs.writeShellScript "start-nakamura-api" ''
        set -e

        # Load secrets
        export SLACK_BOT_TOKEN=$(cat ${config.sops.secrets.slack_bot_token.path})
        export SLACK_SIGNING_SECRET=$(cat ${config.sops.secrets.slack_signing_secret.path})
        export ANTHROPIC_API_KEY=$(cat ${config.sops.secrets.anthropic_api_key.path})
        export DATABASE_URL="postgresql+asyncpg://nakamura_misaki@localhost:5432/nakamura_misaki"

        # nix-ldでライブラリパス自動解決
        export NIX_LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc.lib ]}"

        # uv経由でuvicorn実行
        ${pkgs.uv}/bin/uv run uvicorn src.adapters.primary.api:app \
          --host 127.0.0.1 \
          --port 10000 \
          --log-level info
      '';
    };
  };

  services.tailscale.useRoutingFeatures = "both";
}
```

#### Step 3: GitHub Actionsでuv sync実行

`.github/workflows/deploy.yml`:

```yaml
- name: Sync nakamura-misaki dependencies
  uses: appleboy/ssh-action@master
  with:
    script: |
      cd /home/noguchilin/projects/lab-project/nakamura-misaki

      # uv syncで依存関係同期（.venv自動作成）
      uv sync
      echo "✅ Dependencies synced with uv"

- name: Deploy NixOS configuration
  uses: appleboy/ssh-action@master
  with:
    script: |
      cd nixos-config
      sudo nixos-rebuild switch --flake .#home-lab-01
```

### メリット・デメリット

| メリット | デメリット |
|---------|----------|
| ✅ uvの高速性（Rust実装） | ⚠️ まだ実験的（NixOS統合未成熟） |
| ✅ pyproject.tomlそのまま使用可 | ⚠️ .venvは残る |
| ✅ 開発体験良好 | ⚠️ Nix哲学との距離 |
| ✅ nix-ldで互換性確保 | |

---

## 🎯 推奨実装戦略

### Phase A: 案2で速やかに安定化（1-2日）

**理由**:
- 現在の.venv問題を即座に解決
- 実装コスト最小
- 案1へのマイグレーションパスが明確

**ステップ**:
1. `nakamura-misaki-api.nix` を案2の実装に書き換え
2. `deploy.yml` から venv/pip ステップを削除
3. デプロイ・動作確認
4. Phase 5完了

### Phase B: 案1へマイグレーション（1週間）

**タイミング**: Phase 5-8が安定稼働後

**理由**:
- 完全な再現性・不変性を達成
- NixOS哲学に完全準拠
- ロールバック・複数バージョン管理が可能

**ステップ**:
1. `packages/nakamura-misaki/default.nix` 作成
2. ローカルでビルドテスト（`nix build .#nakamura-misaki`）
3. flake.nix統合
4. systemd service書き換え
5. デプロイ・動作確認

---

## 比較表

| 観点 | 案1 (buildPythonApp) | 案2 (withPackages) | 案3 (uv+nix-ld) | 現状 (venv) |
|-----|---------------------|-------------------|----------------|------------|
| 再現性 | ⭐⭐⭐ | ⭐⭐ | ⭐ | ❌ |
| 不変性 | ⭐⭐⭐ | ⭐⭐ | ❌ | ❌ |
| デプロイ速度 | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐ |
| 開発体験 | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 実装コスト | 高 | 中 | 中 | 低 |
| NixOS哲学 | ⭐⭐⭐ | ⭐⭐ | ⭐ | ❌ |

---

## 実装タイムライン

### 短期（今週）: 案2実装
```
Day 1: nakamura-misaki-api.nix書き換え
Day 2: デプロイ・動作確認・Phase 5完了
```

### 中期（来週以降）: 案1マイグレーション
```
Week 1: packages/nakamura-misaki/作成・ローカルテスト
Week 2: 本番デプロイ・安定化
```

---

## 結論

**即座の行動**: 案2（python3.withPackages）を実装し、Phase 5を完了させる

**長期目標**: 案1（buildPythonApplication）へマイグレーションし、完全な宣言的管理を達成

**案3について**: uvは将来有望だが、現時点ではNixOS統合が未成熟のため保留

---

Generated with [Claude Code](https://claude.com/claude-code)
