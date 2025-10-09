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
      default = 13005;
      description = "Dev server port for live preview";
    };

    memoryLimit = lib.mkOption {
      type = lib.types.int;
      default = 384;
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

      path = [ pkgs.nodejs_22 pkgs.bash ];

      serviceConfig = {
        Type = "simple";
        User = "noguchilin";
        Group = "users";
        WorkingDirectory = projectDir;

        # 依存関係インストール + ポートクリーンアップ
        ExecStartPre = pkgs.writeShellScript "applebuyers-install" ''
          export PATH=${pkgs.nodejs_22}/bin:${pkgs.bash}/bin:${pkgs.procps}/bin:$PATH
          export HUSKY=0

          # Port 13005を使用している既存のプロセスを停止
          echo "🧹 Cleaning up port ${toString cfg.port}..."
          pkill -f "next.*${toString cfg.port}" || true
          sleep 1

          if [ ! -d "node_modules" ]; then
            echo "📦 Installing dependencies..."
            npm ci --ignore-scripts
          else
            echo "✅ Dependencies already installed"
          fi
        '';

        ExecStart = pkgs.writeShellScript "applebuyers-dev" ''
          export PATH=${pkgs.nodejs_22}/bin:${pkgs.bash}/bin:$PATH
          cd ${projectDir}
          echo "🚀 Starting AppleBuyers dev server on port ${toString cfg.port} (memory limit: ${toString cfg.memoryLimit}MB)"
          exec npm run dev:network
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
