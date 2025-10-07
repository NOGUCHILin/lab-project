{ config, lib, pkgs, ... }:

{
  options.services.claude-code = {
    enable = lib.mkEnableOption "Claude Code CLI";
  };

  config = lib.mkIf config.services.claude-code.enable {
    # Node.js環境を提供
    environment.systemPackages = with pkgs; [
      nodejs
      npm
      (writeShellScriptBin "claude" 
        exec ${nodejs}/bin/npx @anthropic-ai/claude-code@1.0.119 "$@"
      )
    ];
  };
}
