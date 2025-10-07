# NixOS Declarative Service Setup

## Services Created
1. **unified-dashboard**: Next.js dashboard on port 3000
2. **tailscale-serve-dashboard**: HTTPS proxy via Tailscale

## Configuration Files
- `/tmp/unified-dashboard.nix`: Ready to copy to /etc/nixos/
- Services run as user `noguchilin`
- Auto-restart on failure
- Logs to systemd journal

## Key Features
- Declarative configuration (no manual startup needed)
- Automatic startup on boot
- Crash recovery with 10s restart delay
- HTTPS access via Tailscale Serve