# Dashboard Service - Unified Service Monitoring
# lab-project統合アーキテクチャ
{ config, lib, pkgs, ... }:

let
  cfg = config.services.dashboard;
  projectDir = "/home/noguchilin/projects/dashboard";
in {
  options.services.dashboard = {
    enable = lib.mkEnableOption "Unified Dashboard service";

    port = lib.mkOption {
      type = lib.types.port;
      default = 3000;
      description = "Dashboard port (production)";
    };

    baseUrl = lib.mkOption {
      type = lib.types.str;
      default = "";
      description = "Base URL for the application (e.g., Tailscale URL)";
    };

    enforceDeclarative = lib.mkOption {
      type = lib.types.bool;
      default = true;
      description = "Refuse manual systemctl operations";
    };
  };

  config = lib.mkIf cfg.enable {
    systemd.services.dashboard = {
      description = "Unified Dashboard (production)";
      wantedBy = [ "multi-user.target" ];
      after = [ "network.target" ];

      environment = {
        PORT = toString cfg.port;
        NODE_ENV = "production";
        NEXT_DIST_DIR = ".next";
      } // lib.optionalAttrs (cfg.baseUrl != "") {
        NEXT_PUBLIC_BASE_URL = cfg.baseUrl;
      };

      path = [ pkgs.nodejs_22 pkgs.bash ];

      serviceConfig = {
        Type = "simple";
        User = "noguchilin";
        Group = "users";
        WorkingDirectory = projectDir;

        ExecStartPre = pkgs.writeShellScript "dashboard-build" ''
          export PATH=${pkgs.nodejs_22}/bin:${pkgs.bash}/bin:$PATH
          export NODE_ENV=production
          export HUSKY=0

          # ビルド済み.nextディレクトリがなければビルド
          if [ ! -d .next ]; then
            echo "📦 Building Dashboard..."
            npm ci --ignore-scripts
            npm run build
          fi
        '';

        ExecStart = pkgs.writeShellScript "dashboard-start" ''
          export PATH=${pkgs.nodejs_22}/bin:${pkgs.bash}/bin:$PATH
          cd ${projectDir}
          exec node node_modules/.bin/next start -p ${toString cfg.port}
        '';

        Restart = "always";
        RestartSec = 10;
        PrivateTmp = true;
        ProtectHome = false;
        ReadWritePaths = [ projectDir ];
      };

      unitConfig = lib.mkIf cfg.enforceDeclarative {
        RefuseManualStop = true;
        RefuseManualStart = true;
      };
    };
  };
}
