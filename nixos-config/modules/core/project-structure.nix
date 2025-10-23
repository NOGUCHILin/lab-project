# Project Structure Management - 宣言的なプロジェクト構造管理
{ config, pkgs, lib, ... }:

with lib;
let
  cfg = config.services.projectStructure;

  # プロジェクト定義
  projects = {
    # AIサービス群
    "ai-gateway" = {
      description = "LiteLLM Multi-provider Gateway";
      owner = "noguchilin";
      group = "users";
    };
    "ai-agents" = {
      description = "CrewAI Agent Orchestration";
      owner = "noguchilin";
      group = "users";
    };
    "ai-knowledge" = {
      description = "LlamaIndex RAG Service";
      owner = "noguchilin";
      group = "users";
    };

    # UI
    "dashboard" = {
      description = "Main Dashboard UI";
      owner = "noguchilin";
      group = "users";
    };

    # データ
    "syncthing-data" = {
      description = "Syncthing Sync Directory";
      owner = "noguchilin";
      group = "syncthing";
    };
  };

  # 廃止されたプロジェクト（自動削除）
  deprecatedProjects = [
    "nixos-dashboard"
    "test-sync"
    "unified-dashboard/.next" # 古いビルドキャッシュ
  ];

  # エイリアス（シンボリックリンク）
  projectAliases = {
    "unified-dashboard" = "dashboard"; # 互換性のため
  };
in
{
  options.services.projectStructure = {
    enable = mkEnableOption "Declarative project structure management";

    basePath = mkOption {
      type = types.str;
      default = "/home/noguchilin/projects";
      description = "Base path for all projects";
    };

    autoCleanup = mkOption {
      type = types.bool;
      default = true;
      description = "Automatically remove deprecated projects";
    };
  };

  config = mkIf cfg.enable {
    # プロジェクトディレクトリの作成
    systemd.tmpfiles.rules =
      # ベースディレクトリ
      [ "d ${cfg.basePath} 0755 noguchilin users - -" ] ++

      # 各プロジェクトディレクトリ
      (mapAttrsToList
        (name: proj:
          "d ${cfg.basePath}/${name} 0755 ${proj.owner} ${proj.group} - -"
        )
        projects) ++

      # シンボリックリンク
      (mapAttrsToList
        (alias: target:
          "L ${cfg.basePath}/${alias} - - - - ${cfg.basePath}/${target}"
        )
        projectAliases) ++

      # 廃止プロジェクトの削除（有効時のみ）
      (optionals cfg.autoCleanup
        (map (name: "r ${cfg.basePath}/${name}") deprecatedProjects)
      );

    # プロジェクト初期化スクリプト
    system.activationScripts.projectStructure = ''
      echo "Setting up project structure..."
      
      # Git設定ファイルの配置
      ${lib.concatMapStrings (name: ''
        if [ ! -f ${cfg.basePath}/${name}/.gitignore ]; then
          cat > ${cfg.basePath}/${name}/.gitignore << 'EOF'
      # Python
      __pycache__/
      *.py[cod]
      venv/
      .env
      
      # Node.js
      node_modules/
      .next/
      dist/
      
      # IDE
      .vscode/
      .idea/
      
      # OS
      .DS_Store
      EOF
          chown noguchilin:users ${cfg.basePath}/${name}/.gitignore
        fi
      '') (attrNames projects)}
    '';

    # プロジェクト情報表示コマンド
    environment.systemPackages = [
      (pkgs.writeScriptBin "projects" ''
        #!${pkgs.bash}/bin/bash
        echo "📁 Project Structure (${cfg.basePath})"
        echo "════════════════════════════════════════"
        ${lib.concatMapStrings (name: ''
          echo "📦 ${name}: ${projects.${name}.description}"
        '') (attrNames projects)}
        echo ""
        echo "🔗 Aliases:"
        ${lib.concatMapStrings (alias: ''
          echo "  ${alias} → ${projectAliases.${alias}}"
        '') (attrNames projectAliases)}
      '')
    ];
  };
}
