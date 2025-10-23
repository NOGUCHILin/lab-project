# Code Server for AppleBuyers Content Writers
# Dedicated workspace for article editing (content/ directory, content-draft branch)
{ config, lib, pkgs, ... }:

let
  cfg = config.services.code-server-applebuyers;
in {
  options.services.code-server-applebuyers = {
    enable = lib.mkEnableOption "Code Server for AppleBuyers content writers";

    port = lib.mkOption {
      type = lib.types.port;
      default = 8890;
      description = "Code Server port for AppleBuyers writers";
    };
  };

  config = lib.mkIf cfg.enable {
    systemd.services.code-server-applebuyers = {
      description = "Code Server for AppleBuyers Content Writers";
      wantedBy = [ "multi-user.target" ];
      after = [ "network.target" ];

      environment = {
        SHELL = "${pkgs.bash}/bin/bash";
        TERM = "xterm-256color";
        HOME = "/home/noguchilin";
        USER = "noguchilin";
        LOGNAME = "noguchilin";
      };

      path = [ pkgs.code-server pkgs.nodejs_22 pkgs.git ];

      serviceConfig = {
        Type = "simple";
        User = "noguchilin";
        Group = "users";

        ExecStart = pkgs.writeShellScript "code-server-applebuyers-writer" ''
          # Ensure main branch is checked out
          cd /home/noguchilin/projects/applebuyers_application/public-site
          ${pkgs.git}/bin/git checkout main 2>/dev/null || true

          exec ${pkgs.code-server}/bin/code-server \
            --host 127.0.0.1 \
            --port ${toString cfg.port} \
            --auth none \
            --disable-telemetry \
            --user-data-dir /home/noguchilin/.local/share/code-server-applebuyers-writer \
            /home/noguchilin/projects/applebuyers_application/public-site/content
        '';

        Restart = "always";
        RestartSec = 10;
        PrivateTmp = true;
        ProtectHome = false;
      };
    };
  };
}
