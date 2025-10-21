{ config, lib, pkgs, ... }:

let
  # Build full Tailscale domain from networking config
  domain =
    if config.networking ? domain && config.networking.domain != ""
    then "${config.networking.hostName}.${config.networking.domain}"
    else config.networking.hostName;

  # Reference ports from actual service configurations
  cfg = config.services;

  services = {
    dashboard = { port = 3000; path = "/"; name = "Unified Dashboard"; description = "Service monitoring and management"; healthCheck = "/api/health"; icon = "🏠"; };
    codeServer = { port = 8889; path = "/code"; name = "Code Server"; description = "Browser-based VSCode"; healthCheck = "/healthz"; icon = "💻"; };
    n8n = { port = 5678; path = "/n8n"; name = "n8n Workflow"; description = "Workflow automation platform"; healthCheck = "/healthLive"; icon = "🔄"; };
    syncthing = { port = 8384; path = "/syncthing"; name = "Syncthing"; description = "File synchronization"; healthCheck = "/rest/noauth/health"; icon = "🔄"; };
    nats = { port = 8222; path = "/nats"; name = "NATS"; description = "Event-driven messaging"; healthCheck = "/varz"; icon = "📡"; };
    fileManager = { port = cfg.file-manager.port; path = "/files"; name = "File Manager"; description = "Web-based file management"; healthCheck = "/api/public/dl/nopass"; icon = "📁"; };
    nakamuraMisaki = { port = cfg.nakamura-misaki.ports.adminUI; path = "/nakamura"; name = "Nakamura-Misaki"; description = "Multi-user Claude Code Agent - Admin UI"; healthCheck = "/health"; icon = "🤖"; };
    nakamuraMisakiApi = { port = null; path = "/nakamura-api"; name = "Nakamura-Misaki API"; description = "Claude Agent API Backend (Funnel only)"; healthCheck = "/health"; icon = "🔧"; };
    applebuyersWriterEditor = { port = 8890; path = "/applebuyers-writer"; name = "AppleBuyers Writer"; description = "ライター用記事編集"; healthCheck = "/healthz"; icon = "✍️"; };
    applebuyersDevEditor = { port = 8891; path = "/applebuyers-dev"; name = "AppleBuyers Dev"; description = "エンジニア用開発環境"; healthCheck = "/healthz"; icon = "⚙️"; };
    applebuyersPreview = { port = cfg.applebuyers-site.port; path = "/applebuyers-preview"; name = "AppleBuyers Preview"; description = "記事プレビュー"; healthCheck = "/"; icon = "👁️"; };
    nakamuraMisakiDb = { port = null; path = null; name = "nakamura-misaki Database"; description = "PostgreSQL 16 + pgvector for v4.0.0"; healthCheck = null; icon = "🗄️"; };
    nakamuraMisakiReminder = { port = null; path = null; name = "nakamura-misaki Reminder"; description = "Handoff reminder scheduler (runs every minute)"; healthCheck = null; icon = "⏰"; };
  };

  servicesJson = builtins.toJSON (lib.mapAttrs (_: service:
    let
      # Dashboard (port 3000) uses root domain, others use port-based URLs
      # Skip URL generation for services without ports (like DB/timers)
      httpsUrl = if service.port == null then null
        else if service.port == 3000
        then "https://${domain}"
        else "https://${domain}:${toString service.port}";
      httpUrl = if service.port == null then null
        else "http://localhost:${toString service.port}";
      publicUrl = if service.port == null then null
        else if domain == "localhost" then httpUrl else httpsUrl;
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
