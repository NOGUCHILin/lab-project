{ config, pkgs, ... }:

{
  # ハンドオフリマインダー送信サービス
  systemd.services.nakamura-misaki-reminder = {
    description = "nakamura-misaki v4.0.0 Handoff Reminder Scheduler";
    after = [ "postgresql.service" "network-online.target" ];
    wants = [ "postgresql.service" ];

    serviceConfig = {
      Type = "oneshot";
      User = "noguchilin";  # Changed to noguchilin (same as nakamura-misaki API service)
      Group = "users";
      WorkingDirectory = "/home/noguchilin/projects/lab-project/nakamura-misaki";

      # リマインダー送信スクリプト実行
      ExecStart = pkgs.writeShellScript "send-nakamura-reminders" ''
        set -e

        # Load secrets (same pattern as nakamura-misaki.nix)
        export SLACK_BOT_TOKEN=$(cat ${config.sops.secrets.slack_bot_token.path})
        export ANTHROPIC_API_KEY=$(cat ${config.sops.secrets.anthropic_api_key.path})
        export DATABASE_URL="postgresql+asyncpg://nakamura_misaki@localhost:5432/nakamura_misaki"

        export PATH="${pkgs.python3}/bin:$PATH"

        # Use same project directory as nakamura-misaki API service
        PROJECT_DIR="/home/noguchilin/projects/lab-project/nakamura-misaki"

        if [ ! -d "$PROJECT_DIR" ]; then
          echo "Error: nakamura-misaki project not found at $PROJECT_DIR"
          exit 1
        fi

        cd "$PROJECT_DIR"

        # Activate venv and run reminders
        if [ -f .venv/bin/activate ]; then
          source .venv/bin/activate
        fi

        # リマインダー送信
        python scripts/send_reminders.py
      '';

      # エラー時も継続
      SuccessExitStatus = "0 1";
    };
  };

  # 毎分実行するタイマー
  systemd.timers.nakamura-misaki-reminder = {
    description = "Timer for nakamura-misaki Handoff Reminders";
    wantedBy = [ "timers.target" ];

    timerConfig = {
      # 毎分実行
      OnCalendar = "*:0/1";

      # システム起動時も実行
      Persistent = true;

      # タイマー精度（1秒以内の誤差を許容）
      AccuracySec = "1s";
    };
  };
}
