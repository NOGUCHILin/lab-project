# Simple Project Structure - YAGNI principles applied
{ config, lib, ... }:

with lib;
let
  cfg = config.services.projectStructure;
in
{
  options.services.projectStructure = {
    enable = mkEnableOption "Simple project structure management";

    basePath = mkOption {
      type = types.str;
      default = "/home/noguchilin/projects";
      description = "Base path for all projects";
    };
  };

  config = mkIf cfg.enable {
    # シンプルなディレクトリ作成のみ
    systemd.tmpfiles.rules = [
      "d ${cfg.basePath} 0755 noguchilin users -"
      "d ${cfg.basePath}/dashboard 0755 noguchilin users -"
    ];
  };
}