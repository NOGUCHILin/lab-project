{
  description = "Nakamura-Misaki - Multi-User Claude Code Agent Service";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };

    # Pythonパッケージとして定義（ソースのみ、依存関係は実行時にvenvから）
    # Nixはソースコードを/nix/store/に配置し、実行時に外部venvを参照
    nakamura-misaki = pkgs.stdenv.mkDerivation rec {
      pname = "nakamura-misaki";
      version = "6.0.0";

      src = ./.;

      nativeBuildInputs = with pkgs; [
        makeWrapper
      ];

      buildInputs = with pkgs; [
        python312
      ];

      # ビルド不要、ソースをそのままコピー
      dontBuild = true;

      # インストール：srcをコピーして起動スクリプトを作成
      installPhase = ''
        mkdir -p $out/opt/nakamura-misaki

        # ソースコードをコピー（.venvは除外）
        cp -r src $out/opt/nakamura-misaki/
        cp pyproject.toml uv.lock README.md $out/opt/nakamura-misaki/ || true

        # 起動スクリプトを作成
        # 実行時に /home/noguchilin/projects/lab-project/nakamura-misaki/.venv を使用
        mkdir -p $out/bin
        makeWrapper ${pkgs.python312}/bin/python $out/bin/nakamura-misaki \
          --add-flags "-m src.main" \
          --set PYTHONPATH "$out/opt/nakamura-misaki:$out/opt/nakamura-misaki/src" \
          --chdir "$out/opt/nakamura-misaki"
      '';

      meta = with pkgs.lib; {
        description = "DDD + Clean Architecture based task management AI assistant";
        homepage = "https://github.com/NOGUCHILin/lab-project";
        license = licenses.mit;
        maintainers = [];
      };
    };

  in {
    # パッケージをエクスポート
    packages.${system} = {
      default = nakamura-misaki;
      nakamura-misaki = nakamura-misaki;
    };

    # 開発環境（direnv用）
    devShells.${system}.default = pkgs.mkShell {
      name = "nakamura-misaki-dev";

      buildInputs = with pkgs; [
        python312
        python312Packages.pip
        python312Packages.virtualenv
        python312Packages.uv
        git
        jq
      ];

      shellHook = ''
        echo "🤖 Nakamura-Misaki 開発環境"
        echo "🐍 Python: $(python --version)"
        echo ""

        # uvで仮想環境セットアップ
        if [ ! -d ".venv" ]; then
          echo "📦 uv sync実行中..."
          uv sync
        fi

        # 仮想環境をアクティベート
        source .venv/bin/activate

        echo "✅ 開発環境準備完了"
        echo "🎯 Python: $(which python)"
        echo "📁 作業ディレクトリ: $PWD"
        echo ""
        echo "💡 コマンド:"
        echo "  uv run python -m src.main  - サービス起動"
        echo "  uv run pytest                - テスト実行"
      '';
    };

    # NixOSモジュール（本番デプロイ用）
    nixosModules.default = { config, lib, pkgs, ... }:
    let
      cfg = config.services.nakamura-misaki;
      # Nixパッケージを使用
      package = self.packages.${system}.nakamura-misaki;
    in {
      options.services.nakamura-misaki = {
        enable = lib.mkEnableOption "Nakamura-Misaki Claude Agent Service";

        # 既存設定との後方互換性のため ports.api を優先
        ports = {
          api = lib.mkOption {
            type = lib.types.port;
            default = 10000;
            description = "API Backend port";
          };

          adminUI = lib.mkOption {
            type = lib.types.port;
            default = 3002;
            description = "Admin UI port (currently not used)";
          };

          webhook = lib.mkOption {
            type = lib.types.port;
            default = 10000;
            description = "Deprecated: use ports.api instead";
          };
        };

        enforceDeclarative = lib.mkOption {
          type = lib.types.bool;
          default = false;
          description = "Refuse manual systemctl operations";
        };

        enableFunnel = lib.mkOption {
          type = lib.types.bool;
          default = true;
          description = "Enable Tailscale Funnel for external access";
        };

        slackToken = lib.mkOption {
          type = lib.types.str;
          default = "";
          description = "Slack bot token (use sops for secrets)";
        };

        anthropicApiKey = lib.mkOption {
          type = lib.types.str;
          default = "";
          description = "Anthropic API key (use sops for secrets)";
        };

        databaseUrl = lib.mkOption {
          type = lib.types.str;
          default = "";
          description = "PostgreSQL database URL (use sops for secrets)";
        };

        nakamuraUserId = lib.mkOption {
          type = lib.types.str;
          default = "U09AHTB4X4H";
          description = "Slack user ID for Nakamura";
        };
      };

      config = lib.mkIf cfg.enable {
        # Main service
        systemd.services.nakamura-misaki = {
          description = "Nakamura-Misaki Multi-User Claude Code Agent";
          wantedBy = [ "multi-user.target" ];
          after = [ "network.target" "postgresql.service" ];

          environment = {
            PORT = toString cfg.ports.api;
            NAKAMURA_USER_ID = cfg.nakamuraUserId;
            PYTHONUNBUFFERED = "1";
          } // lib.optionalAttrs (cfg.databaseUrl != "") {
            DATABASE_URL = cfg.databaseUrl;
          };

          serviceConfig = {
            Type = "simple";
            User = "noguchilin";
            Group = "users";
            WorkingDirectory = "/home/noguchilin/projects/lab-project/nakamura-misaki";

            # venvの準備と依存関係のインストール（noguchilinユーザーで実行）
            # nix-ldが有効なのでvenvでネイティブライブラリが正しくリンクされる
            # 戦略: .venvを毎回削除して再作成（権限問題を完全回避）
            ExecStartPre = pkgs.writeShellScript "nakamura-pre-start" ''
              set -e

              TARGET_DIR="/home/noguchilin/projects/lab-project/nakamura-misaki"

              # ディレクトリ作成
              mkdir -p "$TARGET_DIR"

              # ソースコードを同期（.venvは完全無視）
              ${pkgs.rsync}/bin/rsync -a --delete \
                --exclude=".venv" \
                --exclude="__pycache__" \
                --exclude="*.pyc" \
                --exclude="node_modules" \
                --exclude="workspaces" \
                ${package}/opt/nakamura-misaki/ "$TARGET_DIR/"

              # 古い.venvを削除（権限問題がある場合はスキップ）
              cd "$TARGET_DIR"
              rm -rf .venv 2>/dev/null || true

              # venvを新規作成
              ${pkgs.python312}/bin/python -m venv .venv

              # 依存関係をインストール
              .venv/bin/pip install -q --upgrade pip
              .venv/bin/pip install -q -r requirements.txt
              .venv/bin/pip install -q claude-agent-sdk pgvector
            '';

            # sops secretsを環境変数として読み込んでから起動
            ExecStart = pkgs.writeShellScript "nakamura-start" ''
              # Load secrets from sops-nix
              export SLACK_BOT_TOKEN=$(cat ${config.sops.secrets.slack_bot_token.path})
              export SLACK_SIGNING_SECRET=$(cat ${config.sops.secrets.slack_signing_secret.path})
              export ANTHROPIC_API_KEY=$(cat ${config.sops.secrets.anthropic_api_key.path})

              # Launch the service from venv
              cd /home/noguchilin/projects/lab-project/nakamura-misaki
              exec .venv/bin/python -m src.main
            '';

            Restart = "always";
            RestartSec = 10;
            KillMode = "mixed";
            KillSignal = "SIGTERM";
            TimeoutStopSec = 10;

            # セキュリティ設定
            PrivateTmp = true;
            ProtectSystem = "strict";
            ProtectHome = false;  # Claude CLIアクセス許可
            ReadWritePaths = [
              "/home/noguchilin/.claude"
              "/home/noguchilin/projects/lab-project/nakamura-misaki"
            ];
          };
        };

        # Tailscale Funnel設定
        systemd.services.nakamura-misaki-funnel = lib.mkIf cfg.enableFunnel {
          description = "Setup Tailscale Funnel for Nakamura-Misaki";
          wantedBy = [ "multi-user.target" ];
          after = [ "tailscaled.service" "nakamura-misaki.service" "tailscale-serve-setup.service" ];

          serviceConfig = {
            Type = "oneshot";
            RemainAfterExit = true;
            User = "noguchilin";

            ExecStart = pkgs.writeShellScript "setup-funnel" ''
              # Wait for Tailscale and Serve to be ready
              sleep 5

              # Enable Funnel for external access
              ${pkgs.tailscale}/bin/tailscale funnel --bg --https=${toString cfg.ports.api} ${toString cfg.ports.api}

              # Display webhook URL
              echo "Nakamura-Misaki webhook URL (external):"
              echo "https://$(${pkgs.tailscale}/bin/tailscale status --json | ${pkgs.jq}/bin/jq -r '.Self.DNSName' | sed 's/\.$//')/:${toString cfg.ports.api}/webhook/slack"
            '';

            ExecStop = pkgs.writeShellScript "stop-funnel" ''
              ${pkgs.tailscale}/bin/tailscale funnel --https=${toString cfg.ports.api} off
            '';
          };
        };
      };
    };
  };
}
