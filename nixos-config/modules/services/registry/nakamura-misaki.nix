# Nakamura-Misaki Service - Multi-user Claude Agent
# ベストプラクティス: プロジェクトflake依存を排除、sops-nixで秘密情報管理
{ config, lib, pkgs, ... }:

let
  cfg = config.services.nakamura-misaki;
  projectDir = "/home/noguchilin/projects/nakamura-misaki";
in {
  options.services.nakamura-misaki = {
    enable = lib.mkEnableOption "Nakamura-Misaki Claude Agent Service";

    ports = {
      api = lib.mkOption {
        type = lib.types.port;
        description = "API Backend port";
      };

      adminUI = lib.mkOption {
        type = lib.types.port;
        description = "Admin UI port";
      };

      webhook = lib.mkOption {
        type = lib.types.port;
        description = "Slack Webhook port (exposed via Tailscale Funnel)";
      };
    };

    enforceDeclarative = lib.mkOption {
      type = lib.types.bool;
      default = true;
      description = "Refuse manual systemctl operations";
    };
  };

  config = lib.mkIf cfg.enable {
    # API Backend Service
    systemd.services.nakamura-misaki-api = {
      description = "Nakamura-Misaki API Backend";
      wantedBy = [ "multi-user.target" ];
      after = [ "network.target" ];

      environment = {
        PORT = toString cfg.ports.api;
        PYTHONUNBUFFERED = "1";
        NAKAMURA_USER_ID = "U09AHTB4X4H";
      };

      path = with pkgs; [ nodejs_22 bash coreutils python3 ];

      serviceConfig = {
        Type = "simple";
        User = "noguchilin";
        Group = "users";
        WorkingDirectory = projectDir;

        ExecStart = pkgs.writeShellScript "nakamura-api-start" ''
          # 秘密情報を環境変数に設定（sops-nixで復号化されたファイルから読み込み）
          export SLACK_BOT_TOKEN=$(cat ${config.sops.secrets.slack_bot_token.path})
          export ANTHROPIC_API_KEY=$(cat ${config.sops.secrets.anthropic_api_key.path})

          # venv存在確認
          if [ ! -f ${projectDir}/.venv/bin/python ]; then
            echo "❌ venv not found at ${projectDir}/.venv"
            echo "Run: cd ${projectDir} && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
            exit 1
          fi

          cd ${projectDir}
          source .venv/bin/activate
          exec python -m src.main
        '';

        Restart = "always";
        RestartSec = 10;
        KillMode = "mixed";
        KillSignal = "SIGTERM";
        TimeoutStopSec = 10;

        # セキュリティ設定
        PrivateTmp = true;
        ProtectSystem = "strict";
        ProtectHome = false;  # プロジェクトディレクトリアクセス許可
        ReadWritePaths = [ projectDir ];
      };

      unitConfig = lib.mkIf cfg.enforceDeclarative {
        RefuseManualStop = true;
        RefuseManualStart = true;
      };
    };

    # Admin UI Service
    systemd.services.nakamura-misaki-admin = {
      description = "Nakamura-Misaki Admin UI";
      wantedBy = [ "multi-user.target" ];
      after = [ "network.target" "nakamura-misaki-api.service" ];

      environment = {
        PORT = toString cfg.ports.adminUI;
        HOSTNAME = "127.0.0.1";
        NODE_ENV = "production";
        NEXT_PUBLIC_API_URL = "https://${config.networking.hostName}.${config.networking.domain}:${toString cfg.ports.api}";
      };

      path = with pkgs; [ nodejs_22 bash coreutils ];

      serviceConfig = {
        Type = "simple";
        User = "noguchilin";
        Group = "users";
        WorkingDirectory = "${projectDir}/admin-ui";

        ExecStartPre = pkgs.writeShellScript "nakamura-admin-build" ''
          export PATH=${pkgs.nodejs_22}/bin:$PATH
          export NODE_ENV=production
          export HUSKY=0

          # ビルド済み.nextディレクトリがなければビルド
          if [ ! -d .next ]; then
            echo "📦 Building Admin UI..."
            npm ci --ignore-scripts
            npm run build
          fi
        '';

        ExecStart = pkgs.writeShellScript "nakamura-admin-start" ''
          export PATH=${pkgs.nodejs_22}/bin:$PATH
          exec npm start -- -H 127.0.0.1
        '';

        Restart = "always";
        RestartSec = 10;
        PrivateTmp = true;
        ProtectHome = false;
        ReadWritePaths = [ "${projectDir}/admin-ui" ];
      };

      unitConfig = lib.mkIf cfg.enforceDeclarative {
        RefuseManualStop = true;
        RefuseManualStart = true;
      };
    };
  };
}
