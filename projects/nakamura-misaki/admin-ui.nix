# Admin UI service - imports from project flake
{ config, pkgs, lib, ... }:

let
  # Import admin-ui flake module
  adminFlake = builtins.getFlake "/home/noguchilin/projects/nakamura-misaki/admin-ui";
  adminModule = adminFlake.nixosModules.default;
in
{
  imports = [ adminModule ];

  # Service will be configured in configuration.nix via services.admin-ui options
}
