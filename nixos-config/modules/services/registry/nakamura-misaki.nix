# Nakamura-Misaki Service - Multi-user Claude Agent
# ベストプラクティス: プロジェクトflake依存を排除、sops-nixで秘密情報管理
{ config, lib, pkgs, ... }:

let
  cfg = config.services.nakamura-misaki;
  projectDir = "/home/noguchilin/projects/lab-project/nakamura-misaki";
in
{
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
    # Redis for nakamura-misaki message queue
    services.redis.servers.nakamura = {
      enable = true;
      port = 6380;
      bind = "127.0.0.1"; # Only local access

      # Persistence settings
      save = [
        [ 900 1 ] # After 900 sec (15 min) if at least 1 key changed
        [ 300 10 ] # After 300 sec (5 min) if at least 10 keys changed
        [ 60 10000 ] # After 60 sec if at least 10000 keys changed
      ];

      # AOF (Append-Only File) for durability
      appendOnly = true;
      appendFsync = "everysec";

      # Security
      requirePass = null; # No password needed (local-only)

      # Performance - use settings attribute set
      settings = {
        maxmemory = "256mb";
        maxmemory-policy = "allkeys-lru";
      };
    };

    # Note: nakamura-misaki-api service is defined in nakamura-misaki-api.nix
    # Note: nakamura-misaki-web-ui (Admin UI) is now provided by web-ui/flake.nix

    # RQ Worker Service for Claude Agent processing
    systemd.services.nakamura-misaki-worker = {
      description = "Nakamura-Misaki RQ Worker (Claude Agent Processing)";
      wantedBy = [ "multi-user.target" ];
      after = [ "network.target" "redis-nakamura.service" ];

      environment = {
        PYTHONUNBUFFERED = "1";
        REDIS_HOST = "127.0.0.1";
        REDIS_PORT = "6380";
      };

      path = with pkgs; [ nodejs_22 bash coreutils python3 ];

      serviceConfig = {
        Type = "simple";
        User = "noguchilin";
        Group = "users";
        WorkingDirectory = projectDir;

        ExecStart = pkgs.writeShellScript "nakamura-worker-start" ''
          # Load secrets
          export SLACK_BOT_TOKEN=$(cat ${config.sops.secrets.slack_bot_token.path})
          export ANTHROPIC_API_KEY=$(cat ${config.sops.secrets.anthropic_api_key.path})

          # venv check
          if [ ! -f ${projectDir}/.venv/bin/python ]; then
            echo "❌ venv not found at ${projectDir}/.venv"
            exit 1
          fi

          # 依存関係が最新か確認（requirements.txtが更新された場合に再インストール）
          if [ -f ${projectDir}/requirements.txt ]; then
            source ${projectDir}/.venv/bin/activate
            pip install -q -r ${projectDir}/requirements.txt
          fi

          cd ${projectDir}
          source .venv/bin/activate
          exec python -m src.workers.claude_worker
        '';

        Restart = "always";
        RestartSec = 10;
        KillMode = "mixed";
        KillSignal = "SIGTERM";
        TimeoutStopSec = 30; # Longer timeout for graceful worker shutdown

        # Security
        PrivateTmp = true;
        ProtectSystem = "strict";
        ProtectHome = false;
        ReadWritePaths = [ projectDir ];
      };

      unitConfig = lib.mkIf cfg.enforceDeclarative {
        RefuseManualStop = true;
        RefuseManualStart = true;
      };
    };
  };
}
