# AppleBuyers Public Site - Memory-limited Dev Server for Writer Editing
# Realtime preview with hot reload for content writers
{ config, lib, pkgs, ... }:

let
  cfg = config.services.applebuyers-site;
  projectDir = "/home/noguchilin/projects/applebuyers_application/public-site";
in {
  options.services.applebuyers-site = {
    enable = lib.mkEnableOption "AppleBuyers Public Site dev server";

    port = lib.mkOption {
      type = lib.types.port;
      description = "Dev server port for live preview";
    };

    memoryLimit = lib.mkOption {
      type = lib.types.int;
      default = 768;
      description = "Node.js memory limit in MB";
    };
  };

  config = lib.mkIf cfg.enable {
    systemd.services.applebuyers-site = {
      description = "AppleBuyers Public Site (dev server with memory limit)";
      wantedBy = [ "multi-user.target" ];
      after = [ "network.target" ];

      environment = {
        PORT = toString cfg.port;
        NODE_ENV = "development";
        NODE_OPTIONS = "--max-old-space-size=${toString cfg.memoryLimit}";
        HUSKY = "0";
      };

      path = [ pkgs.nodejs_22 pkgs.nodePackages.pnpm pkgs.bash pkgs.coreutils ];

      serviceConfig = {
        Type = "simple";
        User = "noguchilin";
        Group = "users";
        WorkingDirectory = projectDir;

        # 依存関係インストール + ポートクリーンアップ（pnpm対応版）
        ExecStartPre = pkgs.writeShellScript "applebuyers-install" ''
          export PATH=${pkgs.nodejs_22}/bin:${pkgs.nodePackages.pnpm}/bin:${pkgs.bash}/bin:${pkgs.procps}/bin:${pkgs.coreutils}/bin:$PATH
          export HUSKY=0

          # Port cleanup
          echo "🧹 Cleaning up port ${toString cfg.port}..."
          pkill -f "next.*${toString cfg.port}" || true
          sleep 1

          # 依存関係の確実な更新（package.json/pnpm-lock.yamlのハッシュチェック）
          PACKAGE_HASH=""
          if [ -f "package.json" ] && [ -f "pnpm-lock.yaml" ]; then
            PACKAGE_HASH=$(cat package.json pnpm-lock.yaml | md5sum | cut -d' ' -f1)
          fi

          INSTALLED_HASH=""
          if [ -f ".pnpm-install-hash" ]; then
            INSTALLED_HASH=$(cat .pnpm-install-hash)
          fi

          # ハッシュが異なる、またはnode_modulesがない場合は再インストール
          if [ "$PACKAGE_HASH" != "$INSTALLED_HASH" ] || [ ! -d "node_modules" ]; then
            echo "📦 Installing/updating dependencies with pnpm..."
            echo "Previous hash: $INSTALLED_HASH"
            echo "Current hash:  $PACKAGE_HASH"
            rm -rf node_modules .next
            pnpm install --frozen-lockfile --ignore-scripts
            echo "$PACKAGE_HASH" > .pnpm-install-hash
            echo "✅ Dependencies updated"
          else
            echo "✅ Dependencies up to date (hash: $PACKAGE_HASH)"
          fi
        '';

        ExecStart = pkgs.writeShellScript "applebuyers-dev" ''
          export PATH=${pkgs.nodejs_22}/bin:${pkgs.nodePackages.pnpm}/bin:${pkgs.bash}/bin:$PATH
          cd ${projectDir}
          echo "🚀 Starting AppleBuyers dev server on port ${toString cfg.port} (memory limit: ${toString cfg.memoryLimit}MB)"
          exec pnpm exec next dev -H 127.0.0.1 -p ${toString cfg.port}
        '';

        Restart = "always";
        RestartSec = 10;
        PrivateTmp = true;
        ProtectHome = false;
        ReadWritePaths = [ projectDir ];
      };
    };
  };
}
