{ config, lib, ... }:

let has = config ? myServices && config.myServices ? aiAgents; in {
  config = lib.mkIf has { };
}

