# Code Server - Browser-based VS Code
{ config, pkgs, lib, ... }:

{
  services.code-server = {
    enable = true;
    host = "127.0.0.1";
    port = 8889;
    auth = "none"; # Tailscale経由のみなので認証不要
    user = "noguchilin";
    extraArguments = [
      "--disable-telemetry"
      "--disable-update-check"
      "--disable-workspace-trust" # Tailscale経由での信頼性問題を回避
    ];
  };
}
