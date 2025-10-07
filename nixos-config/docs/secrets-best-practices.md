# NixOS シークレット管理のベストプラクティス

## 現在の課題
- シークレットの値がスクリプトに平文で含まれている
- Gitの履歴に機密情報が残る可能性がある

## 推奨される解決策

### 1. 開発環境と本番環境の分離
```nix
# secrets/dev.yaml - 開発用（ダミー値）
# secrets/prod.yaml - 本番用（暗号化済み、.gitignore）
```

### 2. シークレット更新の正しいワークフロー

#### 初期設定（一度だけ）
```bash
# Age鍵の生成
age-keygen -o ~/.config/sops/age/keys.txt

# .sops.yamlにAge公開鍵を追加
```

#### シークレットの更新
```bash
# SOPSエディタで直接編集（値はメモリ内のみ）
cd ~/nixos-config
sops secrets/secrets.yaml

# または、標準入力から読み込み（履歴に残らない）
read -s TOKEN
echo "$TOKEN" | sops --set '["SLACK_USER_TOKEN_MEMENTOMORIS"] /dev/stdin' -i secrets/secrets.yaml
```

### 3. 環境変数を使わない方法
```nix
# modules/services/mementomoris.nix
{
  sops.secrets.mementomoris = {
    format = "yaml";
    sopsFile = ../../secrets/secrets.yaml;
    key = "SLACK_USER_TOKEN_MEMENTOMORIS";
  };

  systemd.services.mementomoris = {
    serviceConfig = {
      LoadCredential = "token:${config.sops.secrets.mementomoris.path}";
      ExecStart = ''
        ${pkgs.bash}/bin/bash -c '
          export SLACK_USER_TOKEN=$(cat $CREDENTIALS_DIRECTORY/token)
          exec ${python}/bin/python ${script}
        '
      '';
    };
  };
}
```

## セキュリティのチェックリスト

- [ ] シークレットの平文がGitに含まれていない
- [ ] .gitignoreで機密ファイルを除外
- [ ] git-secretsやgitleaksでスキャン
- [ ] シークレットのローテーション計画
- [ ] アクセス権限の最小化

## 移行手順

1. **既存のシークレットをGitから削除**
```bash
# 履歴から完全に削除
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch scripts/manage-secrets.sh' \
  --prune-empty --tag-name-filter cat -- --all
```

2. **新しいワークフローに移行**
```bash
# シークレット専用のリポジトリを作成
git submodule add git@private-git:secrets.git secrets-private

# または環境変数で管理
direnv + .envrc (gitignore)
```

## 参考資料
- [NixOS Wiki: Comparison of secret managing schemes](https://nixos.wiki/wiki/Comparison_of_secret_managing_schemes)
- [sops-nix documentation](https://github.com/Mic92/sops-nix)
- [agenix documentation](https://github.com/ryantm/agenix)