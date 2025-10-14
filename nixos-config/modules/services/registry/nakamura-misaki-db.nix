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

    # pgvector extension setup (must be created as superuser)
    # postStartはensureDatabases後に実行される
    postStart = ''
      $PSQL -d nakamura_misaki -c 'CREATE EXTENSION IF NOT EXISTS vector;'
    '';
  };

  # データベース初期化サービス
  systemd.services.nakamura-misaki-init-db = {
    description = "Initialize nakamura-misaki v4.0.0 database";
    after = [ "postgresql.service" ];
    wants = [ "postgresql.service" ];
    wantedBy = [ "multi-user.target" ];

    # 初回のみ実行
    unitConfig = {
      ConditionPathExists = "!/home/noguchilin/projects/lab-project/nakamura-misaki/.db-initialized";
    };

    serviceConfig = {
      Type = "oneshot";
      User = "noguchilin";
      Group = "users";
      WorkingDirectory = "/home/noguchilin/projects/lab-project/nakamura-misaki";

      # 初期化スクリプト実行
      ExecStart = pkgs.writeShellScript "init-nakamura-db" ''
        set -e

        # Database URL (local trust authentication, no password needed)
        export DATABASE_URL="postgresql+asyncpg://nakamura_misaki@localhost:5432/nakamura_misaki"

        # C++ library path for numpy (required by pgvector)
        export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"

        export PATH="${pkgs.python3}/bin:$PATH"

        # プロジェクトディレクトリ（nakamura-misaki API serviceと同じ）
        PROJECT_DIR="/home/noguchilin/projects/lab-project/nakamura-misaki"

        if [ ! -d "$PROJECT_DIR" ]; then
          echo "Error: nakamura-misaki project not found at $PROJECT_DIR"
          exit 1
        fi

        cd "$PROJECT_DIR"

        # データベース初期化（venvのpythonを直接使用）
        if [ -f .venv/bin/python ]; then
          .venv/bin/python scripts/init_db.py
        else
          echo "Error: venv not found at $PROJECT_DIR/.venv"
          exit 1
        fi

        # 初期化完了マーク
        touch "$PROJECT_DIR/.db-initialized"

        echo "✅ Database initialized successfully"
      '';
    };
  };
}
