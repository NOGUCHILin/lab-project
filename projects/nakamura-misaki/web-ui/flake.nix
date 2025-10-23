{
  description = "Nakamura-Misaki Web UI - Next.js Dashboard";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in
    {
      # Web UI Package (Production Build)
      packages.${system}.default = pkgs.buildNpmPackage {
        pname = "nakamura-misaki-web-ui";
        version = "1.0.0";
        src = ./.;

        # npm dependencies hash
        npmDepsHash = "sha256-Ihb96hIfq1asPsBQsnbEubeivlh6XOzn629OFQxnpmI=";

        # Build Next.js app
        buildPhase = ''
          export NEXT_TELEMETRY_DISABLED=1
          export NODE_ENV=production
          npm run build
        '';

        # Install standalone build to Nix store
        installPhase = ''
          mkdir -p $out

          # Copy standalone server (includes server.js, node_modules, etc.)
          cp -r .next/standalone/* $out/

          # Create .next directory structure
          mkdir -p $out/.next

          # Copy static files
          cp -r .next/static $out/.next/static

          # Copy server directory (pages-manifest.json, etc.)
          if [ -d .next/server ]; then
            cp -r .next/server $out/.next/server
          fi

          # Copy all root-level files from .next (BUILD_ID, manifests, etc.)
          find .next -maxdepth 1 -type f -exec cp {} $out/.next/ \;

          # Copy public files
          cp -r public $out/public
        '';

        meta = {
          description = "Nakamura-Misaki Web UI for task and conversation management";
          license = pkgs.lib.licenses.mit;
        };
      };

      # NixOS Module
      nixosModules.default = { config, lib, pkgs, ... }:
        let
          cfg = config.services.nakamura-misaki-web-ui;
        in
        {
          options.services.nakamura-misaki-web-ui = {
            enable = lib.mkEnableOption "Nakamura-Misaki Web UI";

            port = lib.mkOption {
              type = lib.types.port;
              default = 3002;
              description = "Port for the Web UI server";
            };

            apiUrl = lib.mkOption {
              type = lib.types.str;
              default = "http://localhost:10000";
              description = "Backend API URL";
            };
          };

          config = lib.mkIf cfg.enable {
            systemd.services.nakamura-misaki-web-ui = {
              description = "Nakamura-Misaki Web UI (Next.js)";
              wantedBy = [ "multi-user.target" ];
              after = [ "network.target" "nakamura-misaki-api.service" ];

              environment = {
                NODE_ENV = "production";
                PORT = toString cfg.port;
                NEXT_PUBLIC_API_URL = cfg.apiUrl;
                HOSTNAME = "127.0.0.1";
              };

              serviceConfig = {
                Type = "simple";
                User = "noguchilin";
                Group = "users";
                WorkingDirectory = "${self.packages.${system}.default}";
                ExecStart = "${pkgs.nodejs}/bin/node server.js";

                Restart = "always";
                RestartSec = 5;

                # Security
                PrivateTmp = true;
                ProtectSystem = "strict";
                ProtectHome = false;
              };
            };
          };
        };
    };
}
