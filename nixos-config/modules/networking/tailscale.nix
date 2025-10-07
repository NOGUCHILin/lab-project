# Tailscale VPN サービス（単一責務）
{ config, pkgs, ... }:

{
  # Tailscaleサービス（基本設定）
  services.tailscale = {
    enable = true;
    useRoutingFeatures = "server";  # Funnel使用のためserverモードに変更
  };

  # Tailscaleインターフェース用の基本設定
  networking.firewall = {
    checkReversePath = "loose";
    trustedInterfaces = [ "tailscale0" ];
  };
}