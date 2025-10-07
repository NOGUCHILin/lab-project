# Edit this configuration file to define what should be installed on
# your system.  Help is available in the configuration.nix(5) man page
# and in the NixOS manual (accessible by running 'nixos-help').

{ config, pkgs, ... }:

{
  imports =
    [ # Include the results of the hardware scan.
      ./hardware-configuration.nix
      # Common settings for all hosts
      ../../modules/common.nix

      # Core modules (基盤設定)
      ../../modules/core/port-management.nix      # Centralized port configuration (MUST BE FIRST)
      ../../modules/core/hostname-config.nix      # Hostname and URL configuration
      ../../modules/core/secrets.nix              # Secrets management with sops-nix
      ../../modules/core/ssh-secure.nix           # SSH secure configuration
      ../../modules/core/firewall-secure.nix      # Firewall security rules
      ../../modules/core/project-structure.nix   # Project directory management

      # Networking modules (ネットワーク設定)
      ../../modules/networking/tailscale.nix      # Tailscale VPN service
      ../../modules/networking/tailscale-serve.nix # Tailscale Serve configuration

      # Service modules (アプリケーションサービス)
      ../../modules/security/cli-guards.nix          # CLI guards (soft blacklist)
    ];

  # Bootloader.
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.hostName = "home-lab-01"; # Define your hostname.
  # networking.wireless.enable = true;  # Enables wireless support via wpa_supplicant.

  # Configure network proxy if necessary
  # networking.proxy.default = "http://user:password@proxy:port/";
  # networking.proxy.noProxy = "127.0.0.1,localhost,internal.domain";

  # Enable networking
  #   networking.networkmanager.enable = true;

  # Set your time zone.
  #   time.timeZone = "Asia/Tokyo";

  # Select internationalisation properties.
  i18n.defaultLocale = "en_US.UTF-8";

  i18n.extraLocaleSettings = {
    LC_ADDRESS = "en_US.UTF-8";
    LC_IDENTIFICATION = "en_US.UTF-8";
    LC_MEASUREMENT = "en_US.UTF-8";
    LC_MONETARY = "en_US.UTF-8";
    LC_NAME = "en_US.UTF-8";
    LC_NUMERIC = "en_US.UTF-8";
    LC_PAPER = "en_US.UTF-8";
    LC_TELEPHONE = "en_US.UTF-8";
    LC_TIME = "ja_JP.UTF-8";
  };

  # Enable the X11 windowing system.
  services.xserver.enable = true;

  # Enable the GNOME Desktop Environment.
  services.displayManager.gdm.enable = true;
  services.desktopManager.gnome.enable = true;

  # Configure keymap in X11
  services.xserver.xkb = {
    layout = "us";
    variant = "";
  };

  # Enable CUPS to print documents.
  services.printing.enable = true;

  # Enable sound with pipewire.
  services.pulseaudio.enable = false;
  security.rtkit.enable = true;
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    alsa.support32Bit = true;
    pulse.enable = true;
    # If you want to use JACK applications, uncomment this
    #jack.enable = true;

    # use the example session manager (no others are packaged yet so this is enabled by default,
    # no need to redefine it in your config for now)
    #media-session.enable = true;
  };

  # Enable touchpad support (enabled default in most desktopManager).
  # services.xserver.libinput.enable = true;

  # サービス設定 - ベストプラクティス: sops-nix & 分離アーキテクチャ

  # Dashboard設定
  services.dashboard = {
    enable = true;
    port = 3000;
    baseUrl = config.services.tailscale.urls.baseUrl;
    enforceDeclarative = false;  # 開発中はfalse
  };

  # Nakamura-Misaki設定
  services.nakamura-misaki = {
    enable = true;
    ports = {
      api = 8010;
      adminUI = 3002;
      webhook = 10000;
    };
    enforceDeclarative = false;  # 開発中はfalse
  };

  # AppleBuyers Public Site Preview設定
  services.applebuyers-public-site-dev = {
    enable = true;
    port = 13005;
  };

  # AppleBuyers Article Editor設定
  services.applebuyers-code-server = {
    enable = true;
    port = 8890;
  };


  # Define a user account. Don't forget to set a password with 'passwd'.
  users.users.noguchilin = {
    isNormalUser = true;
    description = "noguchilin";
    extraGroups = [ "networkmanager" "wheel" "systemd-journal" ];
    packages = with pkgs; [
    #  thunderbird
    ];
    openssh.authorizedKeys.keys = [
      "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMLiIuIMFlbVcZQAJCpSj8xvZe2dqSH+wvVkUJhNZmMf noguchilin1103@gmail.com"
    ];
  };

  # Enable automatic login for the user.
  services.displayManager.autoLogin.enable = true;
  services.displayManager.autoLogin.user = "noguchilin";

  # Workaround for GNOME autologin: https://github.com/NixOS/nixpkgs/issues/103746#issuecomment-945091229
  systemd.services."getty@tty1".enable = false;
  systemd.services."autovt@tty1".enable = false;

  # Firefox無効化（使用しない）
  # programs.firefox.enable = true;
  
  # Git設定
  programs.git = {
    enable = true;
    config = {
      user = {
        name = "noguchilin";
        email = "noguchilin@nixos.local";
      };
      init.defaultBranch = "main";
      push.default = "simple";
    };
  };

  # Allow unfree packages
  nixpkgs.config.allowUnfree = true;

  # sudo設定: 必要最小限のコマンドのみパスワードなし
  security.sudo.extraRules = [{
    users = [ "noguchilin" ];
    commands = [
      {
        command = "/run/current-system/sw/bin/nixos-rebuild";
        options = [ "NOPASSWD" ];
      }
      {
        command = "/run/current-system/sw/bin/journalctl";
        options = [ "NOPASSWD" ];
      }
      {
        command = "/run/current-system/sw/bin/sops";
        options = [ "NOPASSWD" ];
      }
    ];
  }];

  # 追加システム設定
  systemd.tmpfiles.rules = [
    # ログディレクトリ（必要時のみ）
  ];

  # journald設定でログアクセスを改善
  services.journald.extraConfig = ''
    SystemMaxUse=1G
    RuntimeMaxUse=512M
    Storage=persistent
  '';

  # Enable Flakes
  nix = {
    settings = {
      experimental-features = [ "nix-command" "flakes" ];
      auto-optimise-store = true;
    };
    gc = {
      automatic = true;
      dates = "weekly";
      options = "--delete-older-than 30d";
    };
  };

  # ポート管理 - シンプル化
  services.portManagement = {
    enable = true;
    autoFirewall = false;
    useInterfaceRules = false;
  };
  
  # プロジェクト構造管理 - 簡素化
  services.projectStructure = {
    enable = true;
  };

  # Note: Nakamura-Misaki configuration moved to line 115-125
  # Old configuration removed to avoid duplication

  # Admin UI is now part of nakamura-misaki service

  # List packages installed in system profile. To search, run:
  # $ nix search wget
  environment.systemPackages = with pkgs; [
    # システム運用に必要な最小限の基本ツールのみ
    vim
    git
    wget
    curl

    # ブラウザとテスト自動化
    chromium
    playwright-driver

    # Node.js環境 - Claude Code用
    nodejs_22
    nodePackages.npm
  ];

  # Some programs need SUID wrappers, can be configured further or are
  # started in user sessions.
  # programs.mtr.enable = true;
  # programs.gnupg.agent = {
  #   enable = true;
  #   enableSSHSupport = true;
  # };

  # Enable direnv
  programs.direnv = {
    enable = true;
    nix-direnv.enable = true;
  };

  # 環境変数設定 - Claude Code対応とPlaywright設定
  environment.localBinInPath = true;
  environment.variables = {
    # UTF-8環境設定
    LANG = "en_US.UTF-8";
    LC_ALL = "en_US.UTF-8";
    # Node.js環境設定
    NODE_PATH = "/run/current-system/sw/lib/node_modules";
    # Playwright設定 - Chromiumパスを宣言的に管理
    PLAYWRIGHT_BROWSERS_PATH = "${pkgs.playwright-driver}/bin";
    PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH = "${pkgs.chromium}/bin/chromium";
  };

  # List services that you want to enable:

  # Syncthing - ファイル同期
  services.syncthing = {
    enable = true;
    user = "noguchilin";
    dataDir = "/home/noguchilin/.syncthing";
    configDir = "/home/noguchilin/.syncthing/.config/syncthing";
    openDefaultPorts = true;
    settings = {
      gui = {
        address = "0.0.0.0:8384";
        insecureAdminAccess = true;
        insecureSkipHostCheck = true;  # Tailscale経由のアクセスを許可
      };
    };
  };

  # Enable the OpenSSH daemon.
  # services.openssh.enable = true;

  # Open ports in the firewall.
  # networking.firewall.allowedTCPPorts = [ ... ];
  # networking.firewall.allowedUDPPorts = [ ... ];
  # Or disable the firewall altogether.
  # networking.firewall.enable = false;

  # This value determines the NixOS release from which the default
  # settings for stateful data, like file locations and database versions
  # on your system were taken. It's perfectly fine and recommended to leave
  # this value at the release version of the first install of this system.
  # Before changing this value read the documentation for this option
  # (e.g. man configuration.nix or on https://nixos.org/nixos/options.html).
  # system.stateVersion = "25.05"; # Managed by common.nix # Did you read the comment?
  
  # SSH設定はtailscale-secure.nixで管理

  # Disable automatic sleep and suspend
    powerManagement = {
      enable = false;
    };

    services.logind = {
      settings = {
        Login = {
          HandleLidSwitch = "ignore";
          IdleAction = "ignore";
          IdleActionSec = "infinity";
          HandleSuspendKey = "ignore";
          HandleHibernateKey = "ignore";
        };
      };
    };

    systemd.targets = {
      sleep.enable = false;
      suspend.enable = false;
      hibernate.enable = false;
    };


}
