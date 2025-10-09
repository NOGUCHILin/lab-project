{ config, lib, ... }:

let has = config ? myServices && config.myServices ? realtime; in {
  config = lib.mkIf has {};
}

