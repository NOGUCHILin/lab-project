{
  description = "Unified Dashboard - Service Monitoring & Management";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
  let
    inherit (nixpkgs) lib;

    # Define systems to build for
    forAllSystems = lib.genAttrs [
      "x86_64-linux"
      "aarch64-linux"
      "x86_64-darwin"
      "aarch64-darwin"
    ];

    # Dashboard package per system
    dashboardPkgs = forAllSystems (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
        pkgs.buildNpmPackage {
          pname = "unified-dashboard";
          version = "0.1.0";

          src = ./.;

          # Generate npm dependencies hash
          # Run on NixOS: nix run nixpkgs#prefetch-npm-deps package-lock.json
          npmDepsHash = "sha256-A+QujJnwZNTLXx2BDdLRtPqkmKEI77g8welPn9AGrp8=";

          # Set environment for build
          NODE_ENV = "production";
          HUSKY = "0";  # Disable husky git hooks

          # Build phase
          buildPhase = ''
            runHook preBuild

            export HOME=$TMPDIR
            npm run build

            runHook postBuild
          '';

          # Install phase - copy built files to output
          installPhase = ''
            runHook preInstall

            mkdir -p $out

            # Copy Next.js build output
            cp -r .next $out/
            cp -r public $out/
            cp -r node_modules $out/

            # Copy package files needed for runtime
            cp package.json $out/
            cp package-lock.json $out/

            # Copy Next.js config
            cp next.config.js $out/

            runHook postInstall
          '';

          # Runtime dependencies
          nativeBuildInputs = with pkgs; [
            nodejs_22
          ];

          meta = with lib; {
            description = "Unified service monitoring dashboard";
            homepage = "https://github.com/NOGUCHILin/lab-project";
            license = licenses.mit;
            maintainers = [ ];
            platforms = platforms.all;
          };
        }
    );

  in {
    # Export packages
    packages = forAllSystems (system: {
      default = dashboardPkgs.${system};
      dashboard = dashboardPkgs.${system};
    });

    # Development shells
    devShells = forAllSystems (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        default = pkgs.mkShell {
          name = "dashboard-dev";

          packages = with pkgs; [
            nodejs_22
            nodePackages.npm
          ];

          shellHook = ''
            echo "📊 Dashboard 開発環境"
            echo "📦 Node.js: ${pkgs.nodejs_22.version}"
            echo ""
            echo "💡 開発コマンド:"
            echo "   npm run dev       - 開発サーバー起動"
            echo "   npm run build     - プロダクションビルド"
            echo "   npm run test      - Playwrightテスト"
          '';
        };
      }
    );

    # NixOS module for deployment
    nixosModules.default = { config, lib, pkgs, ... }:
    let
      cfg = config.services.dashboard;
      # Use the package built for the current system
      package = self.packages.${pkgs.system}.default;
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

          serviceConfig = {
            Type = "simple";
            User = "noguchilin";
            Group = "users";
            WorkingDirectory = "${package}";

            # Execute from Nix package (no build needed - already built in derivation)
            ExecStart = pkgs.writeShellScript "dashboard-start" ''
              export PATH=${pkgs.nodejs_22}/bin:$PATH
              cd ${package}
              exec ${pkgs.nodejs_22}/bin/node ${package}/node_modules/.bin/next start -p ${toString cfg.port}
            '';

            Restart = "always";
            RestartSec = 10;

            # Security hardening
            PrivateTmp = true;
            ProtectSystem = "strict";
            ProtectHome = true;
            ReadOnlyPaths = [ package ];
          };

          unitConfig = lib.mkIf cfg.enforceDeclarative {
            RefuseManualStop = true;
            RefuseManualStart = true;
          };
        };
      };
    };
  };
}
