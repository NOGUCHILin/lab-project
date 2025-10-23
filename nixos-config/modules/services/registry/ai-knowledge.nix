{ config, lib, ... }:

let has = config ? myServices && config.myServices ? aiKnowledge; in {
  config = lib.mkIf has { };
}

