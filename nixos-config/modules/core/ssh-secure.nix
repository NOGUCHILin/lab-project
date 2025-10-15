# SSH セキュア設定（認証・アクセス制御）
{ config, pkgs, ... }:

{
  # SSH強化設定
  services.openssh = {
    enable = true;
    settings = {
      PasswordAuthentication = false;  # 公開鍵認証のみ
      PermitRootLogin = "prohibit-password";  # Root login via SSH key only (for deploy-rs)
      PubkeyAuthentication = true;
      AuthorizedKeysFile = "/etc/ssh/authorized_keys.d/%u %h/.ssh/authorized_keys";
    };
  };
}