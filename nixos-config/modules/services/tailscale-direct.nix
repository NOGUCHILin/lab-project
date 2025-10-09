# Tailscale Direct Service Access
# 各サービスを直接ポートで公開する設定
{ config, pkgs, lib, ... }:

let
  # 中央レジストリ（registry/default.nix）で定義されたサービス一覧
  services = config.myServices;
  # Avoid recursion on environment.sessionVariables: read process env first, fallback to hostName
  tailscaleDomain = let d = builtins.getEnv "TAILSCALE_DOMAIN"; in
    if d != "" then d else (config.networking.hostName or "tailnet.local");
in {
  # Tailscale設定
  services.tailscale = {
    enable = true;
    useRoutingFeatures = lib.mkForce "server";
  };

  # ファイアウォール設定 - 各サービスのポートを開放
  networking.firewall = {
    # Tailscaleインターフェースを信頼
    trustedInterfaces = [ "tailscale0" ];
    
    # 各サービスのポートを開放
    allowedTCPPorts = lib.unique (
      lib.mapAttrsToList (name: service: service.port) services
    );
  };

  # Tailscale Serve設定用スクリプト
  environment.systemPackages = with pkgs; [
    (writeScriptBin "setup-tailscale-direct" ''
      #!${pkgs.bash}/bin/bash
      echo "Setting up Tailscale direct service access..."
      
      # ダッシュボード (メインサービス)
      tailscale serve --bg --https 443 http://localhost:3005
      echo "✓ Dashboard on https://${tailscaleDomain}/"
      
      # 各サービスを個別ポートで公開
      ${lib.concatStringsSep "\n" (
        lib.mapAttrsToList (name: service:
          if service.port != 3005 then
            ''
              tailscale serve --bg --https ${toString service.port} http://localhost:${toString service.port}
              echo "✓ ${service.name} on https://${tailscaleDomain}:${toString service.port}/"
            ''
          else ""
        ) services
      )}
      
      echo "Setup complete! Services are available at their respective ports."
    '')
    
    (writeScriptBin "check-services" ''
      #!${pkgs.bash}/bin/bash
      echo "=== Service Status Check ==="
      ${lib.concatStringsSep "\n" (
        lib.mapAttrsToList (name: service: 
          ''
            echo -n "${service.name} (port ${toString service.port}): "
            if curl -s -o /dev/null -w "%{http_code}" http://localhost:${toString service.port}${service.healthCheck or "/"} | grep -q "200\|302"; then
              echo "✅ OK"
            else
              echo "❌ Failed"
            fi
          ''
        ) services
      )}
    '')
  ];

  # systemd service to setup Tailscale routing on boot
  systemd.services.tailscale-direct-setup = {
    description = "Setup Tailscale direct service access";
    after = [ "tailscaled.service" "network-online.target" ];
    wants = [ "tailscaled.service" "network-online.target" ];
    wantedBy = [ "multi-user.target" ];
    
    serviceConfig = {
      Type = "oneshot";
      RemainAfterExit = true;
      ExecStart = "${pkgs.bash}/bin/bash -c 'sleep 10 && /run/current-system/sw/bin/setup-tailscale-direct'";
    };
  };
}
