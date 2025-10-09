{ config, pkgs, lib, ... }:

{
  # Home Manager needs a bit of information about you and the
  # paths it should manage.
  home.username = "noguchilin";
  home.homeDirectory = "/home/noguchilin";

  # This value determines the Home Manager release that your
  # configuration is compatible with. This helps avoid breakage
  # when a new Home Manager release introduces backwards
  # incompatible changes.
  home.stateVersion = "24.05";

  # Let Home Manager install and manage itself.
  programs.home-manager.enable = true;

  # Packages to install（ユーザー領域のユーティリティ中心）
  home.packages = with pkgs; [
    # 開発ツール
    neovim
    tmux
    ripgrep
    fd
    jq
    yq
    bat
    eza
    zoxide
    fzf
    tree
    htop
    btop

    # Git関連
    gh
    lazygit

    # ユーザー系CLI（必要に応じて）
    codex
    gemini-cli
  ];

  # Git設定
  programs.git = {
    enable = true;
    userName = "noguchilin";
    userEmail = "noguchilin@nixos.local";
    extraConfig = {
      init.defaultBranch = "main";
      pull.rebase = false;
    };
  };

  # Bash設定
  programs.bash = {
    enable = true;
    # グローバルnpmのPATH追加や関数は撤去（再現性向上のため）
    initExtra = ''
    '';
    shellAliases = {
      # 一般的なls系
      ll = "ls -la";
      la = "ls -la"; 
      l = "ls -l";
      
      # 一般的なgit系
      gs = "git status";
      ga = "git add";
      gc = "git commit";
      gp = "git push";
      gl = "git log --oneline";
      
      # 一般的なNixOS系（コミュニティ標準）
      nrs = "sudo nixos-rebuild switch --flake ~/nixos-config#home-lab-01";
      nrt = "sudo nixos-rebuild test --flake ~/nixos-config#home-lab-01";
      nrb = "sudo nixos-rebuild build --flake ~/nixos-config#home-lab-01";
      nru = "nix flake update ~/nixos-config";
      
      # フレンドリーな名前（併用）
      rebuild = "sudo nixos-rebuild switch --flake ~/nixos-config#home-lab-01";
      
      # tmux + Claude Code
      tc = "tmux new-session -A -s claude";
      tl = "tmux list-sessions";
      ta = "tmux attach";
    };
  };

  # Direnv設定
  programs.direnv = {
    enable = true;
    enableBashIntegration = true;
    nix-direnv.enable = true;
  };

  # npmのグローバルprefix運用は廃止（devShellでnpx/pnpm dlxを推奨）

  # XDG Base Directory仕様準拠
  xdg.enable = true;
  xdg.userDirs = {
    enable = true;
    createDirectories = true;
    extraConfig = {
      XDG_PROJECTS_DIR = "$HOME/projects";
    };
  };

  # VS Code設定（必要なら）
  programs.vscode = {
    enable = false;  # 必要ならtrueに
    profiles.default.extensions = with pkgs.vscode-extensions; [
      # bbenoist.nix
      # ms-python.python
    ];
  };

  # GitHub CLI設定（宣言的管理）
  programs.gh = {
    enable = true;
    settings = {
      git_protocol = "ssh";
      prompt = "enabled";
      aliases = {
        co = "pr checkout";
        pv = "pr view";
      };
    };
  };

  # SSH設定（宣言的管理）
  programs.ssh = {
    enable = true;
    matchBlocks = {
      "github.com" = {
        hostname = "github.com";
        user = "git";
        identityFile = "~/.ssh/id_ed25519";
      };
      "*.tail*.ts.net" = {
        user = "noguchilin";
        identityFile = "~/.ssh/id_ed25519";
      };
    };
  };


  # GitHub CLI hosts設定をsops secretsから自動生成
  systemd.user.services.github-cli-setup = {
    Unit = {
      Description = "Setup GitHub CLI authentication from sops";
      After = [ "graphical-session.target" ];
    };
    Service = {
      Type = "oneshot";
      RemainAfterExit = true;
      ExecStart = pkgs.writeShellScript "github-cli-setup" ''
        # Wait for sops secrets to be available
        while [ ! -f /run/secrets/github-token ]; do
          sleep 1
        done
        
        # Create GitHub CLI config directory
        mkdir -p ~/.config/gh
        
        # Generate hosts.yml from sops secrets
        cat > ~/.config/gh/hosts.yml <<EOF
        github.com:
          oauth_token: $(cat /run/secrets/github-token)
          user: $(cat /run/secrets/github-user)
          git_protocol: ssh
        EOF
        
        chmod 600 ~/.config/gh/hosts.yml
      '';
    };
    Install = {
      WantedBy = [ "default.target" ];
    };
  };

  # Code Server情報表示コマンド（宣言的定義）
  home.file.".local/bin/code-server-info" = {
    executable = true;
    text = ''
      #!/usr/bin/env bash
      echo "🚀 Code Server (VS Code in Browser)"
      echo "===================================="
      echo ""
      echo "📱 アクセス方法："
      echo ""
      echo "1. Tailscale経由（推奨）:"
      echo "   http://$(tailscale ip -4 2>/dev/null || echo '100.x.x.x'):8889"
      echo ""
      echo "2. ローカルネットワーク:"
      echo "   http://$(ip -4 addr show | grep 192.168 | awk '{print $2}' | cut -d/ -f1 | head -1):8889"
      echo ""
      echo "🔐 認証: 無効（ローカルネットワークのみ）"
      echo ""
      echo "💡 ヒント:"
      echo "   - フルスクリーンモード: F11"
      echo "   - ターミナル: Ctrl+\` "
      echo "   - すべての設定はNixOSで管理"
    '';
  };

  # SSH key setup from sops
  systemd.user.services.ssh-key-setup = {
    Unit = {
      Description = "Setup SSH keys from sops";
      After = [ "graphical-session.target" ];
    };
    Service = {
      Type = "oneshot";
      RemainAfterExit = true;
      ExecStart = pkgs.writeShellScript "ssh-key-setup" ''
        # Wait for sops secrets to be available
        while [ ! -f /run/secrets/ssh-private-key ]; do
          sleep 1
        done
        
        # Create SSH directory
        mkdir -p ~/.ssh
        chmod 700 ~/.ssh
        
        # Copy SSH private key from sops
        cp /run/secrets/ssh-private-key ~/.ssh/id_ed25519
        chmod 600 ~/.ssh/id_ed25519
        
        # Generate public key from private key
        ${pkgs.openssh}/bin/ssh-keygen -y -f ~/.ssh/id_ed25519 > ~/.ssh/id_ed25519.pub
        chmod 644 ~/.ssh/id_ed25519.pub
      '';
    };
    Install = {
      WantedBy = [ "default.target" ];
    };
  };

  # Serena MCP設定を宣言的管理
  xdg.configFile."serena/config.json" = {
    text = ''
      {
        "host": "localhost",
        "port": 3001,
        "defaultProject": "~/nixos-config",
        "memory": {
          "enabled": true,
          "path": "~/.serena/memory"
        }
      }
    '';
  };

  # Gemini設定を宣言的管理（OAuth使用なので最小限）
  xdg.configFile."gemini/settings.json" = {
    text = ''
      {
        "auth": {
          "type": "gca"
        },
        "selectedAuthType": "oauth-personal"
      }
    '';
  };
}
