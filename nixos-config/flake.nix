{
  description = "NixOS統合設定 - lab-project";

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

    # deploy-rs を追加
    deploy-rs = {
      url = "github:serokell/deploy-rs";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, home-manager, sops-nix, deploy-rs, ... }@inputs:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
  in {
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
        modules = [
          ./hosts/home-lab-01/configuration.nix

          # Nginxリバースプロキシ設定
          ./modules/nginx.nix

          # 全サービス定義をprojects/からimport
          ../projects/dashboard/service.nix
          ../projects/nakamura-misaki/service.nix
          # TODO: admin-ui.nixは既存プロジェクトコード統合後に有効化
          # ../projects/nakamura-misaki/admin-ui.nix
          ../projects/code-server/service.nix
          ../projects/filebrowser/service.nix
          ../projects/nats/service.nix
          ./projects/applebuyers-public-site/service.nix
          ./projects/applebuyers-code-server/service.nix

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

    # Allow directly switching the Home Manager config without a full NixOS rebuild
    homeConfigurations = {
      noguchilin = home-manager.lib.homeManagerConfiguration {
        inherit pkgs;
        modules = [
          ./users/noguchilin.nix
        ];
      };
    };

    # deploy-rs configuration
    deploy = {
      nodes = {
        home-lab-01 = {
          hostname = "192.168.11.27";  # または Tailscale hostname
          sshUser = "noguchilin";
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
