# Tailscale VPN サービス（単一責務）
{ config, pkgs, ... }:

{
  # Tailscaleサービス（基本設定）
  services.tailscale = {
    enable = true;
    useRoutingFeatures = "client";
  };

  # Tailscaleインターフェース用の基本設定
  networking.firewall = {
    checkReversePath = "loose";
    trustedInterfaces = [ "tailscale0" ];
  };
}