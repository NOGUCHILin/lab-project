{ lib, ... }:

{
  options.services.unified-dashboard.developmentMode = lib.mkOption {
    type = lib.types.bool;
    default = false;
    description = "Enable development mode for Unified Dashboard";
  };
}

