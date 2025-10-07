# Secrets management with sops-nix
{ config, pkgs, ... }:

{
  # sops configuration
  sops = {
    # Use user age key for decryption
    age.keyFile = "/home/noguchilin/.config/sops/age/keys.txt";

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
        key = "OPENAI_API_KEY";  # Reference same secret content
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

      # Mementomoris Slack user token (used by reminder service)
      "SLACK_USER_TOKEN_MEMENTOMORIS" = {
        owner = "noguchilin";
        group = "users";
        mode = "0400";
      };

      # Nakamura-Misaki Slack user token (same as mementomoris)
      "SLACK_USER_TOKEN_NAKAMURA" = {
        key = "SLACK_USER_TOKEN_MEMENTOMORIS";  # 同じトークンを参照
        owner = "noguchilin";
        group = "users";
        mode = "0400";
      };

      # Nakamura-Misaki Slack bot token
      "slack_bot_token" = {
        owner = "noguchilin";
        group = "users";
        mode = "0400";
      };

      # Nakamura-Misaki Anthropic API key
      "anthropic_api_key" = {
        owner = "noguchilin";
        group = "users";
        mode = "0400";
      };
    };
  };
}
