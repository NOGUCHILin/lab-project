{ config, pkgs, ... }:

let
  # Python環境をNixで宣言的に定義
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
  # nakamura-misaki API Service（Slack Events API）
  systemd.services.nakamura-misaki-api = {
    description = "nakamura-misaki v4.0.0 API Server";
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
      RestartSec = "5s";

      # API server起動
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

        # Start FastAPI server with uvicorn（Nix管理のPython環境から実行）
        ${pythonEnv}/bin/uvicorn src.adapters.primary.api:app \
          --host 127.0.0.1 \
          --port 10000 \
          --log-level info
      '';
    };
  };

  # Tailscale Funnel for external access (port 10000)
  services.tailscale.useRoutingFeatures = "both";
}
