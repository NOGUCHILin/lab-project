# AppleBuyers Article Editor - Code Server instance
# Dedicated Code Server for AppleBuyers article editing
{ config, pkgs, lib, ... }:

let
  cfg = config.services.applebuyers-code-server;
  articlesDir = "/home/noguchilin/projects/applebuyers_application/public-site/content/articles";
in {
  options.services.applebuyers-code-server = {
    enable = lib.mkEnableOption "AppleBuyers Article Editor (Code Server)";

    port = lib.mkOption {
      type = lib.types.port;
      default = 8890;
      description = "Code Server port for AppleBuyers article editing";
    };
  };

  config = lib.mkIf cfg.enable {
    systemd.services.applebuyers-code-server = {
      description = "AppleBuyers Article Editor (Code Server)";
      wantedBy = [ "multi-user.target" ];
      after = [ "network.target" ];

      environment = {
        HOME = "/home/noguchilin";
      };

      serviceConfig = {
        Type = "simple";
        User = "noguchilin";
        Group = "users";
        WorkingDirectory = articlesDir;

        ExecStart = "${pkgs.code-server}/bin/code-server --bind-addr 127.0.0.1:${toString cfg.port} --user-data-dir /home/noguchilin/.local/share/applebuyers-code-server --auth none --disable-telemetry --disable-update-check --disable-workspace-trust ${articlesDir}";

        Restart = "always";
        RestartSec = 10;
        PrivateTmp = true;
        ProtectHome = false;
      };
    };

    # ファイアウォール設定（ローカルのみ）
    # Tailscale Serveで公開するため、ファイアウォールは不要
  };
}
