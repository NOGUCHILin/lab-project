{ config, lib, ... }:

let has = config ? myServices && config.myServices ? aiGateway; in {
  config = lib.mkIf has {};
}

