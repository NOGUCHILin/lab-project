{
  description = "Nakamura-Misaki - Multi-User Claude Code Agent Service (Pure Nix)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };

    # カスタムPythonパッケージの定義
    customPythonPackages = {
      # claude-agent-sdk (PyPI: claude-agent-sdk 0.1.4)
      claude-agent-sdk = pkgs.python312Packages.buildPythonPackage rec {
        pname = "claude-agent-sdk";
        version = "0.1.4";

        src = pkgs.fetchPypi {
          inherit pname version;
          sha256 = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="; # Will get real hash from build error
        };

        propagatedBuildInputs = with pkgs.python312Packages; [
          anthropic
          httpx
        ];

        doCheck = false;
      };

      # pgvector (PyPI: pgvector 0.4.1)
      pgvector = pkgs.python312Packages.buildPythonPackage rec {
        pname = "pgvector";
        version = "0.4.1";

        src = pkgs.fetchPypi {
          inherit pname version;
          sha256 = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="; # Will get real hash from build error
        };

        propagatedBuildInputs = with pkgs.python312Packages; [
          numpy
        ];

        doCheck = false;
      };
    };

    # Python環境を構築（すべての依存関係を含む）
    pythonEnv = pkgs.python312.withPackages (ps: with ps; [
      # Core dependencies
      fastapi
      uvicorn
      pydantic
      pydantic-settings

      # Slack SDK
      slack-bolt
      slack-sdk

      # Anthropic
      anthropic

      # HTTP client
      aiohttp

      # Database
      sqlalchemy
      asyncpg
      psycopg3
      alembic

      # Python utilities
      python-dateutil

      # Custom packages
      customPythonPackages.claude-agent-sdk
      customPythonPackages.pgvector
    ]);

    # アプリケーションパッケージ
    nakamura-misaki = pkgs.stdenv.mkDerivation rec {
      pname = "nakamura-misaki";
      version = "6.0.0";

      src = ./.;

      nativeBuildInputs = [ pkgs.makeWrapper ];

      dontBuild = true;

      installPhase = ''
        mkdir -p $out/opt/nakamura-misaki
        cp -r src $out/opt/nakamura-misaki/

        mkdir -p $out/bin
        makeWrapper ${pythonEnv}/bin/python $out/bin/nakamura-misaki \
          --add-flags "-m src.main" \
          --set PYTHONPATH "$out/opt/nakamura-misaki" \
          --chdir "$out/opt/nakamura-misaki"
      '';

      meta = with pkgs.lib; {
        description = "DDD + Clean Architecture based task management AI assistant";
        homepage = "https://github.com/NOGUCHILin/lab-project";
        license = licenses.mit;
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
        git
        jq
      ];

      shellHook = ''
        echo "🤖 Nakamura-Misaki 開発環境"
        echo "🐍 Python: $(python --version)"
        echo ""
        echo "💡 開発時はuvまたはpip installで依存関係を管理してください"
      '';
    };

    # NixOSモジュール（本番デプロイ用）
    nixosModules.default = { config, lib, pkgs, ... }:
    let
      cfg = config.services.nakamura-misaki;
      package = self.packages.${system}.nakamura-misaki;
    in {
      options.services.nakamura-misaki = {
        enable = lib.mkEnableOption "Nakamura-Misaki Claude Agent Service";

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
          description = "PostgreSQL database URL";
        };

        nakamuraUserId = lib.mkOption {
          type = lib.types.str;
          default = "U09AHTB4X4H";
          description = "Slack user ID for Nakamura";
        };
      };

      config = lib.mkIf cfg.enable {
        # Main service - Pure Nix (no venv)
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

            # Pure Nixアプローチ: すべての依存関係がNixパッケージに含まれる
            ExecStart = pkgs.writeShellScript "nakamura-start" ''
              # Load secrets from sops-nix
              export SLACK_BOT_TOKEN=$(cat ${config.sops.secrets.slack_bot_token.path})
              export SLACK_SIGNING_SECRET=$(cat ${config.sops.secrets.slack_signing_secret.path})
              export ANTHROPIC_API_KEY=$(cat ${config.sops.secrets.anthropic_api_key.path})

              # Nixパッケージから直接実行
              exec ${package}/bin/nakamura-misaki
            '';

            Restart = "always";
            RestartSec = 10;
            KillMode = "mixed";
            KillSignal = "SIGTERM";
            TimeoutStopSec = 10;

            # Security hardening
            PrivateTmp = true;
            ProtectSystem = "strict";
            ProtectHome = false;
            ReadWritePaths = [
              "/home/noguchilin/.claude"
            ];
          };
        };

        # Tailscale Funnel setup
        systemd.services.nakamura-misaki-funnel = lib.mkIf cfg.enableFunnel {
          description = "Setup Tailscale Funnel for Nakamura-Misaki";
          wantedBy = [ "multi-user.target" ];
          after = [ "tailscaled.service" "nakamura-misaki.service" "tailscale-serve-setup.service" ];

          serviceConfig = {
            Type = "oneshot";
            RemainAfterExit = true;
            User = "noguchilin";

            ExecStart = pkgs.writeShellScript "setup-funnel" ''
              # Wait for services
              while ! ${pkgs.systemd}/bin/systemctl is-active tailscaled.service >/dev/null 2>&1; do
                echo "Waiting for tailscaled..."
                sleep 2
              done

              while ! ${pkgs.systemd}/bin/systemctl is-active nakamura-misaki.service >/dev/null 2>&1; do
                echo "Waiting for nakamura-misaki..."
                sleep 2
              done

              # Enable Funnel
              echo "Setting up Tailscale Funnel for nakamura-misaki on port ${toString cfg.ports.api}..."
              ${pkgs.tailscale}/bin/tailscale funnel --bg --https=443 --set-path=/ ${toString cfg.ports.api}
            '';

            ExecStop = pkgs.writeShellScript "stop-funnel" ''
              echo "Removing Tailscale Funnel for nakamura-misaki..."
              ${pkgs.tailscale}/bin/tailscale funnel --https=443 off || true
            '';
          };
        };
      };
    };
  };
}
