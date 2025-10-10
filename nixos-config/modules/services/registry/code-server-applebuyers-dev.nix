# Code Server for AppleBuyers Development (Engineers)
# Full project workspace on main branch
{ config, lib, pkgs, ... }:

let
  cfg = config.services.code-server-applebuyers-dev;
in {
  options.services.code-server-applebuyers-dev = {
    enable = lib.mkEnableOption "Code Server for AppleBuyers development (engineers)";

    port = lib.mkOption {
      type = lib.types.port;
      default = 8891;
      description = "Code Server port for AppleBuyers engineers";
    };
  };

  config = lib.mkIf cfg.enable {
    systemd.services.code-server-applebuyers-dev = {
      description = "Code Server for AppleBuyers Development";
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

        ExecStart = pkgs.writeShellScript "code-server-applebuyers-dev" ''
          # Ensure main branch is checked out
          cd /home/noguchilin/projects/applebuyers_application/public-site
          ${pkgs.git}/bin/git checkout main 2>/dev/null || true

          exec ${pkgs.code-server}/bin/code-server \
            --host 127.0.0.1 \
            --port ${toString cfg.port} \
            --auth none \
            --disable-telemetry \
            --user-data-dir /home/noguchilin/.local/share/code-server-applebuyers-dev \
            /home/noguchilin/projects/applebuyers_application/public-site
        '';

        Restart = "always";
        RestartSec = 10;
        PrivateTmp = true;
        ProtectHome = false;
      };
    };
  };
}
