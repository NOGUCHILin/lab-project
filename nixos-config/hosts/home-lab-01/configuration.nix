# Edit this configuration file to define what should be installed on
# your system.  Help is available in the configuration.nix(5) man page
# and in the NixOS manual (accessible by running 'nixos-help').

{ config, pkgs, ... }:

{
  imports =
    [ # Include the results of the hardware scan.
      ./hardware-configuration.nix
      
      # Core modules (基盤設定)
      ../../modules/core/port-management.nix      # Centralized port configuration (MUST BE FIRST)
      ../../modules/core/secrets.nix              # Secrets management with sops-nix
      ../../modules/core/ssh-secure.nix           # SSH secure configuration
      ../../modules/core/firewall-secure.nix      # Firewall security rules
      ../../modules/core/project-structure.nix   # Project directory management
      
      # Networking modules (ネットワーク設定)
      ../../modules/networking/tailscale.nix      # Tailscale VPN service
      
      # Service modules (アプリケーションサービス)
      # Services (registry + exposure)
      ../../modules/services/registry                     # Centralized service configuration (default.nix)
      ../../modules/services/tailscale-direct.nix         # Tailscale exposure (Serve)
      
      # Services
      ../../modules/services/registry/code-server.nix     # Code Server (VS Code in Browser)
      ../../modules/services/registry/openai-realtime.nix        # OpenAI Realtime Voice Chat (Clean Architecture)
      ../../modules/services/registry/ai-gateway.nix             # AI Gateway - Multi-provider AI API (Clean Architecture)
      ../../modules/services/registry/ai-agents.nix              # AI Agents - CrewAI orchestration (Clean Architecture)
      ../../modules/services/registry/ai-knowledge.nix           # AI Knowledge - RAG with LlamaIndex (Clean Architecture)
      ../../modules/services/registry/n8n.nix                # N8N Workflow Automation Platform
      ../../modules/services/registry/file-manager.nix       # Simple File Manager (registry-based)
      ../../modules/services/registry/mumuko.nix              # Mumuko Service (registry-based)
      ../../modules/services/registry/nats.nix               # NATS Event-Driven Messaging (monitoring via registry)
      # dashboardはflakeのNixOSモジュールから提供（flake.nixで自動import）
      # nakamura-misakiはflakeのNixOSモジュールから提供（flake.nixで自動import）
      # nakamura-misaki-web-uiもflakeのNixOSモジュールから提供（flake.nixで自動import）
      # nakamura-misaki-db.nixもflake.nixでspecialArgs経由でimport（venv依存のため）
      ../../modules/services/registry/applebuyers-site.nix        # AppleBuyers Public Site (dev server)
      ../../modules/services/registry/code-server-applebuyers.nix     # Code Server for AppleBuyers (Writers)
      ../../modules/services/registry/code-server-applebuyers-dev.nix # Code Server for AppleBuyers (Engineers)
    ];

  # Bootloader.
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.hostName = "home-lab-01"; # Define your hostname.
  networking.domain = "tail4ed625.ts.net"; # Tailscale domain
  # networking.wireless.enable = true;  # Enables wireless support via wpa_supplicant.

  # Configure network proxy if necessary
  # networking.proxy.default = "http://user:password@proxy:port/";
  # networking.proxy.noProxy = "127.0.0.1,localhost,internal.domain";

  # Enable networking
  networking.networkmanager.enable = true;

  # Set your time zone.
  time.timeZone = "Asia/Tokyo";

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

  # Dashboard Configuration
  services.dashboard = {
    enable = true;
    port = 3000;
    baseUrl = "https://${config.networking.hostName}.${config.networking.domain}";
  };

  # Nakamura-Misaki Configuration
  services.nakamura-misaki = {
    enable = true;
    enforceDeclarative = false;  # Allow manual restart for testing
    ports = {
      api = 10000;  # API port (Funnel directly exposes this)
      adminUI = 3002;
      webhook = 10000;  # Deprecated, using api port instead
    };

    # Secrets from sops-nix (read at runtime via ExecStartPre)
    # Note: We can't directly pass secrets here, they're loaded in the service script
    slackToken = "";  # Loaded from ${config.sops.secrets.slack_bot_token.path}
    anthropicApiKey = "";  # Loaded from ${config.sops.secrets.anthropic_api_key.path}
    databaseUrl = "postgresql+asyncpg://nakamura_misaki@localhost:5432/nakamura_misaki";
  };

  # Nakamura-Misaki Web UI Configuration
  services.nakamura-misaki-web-ui = {
    enable = true;
    port = 3002;
    apiUrl = "http://localhost:10000";
  };

  # AppleBuyers Configuration
  services.applebuyers-site = {
    enable = true;
    port = 13006;
    memoryLimit = 768;  # 768MB memory limit
  };

  # Code Server for AppleBuyers Writers
  services.code-server-applebuyers = {
    enable = true;
    port = 8890;
  };

  # Code Server for AppleBuyers Engineers
  services.code-server-applebuyers-dev = {
    enable = true;
    port = 8891;
  };

  # File Manager Configuration
  services.file-manager = {
    enable = true;
    port = 9000;
    rootDir = "/home/noguchilin";
  };

  # Define a user account. Don't forget to set a password with 'passwd'.
  users.users.noguchilin = {
    isNormalUser = true;
    description = "noguchilin";
    extraGroups = [ "networkmanager" "wheel" ];
    packages = with pkgs; [
    #  thunderbird
    ];
    openssh.authorizedKeys.keys = [
      "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMLiIuIMFlbVcZQAJCpSj8xvZe2dqSH+wvVkUJhNZmMf noguchilin1103@gmail.com"
    ];
  };

  # Root user SSH key for deploy-rs
  users.users.root.openssh.authorizedKeys.keys = [
    "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIG/tXGwO4MO54lSVf+XIG4RHeqa5WOVFliWPlyA1MAJa github-actions-deploy@lab-project"
  ];

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

  # Enable nix-ld for Python venv with native libraries
  programs.nix-ld = {
    enable = true;
    libraries = with pkgs; [
      # Standard libraries for Python native extensions
      stdenv.cc.cc
      zlib
      zstd
      openssl
      curl
      libssh
      libxml2
      ncurses
      attr
      acl
      bzip2
      xz
      util-linux
      systemd
      # PostgreSQL client libraries
      postgresql
    ];
  };

  # sudo設定: nixos-rebuildとサービス制御をパスワードなし
  security.sudo.extraRules = [{
    users = [ "noguchilin" ];
    commands = [
      {
        command = "/run/current-system/sw/bin/nixos-rebuild";
        options = [ "NOPASSWD" ];
      }
      {
        command = "/run/current-system/sw/bin/systemctl restart dashboard.service";
        options = [ "NOPASSWD" ];
      }
      {
        command = "/run/current-system/sw/bin/systemctl status dashboard.service";
        options = [ "NOPASSWD" ];
      }
      {
        command = "/run/current-system/sw/bin/systemctl stop dashboard.service";
        options = [ "NOPASSWD" ];
      }
      {
        command = "/run/current-system/sw/bin/systemctl start dashboard.service";
        options = [ "NOPASSWD" ];
      }
      {
        command = "/run/current-system/sw/bin/systemctl * dashboard.service";
        options = [ "NOPASSWD" ];
      }
      {
        command = "/run/current-system/sw/bin/systemctl restart openai-realtime.service";
        options = [ "NOPASSWD" ];
      }
      {
        command = "/run/current-system/sw/bin/systemctl status openai-realtime.service";
        options = [ "NOPASSWD" ];
      }
      {
        command = "/run/current-system/sw/bin/systemctl stop openai-realtime.service";
        options = [ "NOPASSWD" ];
      }
      {
        command = "/run/current-system/sw/bin/systemctl start openai-realtime.service";
        options = [ "NOPASSWD" ];
      }
      {
        command = "/run/current-system/sw/bin/systemctl * openai-realtime.service";
        options = [ "NOPASSWD" ];
      }
      {
        command = "/run/current-system/sw/bin/systemctl * applebuyers-site.service";
        options = [ "NOPASSWD" ];
      }
      {
        command = "/run/current-system/sw/bin/systemctl * code-server-applebuyers.service";
        options = [ "NOPASSWD" ];
      }
      {
        command = "/run/current-system/sw/bin/systemctl * nakamura-misaki-api.service";
        options = [ "NOPASSWD" ];
      }
      {
        command = "/run/current-system/sw/bin/systemctl * nakamura-misaki-admin.service";
        options = [ "NOPASSWD" ];
      }
      {
        command = "/run/current-system/sw/bin/systemctl * filebrowser.service";
        options = [ "NOPASSWD" ];
      }
    ];
  }];

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

  # Enable centralized port management
  services.portManagement = {
    enable = true;
    autoFirewall = false;  # FWはregistry/tailscale側で一元管理（YAGNI）
    useInterfaceRules = false;  # Use global rules for simplicity
    # Ports are defined in the module, but can be overridden here if needed
    # ports = {
    #   codeServer = 8889;
    #   unifiedDashboard = 3005;
    #   openaiRealtime = 8891;
    # };
  };
  
  # Enable declarative project structure management
  services.projectStructure = {
    enable = true;
    basePath = "/home/noguchilin/projects";
    autoCleanup = true;  # 古いプロジェクトを自動削除
  };

  # List packages installed in system profile. To search, run:
  # $ nix search wget
  environment.systemPackages = with pkgs; [
    # システム運用に必要な最小限の基本ツールのみ
    vim
    git
    wget
    curl
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
  system.stateVersion = "25.05"; # Did you read the comment?
  
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
