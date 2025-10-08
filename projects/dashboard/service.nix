# Dashboard Service - Unified Service Monitoring (Standalone Mode)
# lab-project統合アーキテクチャ
{ config, lib, pkgs, ... }:

let
  cfg = config.services.dashboard;
  projectDir = "/home/noguchilin/projects/dashboard";
  standaloneDir = "${projectDir}/.next/standalone";
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
      default = false;
      description = "Refuse manual systemctl operations";
    };
  };

  config = lib.mkIf cfg.enable {
    systemd.services.dashboard = {
      description = "Unified Dashboard (production - standalone mode)";
      wantedBy = [ "multi-user.target" ];
      after = [ "network.target" ];

      environment = {
        PORT = toString cfg.port;
        NODE_ENV = "production";
      } // lib.optionalAttrs (cfg.baseUrl != "") {
        NEXT_PUBLIC_BASE_URL = cfg.baseUrl;
      };

      path = [ pkgs.nodejs_22 pkgs.bash pkgs.rsync ];

      serviceConfig = {
        Type = "simple";
        User = "noguchilin";
        Group = "users";
        WorkingDirectory = standaloneDir;

        # Standalone modeビルド + 静的ファイルコピー
        ExecStartPre = pkgs.writeShellScript "dashboard-build" ''
          export PATH=${pkgs.nodejs_22}/bin:${pkgs.bash}/bin:${pkgs.rsync}/bin:$PATH
          export NODE_ENV=production
          export HUSKY=0

          cd ${projectDir}

          # Standaloneビルドが存在しない、またはソースが更新されている場合ビルド
          if [ ! -f ${standaloneDir}/server.js ]; then
            echo "📦 Building Dashboard (standalone mode)..."
            npm ci --ignore-scripts
            npm run build

            # 静的ファイルをstandaloneディレクトリにコピー
            echo "📁 Copying static files..."
            cp -r public ${standaloneDir}/ || true
            cp -r .next/static ${standaloneDir}/.next/ || true
          else
            echo "✅ Standalone build exists"

            # 静的ファイルが存在しない場合のみコピー
            if [ ! -d ${standaloneDir}/public ]; then
              echo "📁 Copying public files..."
              cp -r public ${standaloneDir}/ || true
            fi
            if [ ! -d ${standaloneDir}/.next/static ]; then
              echo "📁 Copying static files..."
              cp -r .next/static ${standaloneDir}/.next/ || true
            fi
          fi
        '';

        # Standalone server.jsを直接起動（next startより高速）
        ExecStart = pkgs.writeShellScript "dashboard-start" ''
          export PATH=${pkgs.nodejs_22}/bin:${pkgs.bash}/bin:$PATH
          cd ${standaloneDir}

          echo "🚀 Starting Dashboard (standalone mode)..."
          exec node server.js
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
