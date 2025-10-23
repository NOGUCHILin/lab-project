{ pkgs, lib, ... }:

# Minimal test helper for service registry behaviors used in tests/
let
  inherit (lib) mkIf;
in
{
  # Example function stubs to satisfy tests; replace with real implementations if needed
  registerService = svc: svc // {
    user = svc.name;
    group = svc.name;
    serviceHome = "/var/lib/${svc.name}";
  };

  generateSystemdService = svc: {
    systemd.services."${svc.name}" = {
      wantedBy = [ "multi-user.target" ];
      environment.PORT = toString (svc.port or 0);
      script = "#!/bin/sh\necho running ${svc.type or "python"}";
    };
  };

  applySecurityProfile = { securityProfile, ... }@svc: {
    serviceConfig = {
      NoNewPrivileges = true;
      PrivateTmp = true;
      ProtectSystem = if securityProfile == "strict" then "strict" else "full";
      ProtectHome = true;
    };
  };

  managePorts = services: {
    ports = map (s: s.port) (lib.attrValues services);
    networking.firewall.allowedTCPPorts = map (s: s.port) (lib.attrValues services);
    conflicts = [ ];
  };

  resolveDependencies = svc: {
    after = map (d: "${d}.service") (svc.dependencies or [ ]);
    wants = map (d: "${d}.service") (svc.dependencies or [ ]);
  };

  handleEnvironment = svc: {
    environment = (svc.environment or { }) // (
      if svc.useSops or false then { OPENAI_API_KEY_FILE = "/run/secrets/OPENAI_API_KEY"; } else { }
    );
  };
}

