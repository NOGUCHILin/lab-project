{ config, lib, pkgs, ... }:

let
  has = config ? myServices && config.myServices ? nats;
  svc = if has then config.myServices.nats else {};
in {
  config = lib.mkIf has {
    services.nats = {
      enable = true;
      jetstream = true;
      settings.http_port = svc.port;
    };
  };
}

