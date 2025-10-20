{ config, lib, pkgs, nakamura-misaki-venv, ... }:

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
    authentication = lib.mkOverride 10 ''
      local all all trust
      host all all 127.0.0.1/32 trust
      host all all ::1/128 trust
    '';
  };

  # pgvector extension有効化サービス（一度だけ実行）
  systemd.services.nakamura-misaki-enable-vector = {
    description = "Enable pgvector extension in nakamura_misaki database";
    after = [ "postgresql.service" ];
    requires = [ "postgresql.service" ];
    wantedBy = [ "multi-user.target" ];

    unitConfig = {
      ConditionPathExists = "!/var/lib/postgresql/.nakamura-vector-enabled";
    };

    serviceConfig = {
      Type = "oneshot";
      User = "postgres";

      ExecStart = pkgs.writeShellScript "enable-vector" ''
        ${pkgs.postgresql_16}/bin/psql -d nakamura_misaki -c \
          'CREATE EXTENSION IF NOT EXISTS vector;'
        touch /var/lib/postgresql/.nakamura-vector-enabled
        echo "✅ pgvector extension enabled in nakamura_misaki database"
      '';
    };
  };

  # データベース初期化サービス
  systemd.services.nakamura-misaki-init-db = {
    description = "Initialize nakamura-misaki v6.0.0 database";
    after = [ "postgresql.service" "nakamura-misaki-enable-vector.service" ];
    requires = [ "nakamura-misaki-enable-vector.service" ];
    wants = [ "postgresql.service" ];
    wantedBy = [ "multi-user.target" ];

    serviceConfig = {
      Type = "oneshot";
      User = "noguchilin";
      Group = "users";

      # 初期化スクリプト実行（冪等性があるため毎回実行可能）
      ExecStart = pkgs.writeShellScript "init-nakamura-db" ''
        set -e

        # Database URL (local trust authentication, no password needed)
        export DATABASE_URL="postgresql+asyncpg://nakamura_misaki@localhost:5432/nakamura_misaki"

        # C++ library path for numpy (required by pgvector)
        export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"

        # データベース初期化（nakamura-init-db scriptを使用）
        ${nakamura-misaki-venv}/bin/nakamura-init-db

        echo "✅ Database initialization complete"
      '';
    };
  };
}
