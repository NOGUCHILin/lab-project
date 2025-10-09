{ config, lib, ... }:

let has = config ? myServices && config.myServices ? mumuko; in {
  config = lib.mkIf has {};
}

