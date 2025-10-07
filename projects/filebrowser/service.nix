# FileBrowser - Web-based file manager
{ config, pkgs, lib, ... }:

{
  systemd.services.filebrowser = {
    description = "FileBrowser - Web File Management";
    wantedBy = [ "multi-user.target" ];
    after = [ "network.target" ];

    serviceConfig = {
      Type = "simple";
      User = "noguchilin";
      Group = "users";
      WorkingDirectory = "/home/noguchilin";

      # データベースファイルをホームディレクトリに保存
      ExecStart = "${pkgs.filebrowser}/bin/filebrowser -a 127.0.0.1 -p 9000 -r /home/noguchilin -d /home/noguchilin/.filebrowser.db --noauth";

      Restart = "always";
      RestartSec = 10;

      # セキュリティ設定
      PrivateTmp = true;
      NoNewPrivileges = true;
    };
  };
}
