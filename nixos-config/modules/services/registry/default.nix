{ config, lib, pkgs, ... }:

let
  # Resolve domain from process env to avoid config recursion; fallback to hostName or localhost
  domain = let fromEnv = builtins.getEnv "TAILSCALE_DOMAIN"; in
    if fromEnv != "" then fromEnv else (config.networking.hostName or "localhost");

  services = {
    dashboard = { port = 3000; path = "/"; name = "Unified Dashboard"; description = "Service monitoring and management"; healthCheck = "/api/health"; icon = "🏠"; };
    codeServer = { port = 8889; path = "/code"; name = "Code Server"; description = "Browser-based VSCode"; healthCheck = "/healthz"; icon = "💻"; };
    n8n = { port = 5678; path = "/n8n"; name = "n8n Workflow"; description = "Workflow automation platform"; healthCheck = "/healthLive"; icon = "🔄"; };
    syncthing = { port = 8384; path = "/syncthing"; name = "Syncthing"; description = "File synchronization"; healthCheck = "/rest/noauth/health"; icon = "🔄"; };
    nats = { port = 8222; path = "/nats"; name = "NATS"; description = "Event-driven messaging"; healthCheck = "/varz"; icon = "📡"; };
    fileManager = { port = 9000; path = "/files"; name = "File Manager"; description = "Web-based file management"; healthCheck = "/api/public/dl/nopass"; icon = "📁"; };
    nakamuraMisaki = { port = 3002; path = "/nakamura"; name = "Nakamura-Misaki"; description = "Multi-user Claude Code Agent - Admin UI"; healthCheck = "/health"; icon = "🤖"; };
    nakamuraMisakiApi = { port = 8010; path = "/nakamura-api"; name = "Nakamura-Misaki API"; description = "Claude Agent API Backend"; healthCheck = "/health"; icon = "🔧"; };
    applebuyersEditor = { port = 8890; path = "/applebuyers-editor"; name = "AppleBuyers Editor"; description = "記事編集 Code Server"; healthCheck = "/healthz"; icon = "📝"; };
    applebuyersPreview = { port = 13006; path = "/applebuyers-preview"; name = "AppleBuyers Preview"; description = "記事プレビュー"; healthCheck = "/"; icon = "👁️"; };
  };

  servicesJson = builtins.toJSON (lib.mapAttrs (_: service:
    let
      httpsUrl = "https://${domain}${service.path}";
      httpUrl = "http://localhost:${toString service.port}";
      publicUrl = if domain == "localhost" then httpUrl else httpsUrl;
    in service // { url = publicUrl; apiUrl = httpUrl; }
  ) services);
in {
  options.myServices = lib.mkOption {
    type = lib.types.attrs;
    default = services;
    description = "Centralized service configuration";
  };

  config = {
    myServices = services;
    environment.etc."unified-dashboard/services.json" = { text = servicesJson; mode = "0644"; };
    # Do NOT open ports globally here; exposure is handled by Tailscale Serve and/or explicit modules
    environment.sessionVariables.SERVICES_CONFIG = "/etc/unified-dashboard/services.json";
  };
}
