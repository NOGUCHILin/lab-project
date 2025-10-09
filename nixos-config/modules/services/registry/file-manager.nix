{ config, lib, ... }:

let has = config ? myServices && config.myServices ? fileManager; in {
  config = lib.mkIf has {};
}

