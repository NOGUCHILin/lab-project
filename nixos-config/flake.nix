{
  description = "NixOS configuration with Home Manager";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    sops-nix = {
      url = "github:Mic92/sops-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    deploy-rs = {
      url = "github:serokell/deploy-rs";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    # nakamura-misakiのflake参照
    nakamura-misaki = {
      url = "path:../projects/nakamura-misaki";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    # dashboardのflake参照
    dashboard = {
      url = "path:../projects/dashboard";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, home-manager, sops-nix, deploy-rs, nakamura-misaki, dashboard, ... }@inputs:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in
    {
      # Re-export packages from project flakes
      packages.${system} = {
        nakamura-misaki = nakamura-misaki.packages.${system}.default;
        dashboard = dashboard.packages.${system}.default;
      };

      # Developer experience: formatter, devShells, and basic checks
      formatter.${system} = pkgs.alejandra;

      devShells.${system} = {
        # Default lightweight shell. Extend per-project via direnv
        default = pkgs.mkShell { packages = [ ]; };

        # Node.js development shell (per-project usage via `nix develop .#node`)
        node = pkgs.mkShell {
          packages = with pkgs; [
            nodejs_22
            nodePackages.pnpm
          ];
        };

        # Python development shell (per-project usage via `nix develop .#py`)
        py = pkgs.mkShell {
          packages = with pkgs; [
            python3
            uv
          ];
        };
      };

      checks.${system} = {
        # Ensure the NixOS system evaluates and builds toplevel
        nixosSystem = self.nixosConfigurations.home-lab-01.config.system.build.toplevel;
      } // (deploy-rs.lib.${system}.deployChecks self.deploy);

      nixosConfigurations = {
        home-lab-01 = nixpkgs.lib.nixosSystem {
          system = system;
          specialArgs = {
            # nakamura-misakiのflakeモジュールとパッケージを渡す
            nakamura-misaki-flake = nakamura-misaki;
            nakamura-misaki-package = self.packages.${system}.nakamura-misaki;
            nakamura-misaki-venv = nakamura-misaki.packages.${system}.venv;
            # dashboardのflakeモジュールとパッケージを渡す
            dashboard-flake = dashboard;
            dashboard-package = self.packages.${system}.dashboard;
          };
          modules = [
            ./hosts/home-lab-01/configuration.nix

            # nakamura-misakiのNixOSモジュールをインポート（Web UIも自動的にインポートされる）
            nakamura-misaki.nixosModules.default

            # dashboardのNixOSモジュールをインポート
            dashboard.nixosModules.default

            # nakamura-misaki-db module with specialArgs
            ({ config, lib, pkgs, nakamura-misaki-venv, ... }: import ./modules/services/registry/nakamura-misaki-db.nix {
              inherit config lib pkgs nakamura-misaki-venv;
            })

            # sops-nix module for secrets management
            sops-nix.nixosModules.sops

            home-manager.nixosModules.home-manager
            {
              home-manager.useGlobalPkgs = true;
              home-manager.useUserPackages = true;
              home-manager.backupFileExtension = "backup";
              home-manager.users.noguchilin = import ./users/noguchilin.nix;
              home-manager.sharedModules = [
                sops-nix.homeManagerModules.sops
              ];
            }
          ];
        };
      };

      deploy = {
        nodes = {
          home-lab-01 = {
            hostname = "home-lab-01"; # Tailscale hostname
            sshUser = "root"; # deploy-rsはroot権限で直接デプロイ
            sshOpts = [ "-p" "22" ];

            profiles.system = {
              user = "root";
              path = deploy-rs.lib.${system}.activate.nixos self.nixosConfigurations.home-lab-01;
            };
          };
        };
      };
    };
}
