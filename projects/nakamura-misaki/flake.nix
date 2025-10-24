{
  description = "Nakamura-Misaki - Multi-User Claude Code Agent Service (uv2nix)";
  # Force flake rebuild to pick up changes (2025-10-24: migration idempotency fix)

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    # Web UI
    web-ui = {
      url = "path:./web-ui";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, uv2nix, pyproject-nix, pyproject-build-systems, web-ui }:
    let
      inherit (nixpkgs) lib;

      # Define systems to build for
      forAllSystems = lib.genAttrs [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      # Load workspace from uv.lock
      workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

      # Create overlay from uv2nix workspace
      overlay = workspace.mkPyprojectOverlay {
        sourcePreference = "wheel"; # Prefer wheels for faster builds
      };

      # Python sets per system
      pythonSets = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          inherit (pkgs) python312;

          # Extend Python package set with uv2nix overlay
          pythonSet = (pkgs.callPackage pyproject-nix.build.packages {
            python = python312;
          }).overrideScope (lib.composeManyExtensions [
            pyproject-build-systems.overlays.default
            overlay
          ]);
        in
        pythonSet
      );

      # Application package per system
      nakamuraMisakiPkgs = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          pythonSet = pythonSets.${system};

          # Create virtual environment with all dependencies
          venv = pythonSet.mkVirtualEnv "nakamura-misaki-env" workspace.deps.default;

          # Build application derivation
          inherit (pkgs.callPackage pyproject-nix.build.util { }) mkApplication;
        in
        mkApplication {
          inherit venv;
          package = pythonSet.nakamura-misaki;
        }
      );

    in
    {
      # Export packages
      packages = forAllSystems (system: {
        default = nakamuraMisakiPkgs.${system};
        nakamura-misaki = nakamuraMisakiPkgs.${system};

        # Web UI package
        web-ui = web-ui.packages.${system}.default;

        # Also export the virtual environment for debugging
        venv = pythonSets.${system}.mkVirtualEnv "nakamura-misaki-env" workspace.deps.default;
      });

      # Development shells
      devShells = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          pythonSet = pythonSets.${system};
          venv = pythonSet.mkVirtualEnv "nakamura-misaki-dev-env" workspace.deps.all;
        in
        {
          default = pkgs.mkShell {
            name = "nakamura-misaki-dev";

            packages = [
              pkgs.uv
              venv
            ];

            shellHook = ''
              echo "🤖 Nakamura-Misaki 開発環境 (uv2nix)"
              echo "🐍 Python: ${pkgs.python312.version}"
              echo ""
              echo "💡 uv コマンドで依存関係を管理してください"
              echo "   uv lock       - 依存関係をロック"
              echo "   uv sync       - 依存関係を同期"
            '';
          };
        }
      );

      # NixOS module for deployment
      nixosModules.default = { config, lib, pkgs, ... }:
        let
          cfg = config.services.nakamura-misaki;
          # Use the package built for the current system
          package = self.packages.${pkgs.system}.default;
        in
        {
          # Import Web UI module
          imports = [
            web-ui.nixosModules.default
          ];

          options.services.nakamura-misaki = {
            enable = lib.mkEnableOption "Nakamura-Misaki Claude Agent Service";

            ports = {
              api = lib.mkOption {
                type = lib.types.port;
                default = 10000;
                description = "API Backend port";
              };

              adminUI = lib.mkOption {
                type = lib.types.port;
                default = 3002;
                description = "Admin UI port (currently not used)";
              };

              webhook = lib.mkOption {
                type = lib.types.port;
                default = 10000;
                description = "Deprecated: use ports.api instead";
              };
            };

            enforceDeclarative = lib.mkOption {
              type = lib.types.bool;
              default = false;
              description = "Refuse manual systemctl operations";
            };

            slackToken = lib.mkOption {
              type = lib.types.str;
              default = "";
              description = "Slack bot token (use sops for secrets)";
            };

            anthropicApiKey = lib.mkOption {
              type = lib.types.str;
              default = "";
              description = "Anthropic API key (use sops for secrets)";
            };

            databaseUrl = lib.mkOption {
              type = lib.types.str;
              default = "";
              description = "PostgreSQL database URL";
            };

            nakamuraUserId = lib.mkOption {
              type = lib.types.str;
              default = "U09AHTB4X4H";
              description = "Slack user ID for Nakamura";
            };
          };

          config = lib.mkIf cfg.enable {
            # Main service - uv2nix approach
            systemd.services.nakamura-misaki = {
              description = "Nakamura-Misaki Multi-User Claude Code Agent";
              wantedBy = [ "multi-user.target" ];
              after = [ "network.target" "postgresql.service" ];

              environment = {
                PORT = toString cfg.ports.api;
                NAKAMURA_USER_ID = cfg.nakamuraUserId;
                PYTHONUNBUFFERED = "1";
              } // lib.optionalAttrs (cfg.databaseUrl != "") {
                DATABASE_URL = cfg.databaseUrl;
              };

              serviceConfig = {
                Type = "simple";
                User = "noguchilin";
                Group = "users";

                # uv2nix approach: execute from Nix store
                ExecStart = pkgs.writeShellScript "nakamura-start" ''
                  # Load secrets from sops-nix
                  export SLACK_BOT_TOKEN=$(cat ${config.sops.secrets.slack_bot_token.path})
                  export SLACK_SIGNING_SECRET=$(cat ${config.sops.secrets.slack_signing_secret.path})
                  export ANTHROPIC_API_KEY=$(cat ${config.sops.secrets.anthropic_api_key.path})

                  # Execute from Nix package
                  exec ${package}/bin/nakamura-misaki
                '';

                Restart = "on-failure";
                RestartSec = 65; # Wait for TIME_WAIT state to clear (default 60s)
                KillMode = "control-group"; # Ensure all processes are killed
                KillSignal = "SIGTERM";
                TimeoutStopSec = 30; # Give more time for graceful shutdown
                TimeoutStartSec = 60; # Prevent infinite startup loops

                # Security hardening
                PrivateTmp = true;
                ProtectSystem = "strict";
                ProtectHome = false;
                ReadWritePaths = [
                  "/home/noguchilin/.claude"
                ];
              };
            };
          };
        };
    };
}
