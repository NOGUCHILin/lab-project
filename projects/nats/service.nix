# NATS - High-performance messaging system
{ config, pkgs, lib, ... }:

{
  services.nats = {
    enable = true;
    serverName = "nixos-nats";
    port = 4222;  # クライアント接続用

    settings = {
      # 基本設定
      host = "127.0.0.1";

      # HTTPモニタリング有効化（ダッシュボードで使用）
      http_port = 8222;

      # ログ設定
      debug = false;
      trace = false;
      logtime = true;

      # 接続設定
      max_connections = 1000;
      max_control_line = 512;
      max_payload = 1048576;  # 1MB
    };
  };
}
