# File Manager Service - Filebrowser
{ config, lib, pkgs, ... }:

let
  cfg = config.services.file-manager;
in {
  options.services.file-manager = {
    enable = lib.mkEnableOption "Filebrowser file manager";

    port = lib.mkOption {
      type = lib.types.port;
      description = "Filebrowser port";
    };

    rootDir = lib.mkOption {
      type = lib.types.str;
      default = "/home/noguchilin";
      description = "Root directory for file browsing";
    };
  };

  config = lib.mkIf cfg.enable {
    systemd.services.filebrowser = {
      description = "Filebrowser Web File Manager";
      wantedBy = [ "multi-user.target" ];
      after = [ "network.target" ];

      environment = {
        FB_PORT = toString cfg.port;
        FB_ADDRESS = "127.0.0.1";
        FB_ROOT = cfg.rootDir;
        FB_DATABASE = "/var/lib/filebrowser/filebrowser.db";
        FB_NOAUTH = "true";  # No auth since behind Tailscale
      };

      path = [ pkgs.filebrowser ];

      serviceConfig = {
        Type = "simple";
        User = "noguchilin";
        Group = "users";
        StateDirectory = "filebrowser";

        ExecStart = "${pkgs.filebrowser}/bin/filebrowser --port ${toString cfg.port} --address 127.0.0.1 --root ${cfg.rootDir} --database /var/lib/filebrowser/filebrowser.db --noauth";

        Restart = "always";
        RestartSec = 10;
        PrivateTmp = true;
        ProtectHome = false;
        ReadWritePaths = [ cfg.rootDir "/var/lib/filebrowser" ];
      };
    };
  };
}
