# Musubi Auto Price Adjuster - Automated Price Reduction System
# Runs every 30 minutes to reduce listed product prices by 0.1%
{ config, lib, pkgs, ... }:

let
  cfg = config.services.musubi-adjuster;
  projectDir = "/home/noguchilin/projects/applebuyers_application/musubi-adjuster";
in
{
  options.services.musubi-adjuster = {
    enable = lib.mkEnableOption "Musubi Auto Price Adjuster";

    interval = lib.mkOption {
      type = lib.types.str;
      default = "*:0/30";
      description = "Timer interval (systemd calendar format). Default: every 30 minutes";
    };

    dryRun = lib.mkOption {
      type = lib.types.bool;
      default = true;
      description = "Run in dry-run mode (no actual uploads). Set to false for production";
    };
  };

  config = lib.mkIf cfg.enable {
    # Install required packages system-wide
    environment.systemPackages = with pkgs; [
      python311
      uv
      playwright-driver.browsers.chromium
    ];

    # Systemd service (oneshot execution)
    systemd.services.musubi-adjuster = {
      description = "Musubi Auto Price Adjuster";
      after = [ "network.target" ];

      environment = {
        # Python/uv環境
        PATH = lib.makeBinPath (with pkgs; [
          python311
          uv
          playwright-driver.browsers.chromium
          coreutils
          bash
        ]);

        # Playwright設定
        PLAYWRIGHT_BROWSERS_PATH = "${pkgs.playwright-driver.browsers}";
        PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = "1";

        # 実行モード設定
        DRY_RUN = if cfg.dryRun then "true" else "false";

        # ログ設定
        LOG_LEVEL = "INFO";
        HEADLESS = "true";
      };

      serviceConfig = {
        Type = "oneshot";
        User = "noguchilin";
        Group = "users";
        WorkingDirectory = projectDir;

        # 環境変数ファイルを読み込み（sopsで管理）
        EnvironmentFile = config.sops.secrets.musubi-env.path;

        # uvで実行（venv自動作成・依存インストール）
        ExecStart = pkgs.writeShellScript "musubi-run" ''
          set -e

          echo "🤖 Starting Musubi Auto Price Adjuster..."
          echo "📁 Working directory: ${projectDir}"
          echo "🔧 Mode: ${if cfg.dryRun then "DRY RUN" else "PRODUCTION"}"

          # uvで依存パッケージ確認・インストール
          if [ ! -d ".venv" ]; then
            echo "📦 Creating virtual environment..."
            ${pkgs.uv}/bin/uv venv
          fi

          echo "📦 Syncing dependencies..."
          ${pkgs.uv}/bin/uv sync --frozen

          # Playwright browserインストール確認
          echo "🎭 Checking Playwright browsers..."
          export PLAYWRIGHT_BROWSERS_PATH=${pkgs.playwright-driver.browsers}

          # 実行
          echo "🚀 Running price adjuster..."
          ${pkgs.uv}/bin/uv run python -m src.main

          echo "✅ Musubi Auto Price Adjuster completed"
        '';

        # ログ設定
        StandardOutput = "journal";
        StandardError = "journal";

        # セキュリティ設定
        PrivateTmp = true;
        ProtectHome = false;
        ReadWritePaths = [ projectDir ];
      };
    };

    # Systemd timer (30分ごとに実行)
    systemd.timers.musubi-adjuster = {
      description = "Musubi Auto Price Adjuster Timer";
      wantedBy = [ "timers.target" ];

      timerConfig = {
        # 30分ごとに実行（設定可能）
        OnCalendar = cfg.interval;

        # システム停止中に実行時刻を過ぎた場合、次回起動時に実行
        Persistent = true;

        # タイマー起動後5分後に初回実行
        OnStartupSec = "5min";

        # ランダムな遅延を追加（サーバー負荷分散）
        RandomizedDelaySec = "2min";
      };
    };

    # SOPS secretsの定義
    sops.secrets.musubi-env = {
      sopsFile = ../../../secrets/musubi.yaml;
      owner = "noguchilin";
      group = "users";
      mode = "0400";
    };
  };
}
