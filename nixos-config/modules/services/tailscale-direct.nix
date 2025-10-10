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
      export PATH=${pkgs.tailscale}/bin:$PATH
      echo "Setting up Tailscale direct service access..."

      # ダッシュボード (メインサービス)
      tailscale serve --bg --https 443 http://localhost:3000
      echo "✓ Dashboard on https://${tailscaleDomain}/"

      # 各サービスを個別ポートで公開
      ${lib.concatStringsSep "\n" (
        lib.mapAttrsToList (name: service:
          if service.port != 3000 then
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
      export PATH=${pkgs.curl}/bin:$PATH
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
    requires = [ "tailscaled.service" ];
    wantedBy = [ "multi-user.target" ];

    serviceConfig = {
      Type = "oneshot";
      RemainAfterExit = true;
      ExecStart = pkgs.writeShellScript "tailscale-serve-setup" ''
        export PATH=${pkgs.tailscale}/bin:${pkgs.coreutils}/bin:$PATH

        # Wait for tailscaled to be ready
        for i in {1..30}; do
          if tailscale status &>/dev/null; then
            break
          fi
          echo "Waiting for tailscaled... ($i/30)"
          sleep 1
        done

        # Setup Tailscale Serve for all registered services (Tailscaleネットワーク内のみ)
        ${lib.concatStringsSep "\n" (
          lib.mapAttrsToList (name: service:
            if service.port == 3000 then
              # Dashboard on main HTTPS port (tailnet only)
              "tailscale serve --bg --https 443 http://localhost:${toString service.port}"
            else
              # Other services on their respective ports (tailnet only)
              "tailscale serve --bg --https ${toString service.port} http://localhost:${toString service.port}"
          ) services
        )}

        # Funnel設定: nakamura-misaki API（ポート8010）のみインターネット公開
        # Slack Webhook用に専用ポートを公開
        tailscale funnel --bg --https ${toString services.nakamuraMisakiApi.port} http://localhost:${toString services.nakamuraMisakiApi.port}

        echo "✅ Tailscale Serve configured for all services"
        echo "✅ Tailscale Funnel configured for nakamura-misaki API (port ${toString services.nakamuraMisakiApi.port})"
      '';
      # Restart on failure
      Restart = "on-failure";
      RestartSec = "10s";
    };
  };
}
