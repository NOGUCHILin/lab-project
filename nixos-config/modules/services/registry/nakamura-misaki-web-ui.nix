{ config, lib, pkgs, ... }:

{
  # Service Registry Definition for Nakamura-Misaki Web UI
  # This file defines the service metadata for the unified dashboard

  config = {
    services.registry.services.nakamuraMisakiWebUI = {
      enable = true;

      # Service metadata
      name = "Nakamura-Misaki Web UI";
      description = "タスク管理AI - 運用管理画面";
      icon = "⚙️";
      category = "ai";

      # Network configuration
      port = 3002;
      path = "/";
      url = "https://${config.networking.hostName}.${config.networking.domain}:3002";
      apiUrl = "http://localhost:3002";

      # Health check
      healthCheck = "/";

      # Tags for filtering and search
      tags = [ "admin" "task-management" "nakamura-misaki" "web-ui" ];

      # Feature list
      features = [
        "タスク一覧・検索"
        "会話履歴閲覧"
        "ユーザー管理"
        "システム統計"
      ];
    };
  };
}
