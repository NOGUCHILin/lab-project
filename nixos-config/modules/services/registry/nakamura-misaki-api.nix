{ config, pkgs, nakamura-misaki, ... }:

{
  # nakamura-misaki API Service（Slack Events API）
  # Force restart on deploy (timestamp: 2025-10-16 12:22)
  systemd.services.nakamura-misaki-api = {
    description = "nakamura-misaki v5.0.0 API Server (Claude Agent SDK)";
    after = [ "network-online.target" "postgresql.service" "nakamura-misaki-init-db.service" ];
    wants = [ "network-online.target" ];
    requires = [ "postgresql.service" ];
    wantedBy = [ "multi-user.target" ];

    serviceConfig = {
      Type = "simple";
      User = "noguchilin";
      Group = "users";
      WorkingDirectory = "/home/noguchilin/projects/lab-project/nakamura-misaki";
      Restart = "always";
      RestartSec = "6s";

      # Run Alembic migrations before starting the server
      ExecStartPre = pkgs.writeShellScript "run-alembic-migrations" ''
        set -e
        cd /home/noguchilin/projects/lab-project/nakamura-misaki

        # Load database URL
        export DATABASE_URL="postgresql+psycopg://nakamura_misaki@localhost:5432/nakamura_misaki"

        # Run migrations (use psycopg for sync operations)
        ${nakamura-misaki.python}/bin/alembic upgrade head
      '';

      # API server起動（buildPythonApplicationパッケージから直接実行）
      ExecStart = pkgs.writeShellScript "start-nakamura-api" ''
        set -e

        # Load secrets
        export SLACK_BOT_TOKEN=$(cat ${config.sops.secrets.slack_bot_token.path})
        export SLACK_SIGNING_SECRET=$(cat ${config.sops.secrets.slack_signing_secret.path})
        export ANTHROPIC_API_KEY=$(cat ${config.sops.secrets.anthropic_api_key.path})
        export DATABASE_URL="postgresql+asyncpg://nakamura_misaki@localhost:5432/nakamura_misaki"

        # v5.0.0 configuration
        export CONVERSATION_TTL_HOURS="24"  # Conversation history TTL

        # Logging configuration
        export LOG_LEVEL="INFO"  # Set to DEBUG for verbose logging

        # C++ library path for numpy (required by pgvector)
        export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"

        # PYTHONPATHに現在のプロジェクトを追加（ソースコードはrsyncで配置）
        export PYTHONPATH="/home/noguchilin/projects/lab-project/nakamura-misaki:$PYTHONPATH"

        # Configure Python logging
        export PYTHONUNBUFFERED=1  # Force unbuffered output for real-time logs

        # Start FastAPI server with uvicorn from Python environment
        # Note: Must use src.adapters.primary.api.app:app (not api:app) since api/ is now a package
        exec ${nakamura-misaki.python}/bin/uvicorn src.adapters.primary.api.app:app \
          --host 127.0.0.1 \
          --port 10000 \
          --log-level info
      '';
    };
  };

  # Tailscale Funnel for external access (port 10000)
  services.tailscale.useRoutingFeatures = "both";
}
