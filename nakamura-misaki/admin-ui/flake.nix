{
  description = "Nakamura-Misaki Admin UI - Next.js Dashboard";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
  in {
    # 開発環境（direnv用）
    devShells.${system}.default = pkgs.mkShell {
      name = "admin-ui-dev";

      buildInputs = with pkgs; [
        nodejs_22
        nodePackages.npm
      ];

      shellHook = ''
        echo "📊 Admin UI 開発環境"
        echo "📦 Node.js: $(node --version)"
        echo "📦 npm: $(npm --version)"
        echo ""
        echo "💡 コマンド:"
        echo "  npm run dev   - 開発サーバー起動"
        echo "  npm run build - プロダクションビルド"
        echo "  npm start     - プロダクションサーバー起動"
      '';
    };

    # NixOSモジュール（本番デプロイ用）
    nixosModules.default = { config, lib, pkgs, ... }:
    let
      cfg = config.services.admin-ui;
      projectDir = "/home/noguchilin/projects/nakamura-misaki/admin-ui";
    in {
      options.services.admin-ui = {
        enable = lib.mkEnableOption "Admin UI Next.js Dashboard";

        port = lib.mkOption {
          type = lib.types.port;
          default = 3000;
          description = "Port for the Next.js development server";
        };

        apiUrl = lib.mkOption {
          type = lib.types.str;
          default = "http://localhost:8010";
          description = "Backend API URL";
        };

        production = lib.mkOption {
          type = lib.types.bool;
          default = false;
          description = "Use production build (next start) instead of development (next dev)";
        };
      };

      config = lib.mkIf cfg.enable {
        systemd.services.admin-ui = {
          description = "Nakamura-Misaki Admin UI Dashboard";
          wantedBy = [ "multi-user.target" ];
          after = [ "network.target" ];

          environment = {
            NODE_ENV = if cfg.production then "production" else "development";
            NEXT_PUBLIC_API_URL = cfg.apiUrl;
            PORT = toString cfg.port;
          };

          path = [ pkgs.nodejs_22 pkgs.nodePackages.npm pkgs.bash pkgs.coreutils ];

          serviceConfig = {
            Type = "simple";
            User = "noguchilin";
            Group = "users";
            WorkingDirectory = projectDir;

            ExecStart = pkgs.writeShellScript "admin-ui-start" ''
              # node_modules存在確認
              if [ ! -d ${projectDir}/node_modules ]; then
                echo "📦 Installing dependencies..."
                cd ${projectDir}
                npm install
              fi

              cd ${projectDir}

              ${if cfg.production then ''
                # Production mode
                if [ ! -d ${projectDir}/.next ]; then
                  echo "🏗️ Building for production..."
                  npm run build
                fi
                exec npm start
              '' else ''
                # Development mode
                exec npm run dev
              ''}
            '';

            Restart = "always";
            RestartSec = 5;
            KillMode = "mixed";
            KillSignal = "SIGTERM";
            TimeoutStopSec = 10;

            # セキュリティ設定
            PrivateTmp = true;
            ProtectSystem = "strict";
            ProtectHome = false;
            ReadWritePaths = [ projectDir ];
          };
        };
      };
    };
  };
}
