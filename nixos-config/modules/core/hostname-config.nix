# Centralized hostname and URL configuration
{ config, lib, ... }:

let
  # Tailscale domain configuration
  tailscaleDomain = "tail4ed625.ts.net";

  # Build full Tailscale hostname
  tailscaleHostname = "${config.networking.hostName}.${tailscaleDomain}";

  # Build HTTPS URL
  tailscaleUrl = "https://${tailscaleHostname}";
in
{
  # Export as module options for other modules to use
  options.services.tailscale.urls = {
    domain = lib.mkOption {
      type = lib.types.str;
      default = tailscaleDomain;
      description = "Tailscale domain";
    };

    hostname = lib.mkOption {
      type = lib.types.str;
      default = tailscaleHostname;
      description = "Full Tailscale hostname";
    };

    baseUrl = lib.mkOption {
      type = lib.types.str;
      default = tailscaleUrl;
      description = "Base HTTPS URL for Tailscale";
    };
  };

  config = {
    # Set the values
    services.tailscale.urls = {
      domain = tailscaleDomain;
      hostname = tailscaleHostname;
      baseUrl = tailscaleUrl;
    };
  };
}