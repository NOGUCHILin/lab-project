{
  description = "Unified Dashboard Development Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
  in {
    # 開発環境のみ - NixOSモジュールは ~/nixos-config/ に分離
    devShells.${system}.default = pkgs.mkShell {
      name = "dashboard-dev";

      buildInputs = with pkgs; [
        nodejs_22
        nodePackages.pnpm
      ];

      shellHook = ''
        echo "🚀 Unified Dashboard 開発環境"
        echo "📦 Node.js: $(node --version)"
        echo "📦 pnpm: $(pnpm --version)"
        echo ""
        echo "💡 開発コマンド:"
        echo "  pnpm dev     - 開発サーバー起動 (port 3005)"
        echo "  pnpm build   - プロダクションビルド"
        echo "  pnpm test    - Playwright テスト"
        echo ""
        echo "🚀 本番環境はNixOSサービスで管理:"
        echo "  sudo systemctl status dashboard.service"
      '';
    };
  };
}
