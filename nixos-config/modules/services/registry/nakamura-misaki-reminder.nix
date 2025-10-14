{ config, pkgs, ... }:

{
  # ハンドオフリマインダー送信サービス
  systemd.services.nakamura-misaki-reminder = {
    description = "nakamura-misaki v4.0.0 Handoff Reminder Scheduler";
    after = [ "postgresql.service" "network-online.target" ];
    wants = [ "postgresql.service" ];

    serviceConfig = {
      Type = "oneshot";
      User = "nakamura-misaki";
      Group = "nakamura-misaki";
      WorkingDirectory = "/var/lib/nakamura-misaki";

      # 環境変数
      EnvironmentFile = config.sops.secrets."nakamura-misaki/env".path;

      # リマインダー送信スクリプト実行
      ExecStart = pkgs.writeShellScript "send-nakamura-reminders" ''
        set -e

        export PATH="${pkgs.python3}/bin:$PATH"

        PROJECT_DIR="/var/lib/nakamura-misaki/nakamura-misaki"

        if [ ! -d "$PROJECT_DIR" ]; then
          echo "Error: nakamura-misaki project not found at $PROJECT_DIR"
          exit 1
        fi

        cd "$PROJECT_DIR"

        # リマインダー送信
        ${pkgs.python3}/bin/python scripts/send_reminders.py
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
