# Secrets management with sops-nix
{ config, pkgs, ... }:

{
  # sops configuration
  sops = {
    # Use SSH host key for age decryption (most reliable)
    age.sshKeyPaths = [ "/etc/ssh/ssh_host_ed25519_key" ];

    # Default sops file
    defaultSopsFile = ../../secrets/secrets.yaml;

    # Secrets definitions
    secrets = {
      # OpenAI API key for realtime voice service
      "OPENAI_API_KEY" = {
        owner = "noguchilin";
        group = "users";
        mode = "0400";
      };

      # OpenAI API key for dashboard service (same content, different permissions)
      "OPENAI_API_KEY_DASHBOARD" = {
        key = "OPENAI_API_KEY"; # Reference same secret content
        owner = "noguchilin";
        group = "users";
        mode = "0400";
      };

      # GitHub CLI authentication token
      "github-token" = {
        owner = "noguchilin";
        group = "users";
        mode = "0400";
      };

      # GitHub username
      "github-user" = {
        owner = "noguchilin";
        group = "users";
        mode = "0400";
      };

      # SSH private key for user
      "ssh-private-key" = {
        owner = "noguchilin";
        group = "users";
        mode = "0400";
      };

      # Nakamura-Misaki secrets (from separate file)
      "slack_bot_token" = {
        sopsFile = ../../secrets/nakamura-misaki.yaml;
        owner = "noguchilin";
        group = "users";
        mode = "0400";
      };

      "slack_signing_secret" = {
        sopsFile = ../../secrets/nakamura-misaki.yaml;
        owner = "noguchilin";
        group = "users";
        mode = "0400";
      };

      "anthropic_api_key" = {
        sopsFile = ../../secrets/nakamura-misaki.yaml;
        owner = "noguchilin";
        group = "users";
        mode = "0400";
      };
    };
  };
}
