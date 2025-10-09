# Nakamura-Misaki Service Setup Guide

## Status
🚧 **Currently Disabled** - Requires sops-nix secrets configuration

## Required Secrets

Nakamura-Misaki service depends on two secrets managed by sops-nix:

1. **`config.sops.secrets.slack_bot_token`** - Slack Bot OAuth Token
2. **`config.sops.secrets.anthropic_api_key`** - Anthropic API Key

## Setup Steps

### 1. Install sops-nix

Add to `flake.nix`:
```nix
inputs.sops-nix.url = "github:Mic92/sops-nix";
```

Import in `configuration.nix`:
```nix
imports = [
  inputs.sops-nix.nixosModules.sops
];
```

### 2. Configure sops-nix

Create `.sops.yaml` in project root:
```yaml
keys:
  - &admin_home_lab_01 YOUR_AGE_PUBLIC_KEY
creation_rules:
  - path_regex: secrets/[^/]+\.yaml$
    key_groups:
      - age:
          - *admin_home_lab_01
```

### 3. Create Secrets File

Create `secrets/nakamura-misaki.yaml`:
```yaml
slack_bot_token: xoxb-YOUR-SLACK-BOT-TOKEN
anthropic_api_key: sk-ant-YOUR-ANTHROPIC-API-KEY
```

Encrypt with sops:
```bash
sops -e -i secrets/nakamura-misaki.yaml
```

### 4. Configure Secrets in NixOS

Add to `configuration.nix`:
```nix
sops = {
  defaultSopsFile = ../secrets/nakamura-misaki.yaml;
  age.keyFile = "/var/lib/sops-nix/key.txt";

  secrets = {
    slack_bot_token = {
      owner = "noguchilin";
      group = "users";
    };
    anthropic_api_key = {
      owner = "noguchilin";
      group = "users";
    };
  };
};
```

### 5. Enable Nakamura-Misaki Service

Uncomment in `configuration.nix`:
```nix
services.nakamura-misaki = {
  enable = true;
  ports = {
    api = 8010;
    adminUI = 3002;
    webhook = 10000;
  };
};
```

Re-add to `modules/services/registry/default.nix`:
```nix
nakamuraMisaki = {
  port = 3002;
  path = "/nakamura";
  name = "Nakamura-Misaki";
  description = "Multi-user Claude Code Agent - Admin UI";
  healthCheck = "/health";
  icon = "🤖";
};
nakamuraMisakiApi = {
  port = 8010;
  path = "/nakamura-api";
  name = "Nakamura-Misaki API";
  description = "Claude Agent API Backend";
  healthCheck = "/health";
  icon = "🔧";
};
```

### 6. Deploy

```bash
nixos-rebuild switch --flake .#home-lab-01
```

## Service Architecture

- **API Backend** (Port 8010): Python FastAPI backend with Slack integration
- **Admin UI** (Port 3002): Next.js frontend for agent management
- **Webhook** (Port 10000): Slack webhook endpoint (via Tailscale Funnel)

## Verification

```bash
# Check service status
systemctl status nakamura-misaki-api.service
systemctl status nakamura-misaki-admin.service

# Check logs
journalctl -u nakamura-misaki-api.service -f
journalctl -u nakamura-misaki-admin.service -f

# Test endpoints
curl http://localhost:8010/health
curl http://localhost:3002
```

## Troubleshooting

### Service Not Starting

1. Check secrets are accessible:
```bash
ls -la /run/secrets/
cat /run/secrets/slack_bot_token
cat /run/secrets/anthropic_api_key
```

2. Check service logs for errors:
```bash
journalctl -u nakamura-misaki-api.service -n 50
```

3. Verify venv exists:
```bash
ls -la /home/noguchilin/projects/nakamura-misaki/.venv
```

### Permission Issues

Ensure secrets have correct ownership:
```nix
sops.secrets.slack_bot_token.owner = "noguchilin";
sops.secrets.anthropic_api_key.owner = "noguchilin";
```

## References

- [sops-nix Documentation](https://github.com/Mic92/sops-nix)
- [Nakamura-Misaki Service Definition](../modules/services/registry/nakamura-misaki.nix)
