{ config, lib, pkgs, ... }:

let
  has = config ? myServices && config.myServices ? codeServer;
  svc = if has then config.myServices.codeServer else { };
in
{
  config = lib.mkIf has {
    services.code-server = {
      enable = true;
      host = lib.mkDefault "127.0.0.1";
      port = svc.port;
      auth = "none";
      user = "noguchilin";
      group = "users";
      extraArguments = [ "/home/noguchilin" ];
      extraEnvironment = {
        SHELL = "${pkgs.bash}/bin/bash";
        TERM = "xterm-256color";
        HOME = "/home/noguchilin";
        USER = "noguchilin";
        LOGNAME = "noguchilin";
      };
    };
  };
}

