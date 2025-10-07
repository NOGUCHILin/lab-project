{ config, lib, pkgs, ... }:

{
  # 全ホスト共通の基本設定
  
  # システム基本設定
  time.timeZone = lib.mkDefault "Asia/Tokyo";
  i18n.defaultLocale = lib.mkDefault "ja_JP.UTF-8";
  
  # 基本システムパッケージ
  environment.systemPackages = with pkgs; [
    # システム基本ツール
    vim
    git
    curl
    wget
    htop
    tree
    unzip
    
    # Node.js環境
    nodejs
    (writeShellScriptBin "claude" ''
      exec npx @anthropic-ai/claude-code@1.0.119 "$@"
    '')
    
    
    # ネットワークツール
    dig
    nmap
    netcat
    
    # 開発基本ツール
    jq
    yq
  ];
  
  # システムサービス基本設定
  services = {
    # SSH有効化（デフォルト）
    openssh.enable = lib.mkDefault true;
  };
  
  # ネットワーク基本設定
  networking = {
    # ファイアウォール有効化
    firewall.enable = lib.mkDefault true;
    
    # NetworkManager有効化
    networkmanager.enable = lib.mkDefault true;
  };
  
  # セキュリティ基本設定
  security = {
    # sudoタイムアウト延長
    sudo.wheelNeedsPassword = lib.mkDefault true;
  };
  
  # Nix設定
  nix = {
    # 実験的機能有効化
    settings = {
      experimental-features = [ "nix-command" "flakes" ];

      # 自動ガベージコレクション - ディスク空き容量が少なくなったら自動実行
      min-free = lib.mkDefault (5 * 1024 * 1024 * 1024);   # 5GB切ったらGC開始
      max-free = lib.mkDefault (20 * 1024 * 1024 * 1024);  # 20GB確保まで削除
    };

    # 定期ガベージコレクション
    gc = {
      automatic = lib.mkDefault true;
      dates = lib.mkDefault "daily";  # 毎日実行（容量問題対策）
      options = lib.mkDefault "--delete-older-than 7d";  # 7日以上古いものを削除
    };
  };

  # システム世代の制限（古い世代が無限に溜まるのを防ぐ）
  boot.loader.systemd-boot.configurationLimit = lib.mkDefault 10;
  
  # システム状態バージョン
  system.stateVersion = lib.mkDefault "23.11";
}
