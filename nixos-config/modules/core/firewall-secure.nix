# セキュアファイアウォール（最小構成）
{ config, pkgs, ... }:

{
  # 既定でファイアウォールを有効化し、公開は各モジュール側で明示
  networking.firewall.enable = true;
}
