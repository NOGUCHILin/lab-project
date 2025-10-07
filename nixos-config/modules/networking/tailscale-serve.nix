# Tailscale Serve configuration for dashboard
{ config, pkgs, lib, ... }:

{
  # Tailscale Serve設定を宣言的に管理
  systemd.services.tailscale-serve-setup = {
    description = "Setup Tailscale Serve for dashboard";
    after = [
      "tailscaled.service"
      "network-online.target"
      "dashboard.service"  # ダッシュボードの起動を待つ
    ];
    wants = [ "network-online.target" ];
    wantedBy = [ "multi-user.target" ];

    # サービスタイプをoneshotに設定（一度だけ実行）
    serviceConfig = {
      Type = "oneshot";
      RemainAfterExit = true;
      ExecStart = pkgs.writeShellScript "tailscale-serve-setup" ''
        # Wait for Tailscale to be ready
        sleep 5

        # Clear existing configuration
        ${pkgs.tailscale}/bin/tailscale serve reset || true

        # Dashboard - HTTPSデフォルトポート（443）でアクセス可能（本番に固定）
        ${pkgs.tailscale}/bin/tailscale serve --bg --https=443 3000

        # Other services remain on their specific ports
        ${pkgs.tailscale}/bin/tailscale serve --bg --https=8080 8080  # FileBrowser
        ${pkgs.tailscale}/bin/tailscale serve --bg --https=8889 8889  # Code Server
        ${pkgs.tailscale}/bin/tailscale serve --bg --https=8384 https+insecure://localhost:8384  # Syncthing
        ${pkgs.tailscale}/bin/tailscale serve --bg --https=8222 8222  # NATS monitoring

        # Nakamura-Misaki services
        ${pkgs.tailscale}/bin/tailscale serve --bg --https=3002 3002  # Admin UI
        ${pkgs.tailscale}/bin/tailscale serve --bg --https=8010 8010  # API Backend
        ${pkgs.tailscale}/bin/tailscale funnel --bg --https=10000 10000  # Slack Webhook (public)

        # AppleBuyers Public Site Preview
        ${pkgs.tailscale}/bin/tailscale serve --bg --https=13005 13005  # Preview Server

        # AppleBuyers Article Editor (Code Server)
        ${pkgs.tailscale}/bin/tailscale serve --bg --https=8890 8890  # Article Editor
      '';

      # Reset設定（サービス停止時に実行）
      ExecStop = pkgs.writeShellScript "tailscale-serve-reset" ''
        ${pkgs.tailscale}/bin/tailscale serve reset
      '';
    };
  };

  # ダッシュボード開発サーバー用のaliasを環境に追加
  environment.shellAliases = {
    dashboard-dev = "cd ~/projects/dashboard && PORT=3005 NEXT_DIST_DIR=.next-dev npm run dev";
    dashboard-url = "echo 'Dashboard: ${config.services.tailscale.urls.baseUrl}/ (no port needed)'";
  };
}
