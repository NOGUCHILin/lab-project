# AppleBuyers Public Site - Development Preview Server
# lab-project統合アーキテクチャ
{ config, lib, pkgs, ... }:

let
  cfg = config.services.applebuyers-public-site-dev;
  projectDir = "/home/noguchilin/projects/applebuyers_application/public-site";
in {
  options.services.applebuyers-public-site-dev = {
    enable = lib.mkEnableOption "AppleBuyers Public Site Development Preview Server";

    port = lib.mkOption {
      type = lib.types.port;
      default = 13005;
      description = "Development server port";
    };
  };

  config = lib.mkIf cfg.enable {
    systemd.services.applebuyers-public-site-dev = {
      description = "AppleBuyers Public Site (Dev Server with Hot Reload)";
      wantedBy = [ "multi-user.target" ];
      after = [ "network.target" ];

      environment = {
        PORT = toString cfg.port;
        NODE_ENV = "development";
      };

      path = [ pkgs.nodejs_22 pkgs.pnpm pkgs.bash ];

      serviceConfig = {
        Type = "simple";
        User = "noguchilin";
        Group = "users";
        WorkingDirectory = projectDir;

        ExecStart = pkgs.writeShellScript "applebuyers-public-site-dev-start" ''
          export PATH=${pkgs.nodejs_22}/bin:${pkgs.pnpm}/bin:${pkgs.bash}/bin:$PATH
          cd ${projectDir}

          # 依存関係インストール（初回または package.json更新時）
          if [ ! -d node_modules ] || [ package.json -nt node_modules ]; then
            echo "📦 Installing dependencies..."
            pnpm install
          fi

          # 開発サーバー起動（ホットリロード有効）
          exec pnpm dev --port ${toString cfg.port}
        '';

        Restart = "always";
        RestartSec = 10;
        PrivateTmp = true;
        ProtectHome = false;
        ReadWritePaths = [ projectDir ];
      };
    };

    # ファイアウォール設定
    networking.firewall.allowedTCPPorts = [ cfg.port ];
  };
}
