{ config, lib, pkgs, ... }:

{
  # Soft guard: wrap common imperative commands in interactive shells
  environment.etc."profile.d/10-cli-guards.sh".text = ''
    #!/usr/bin/env bash
    # Guard imperative commands to prevent drift. Sourced for interactive shells.

    export PIP_REQUIRE_VIRTUALENV=true

    nix-env() {
      echo "Blocked: nix-env is disabled. Use flakes (nixos-rebuild, nix build/develop)." >&2
      return 1
    }

    nix-channel() {
      echo "Blocked: nix-channel is disabled. Use flake inputs instead." >&2
      return 1
    }

    nix() {
      if [ "$1" = profile ]; then
        echo "Blocked: 'nix profile' is disabled (install/remove/upgrade). Use flake-managed packages." >&2
        return 1
      fi
      command nix "$@"
    }

    npm() {
      case " $* " in
        *" -g "*|*" --global "*|"i -g "|"install -g "*)
          echo "Blocked: global npm install is disabled. Add deps to project or flake." >&2
          return 1;;
      esac
      command npm "$@"
    }

    pip() {
      if [ -z "$VIRTUAL_ENV" ]; then
        echo "Blocked: pip outside virtualenv. Activate venv or use 'uv venv' first." >&2
        return 1
      fi
      command pip "$@"
    }

    pip3() { pip "$@"; }

    pipx() {
      echo "Blocked: pipx is disabled. Use project venv or flake." >&2
      return 1
    }

    cargo() {
      if [ "$1" = install ]; then
        echo "Blocked: 'cargo install' is disabled. Vendor in project or build via flake." >&2
        return 1
      fi
      command cargo "$@"
    }

    go() {
      if [ "$1" = install ]; then
        echo "Blocked: 'go install' is disabled. Vendor in project or build via flake." >&2
        return 1
      fi
      command go "$@"
    }

    gem() {
      if [ "$1" = install ]; then
        echo "Blocked: 'gem install' is disabled. Use bundler or flake." >&2
        return 1
      fi
      command gem "$@"
    }

    systemctl() {
      # Block imperative control of dashboard units
      local sub="$1" unit="$2"
      case "$sub:$unit" in
        start:dashboard*|stop:dashboard*|restart:dashboard*|enable:dashboard*|disable:dashboard*|edit:dashboard*)
          echo "Blocked: manual systemctl $sub $unit is disabled. Change Nix config and rebuild." >&2
          return 1;;
      esac
      command systemctl "$@"
    }

    tailscale() {
      if [ "$1" = serve ] && [ "$2" != status ]; then
        echo "Blocked: 'tailscale serve' changes are managed by Nix. Edit config and rebuild." >&2
        return 1
      fi
      command tailscale "$@"
    }
  '';
}
