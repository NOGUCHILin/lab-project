{ config, pkgs, ... }:

{
  # PostgreSQL 16 + pgvector
  services.postgresql = {
    enable = true;
    package = pkgs.postgresql_16;
    enableTCPIP = true;

    # pgvector extension
    extensions = with pkgs.postgresql16Packages; [
      pgvector
    ];

    # データベースとユーザー作成
    ensureDatabases = [ "nakamura_misaki" ];
    ensureUsers = [
      {
        name = "nakamura_misaki";
        ensureDBOwnership = true;
      }
    ];

    # 認証設定
    authentication = pkgs.lib.mkOverride 10 ''
      local all all trust
      host all all 127.0.0.1/32 trust
      host all all ::1/128 trust
    '';
  };

  # nakamura-misakiユーザー作成
  users.users.nakamura-misaki = {
    isSystemUser = true;
    group = "nakamura-misaki";
    home = "/var/lib/nakamura-misaki";
    createHome = true;
  };

  users.groups.nakamura-misaki = {};

  # データベース初期化サービス
  systemd.services.nakamura-misaki-init-db = {
    description = "Initialize nakamura-misaki v4.0.0 database";
    after = [ "postgresql.service" ];
    wants = [ "postgresql.service" ];
    wantedBy = [ "multi-user.target" ];

    # 初回のみ実行
    unitConfig = {
      ConditionPathExists = "!/var/lib/nakamura-misaki/.db-initialized";
    };

    serviceConfig = {
      Type = "oneshot";
      User = "nakamura-misaki";
      Group = "nakamura-misaki";
      WorkingDirectory = "/var/lib/nakamura-misaki";

      # 初期化スクリプト実行
      ExecStart = pkgs.writeShellScript "init-nakamura-db" ''
        set -e

        # Database URL (local trust authentication, no password needed)
        export DATABASE_URL="postgresql+asyncpg://nakamura_misaki@localhost:5432/nakamura_misaki"

        # uvインストール（nakamura-misakiプロジェクト用）
        export PATH="${pkgs.python3}/bin:$PATH"

        # プロジェクトディレクトリ
        PROJECT_DIR="/var/lib/nakamura-misaki/nakamura-misaki"

        if [ ! -d "$PROJECT_DIR" ]; then
          echo "Error: nakamura-misaki project not found at $PROJECT_DIR"
          exit 1
        fi

        cd "$PROJECT_DIR"

        # データベース初期化
        ${pkgs.python3}/bin/python scripts/init_db.py

        # 初期化完了マーク
        touch /var/lib/nakamura-misaki/.db-initialized

        echo "✅ Database initialized successfully"
      '';
    };
  };
}
