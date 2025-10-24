{
  description = "Nakamura-Misaki Web UI - Next.js Dashboard";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };

      # Parameterized package builder
      mkWebUI = { apiUrl }: pkgs.buildNpmPackage {
        pname = "nakamura-misaki-web-ui";
        version = "1.0.0";

        # Fetch source from GitHub instead of local directory (for remote-build)
        src = pkgs.fetchFromGitHub
          {
            owner = "NOGUCHILin";
            repo = "lab-project";
            rev = "main"; # Always use latest main branch
            sha256 = "sha256-8YM8Kh1A/F0FeCMSv6BLGJW6NLmzdJ59j1Tu1jWoumw="; # Context Management page (ab46110)
          } + "/projects/nakamura-misaki/web-ui";

        # npm dependencies hash
        npmDepsHash = "sha256-tthnOvNCmcfg4gwa36xos2qOmTO1yMUhSM8QJF2DZCI=";

        # Build Next.js app with API URL injected at build time
        buildPhase = ''
          export NEXT_TELEMETRY_DISABLED=1
          export NODE_ENV=production
          export NEXT_PUBLIC_API_URL="${apiUrl}"
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
    in
    {
      # Default package (for local testing with default API URL)
      packages.${system}.default = mkWebUI {
        apiUrl = "http://localhost:10000";
      };

      # NixOS Module
      nixosModules.default = { config, lib, pkgs, ... }:
        let
          cfg = config.services.nakamura-misaki-web-ui;
          # Build Web UI package with configured API URL
          webui-pkg = mkWebUI { apiUrl = cfg.apiUrl; };
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
              description = "Backend API URL (injected at build time into NEXT_PUBLIC_API_URL)";
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
                HOSTNAME = "127.0.0.1";
              };

              serviceConfig = {
                Type = "simple";
                User = "noguchilin";
                Group = "users";
                WorkingDirectory = "${webui-pkg}";
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
