{ config, lib, pkgs, ... }:

let
  has = config ? myServices && config.myServices ? n8n;
  svc = if has then config.myServices.n8n else {};
in {
  config = lib.mkIf has {
    services.n8n = {
      enable = true;
      openFirewall = false;
      settings = {
        host = lib.mkDefault "127.0.0.1";
        port = svc.port;
      };
    };
  };
}

