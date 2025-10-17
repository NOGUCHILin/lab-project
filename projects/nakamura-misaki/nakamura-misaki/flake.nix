{
  description = "Nakamura-Misaki - Multi-User Claude Code Agent Service";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
  in {
    # 開発環境（direnv用）
    devShells.${system}.default = pkgs.mkShell {
      name = "nakamura-misaki-dev";

      buildInputs = with pkgs; [
        python312
        python312Packages.pip
        python312Packages.virtualenv
        python312Packages.requests
        python312Packages.redis
        git
        jq
      ];

      shellHook = ''
        echo "🤖 Nakamura-Misaki 開発環境"
        echo "🐍 Python: $(python --version)"
        echo ""

        # 仮想環境のセットアップ
        if [ ! -d ".venv" ]; then
          echo "📦 仮想環境を作成中..."
          python -m venv .venv
        fi

        # 仮想環境をアクティベート
        source .venv/bin/activate

        # Claude Agent SDKをインストール（まだの場合）
        if ! python -c "import claude_agent_sdk" 2>/dev/null; then
          echo "🔧 Claude Agent SDK をインストール中..."
          pip install claude-agent-sdk
        fi

        # Redis & RQ をインストール（まだの場合）
        if ! python -c "import redis" 2>/dev/null; then
          echo "🔧 Redis & RQ をインストール中..."
          pip install redis rq
        fi

        echo "✅ 開発環境準備完了"
        echo "🎯 Python: $(which python)"
        echo "📁 作業ディレクトリ: $PWD"
        echo ""
        echo "💡 コマンド:"
        echo "  python -m src.main  - サービス起動"
      '';
    };

    # NixOSモジュール（本番デプロイ用）
    nixosModules.default = { config, lib, pkgs, ... }:
    let
      cfg = config.services.nakamura-misaki;
      projectDir = "/home/noguchilin/projects/nakamura-misaki";

      pythonEnv = pkgs.python312.withPackages (ps: with ps; [
        requests
      ]);
    in {
      options.services.nakamura-misaki = {
        enable = lib.mkEnableOption "Nakamura-Misaki Claude Agent Service";

        port = lib.mkOption {
          type = lib.types.port;
          default = 10000;
          description = "Port for the web service";
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
          after = [ "network.target" ];

          environment = {
            PYTHONPATH = "${projectDir}/src:${projectDir}";
            HOME = "/home/noguchilin";
          };

          path = [ pythonEnv pkgs.nodejs_22 ];

          serviceConfig = {
            Type = "simple";
            User = "noguchilin";
            Group = "users";
            WorkingDirectory = projectDir;

            ExecStart = pkgs.writeShellScript "nakamura-start" ''
              ${lib.optionalString (cfg.slackToken != "") ''
                export SLACK_BOT_TOKEN="${cfg.slackToken}"
              ''}
              ${lib.optionalString (cfg.anthropicApiKey != "") ''
                export ANTHROPIC_API_KEY="${cfg.anthropicApiKey}"
              ''}
              export NAKAMURA_USER_ID=${cfg.nakamuraUserId}
              export PORT=${toString cfg.port}
              export PYTHONUNBUFFERED=1

              # venv存在確認
              if [ ! -f ${projectDir}/.venv/bin/python ]; then
                echo "❌ venv not found at ${projectDir}/.venv"
                exit 1
              fi

              # claude-agent-sdk確認
              if ! ${projectDir}/.venv/bin/python -c "import claude_agent_sdk" 2>/dev/null; then
                echo "⚠️ claude-agent-sdk not found, installing..."
                ${projectDir}/.venv/bin/pip install --quiet claude-agent-sdk
              fi

              cd ${projectDir}
              exec ${projectDir}/.venv/bin/python -m src.main
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
              ${pkgs.tailscale}/bin/tailscale funnel --bg --https=${toString cfg.port} ${toString cfg.port}

              # Display webhook URL
              echo "Nakamura-Misaki webhook URL (external):"
              echo "https://$(${pkgs.tailscale}/bin/tailscale status --json | ${pkgs.jq}/bin/jq -r '.Self.DNSName' | sed 's/\.$//')/:${toString cfg.port}/webhook/slack"
            '';

            ExecStop = pkgs.writeShellScript "stop-funnel" ''
              ${pkgs.tailscale}/bin/tailscale funnel --https=${toString cfg.port} off
            '';
          };
        };
      };
    };
  };
}
