{
  description = "Nakamura-Misaki - Multi-User Claude Code Agent Service";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };

    # Pythonパッケージとして定義（uvプロジェクトをそのまま使用）
    # uvが依存関係を管理し、Nixはランタイム環境のみ提供
    nakamura-misaki = pkgs.stdenv.mkDerivation rec {
      pname = "nakamura-misaki";
      version = "6.0.0";

      src = ./.;

      nativeBuildInputs = with pkgs; [
        python312Packages.uv
        makeWrapper
      ];

      buildInputs = with pkgs; [
        python312
      ];

      # uvで依存関係をインストール
      buildPhase = ''
        export HOME=$TMPDIR
        uv sync --frozen
      '';

      # インストール：srcと.venvをコピー
      installPhase = ''
        mkdir -p $out/opt/nakamura-misaki
        cp -r . $out/opt/nakamura-misaki/

        # 起動スクリプトを作成
        mkdir -p $out/bin
        makeWrapper ${pkgs.python312}/bin/python $out/bin/nakamura-misaki \
          --add-flags "-m src.main" \
          --set PYTHONPATH "$out/opt/nakamura-misaki/src:$out/opt/nakamura-misaki" \
          --chdir "$out/opt/nakamura-misaki" \
          --prefix PATH : "$out/opt/nakamura-misaki/.venv/bin"
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
            WorkingDirectory = "${package}/opt/nakamura-misaki";

            # sops secretsを環境変数として読み込んでから起動
            ExecStart = pkgs.writeShellScript "nakamura-start" ''
              # Load secrets from sops-nix
              export SLACK_BOT_TOKEN=$(cat ${config.sops.secrets.slack_bot_token.path})
              export SLACK_SIGNING_SECRET=$(cat ${config.sops.secrets.slack_signing_secret.path})
              export ANTHROPIC_API_KEY=$(cat ${config.sops.secrets.anthropic_api_key.path})

              # Launch the service
              exec ${package}/bin/nakamura-misaki
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
            ReadWritePaths = [ "/home/noguchilin/.claude" ];  # Claude CLI config
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
