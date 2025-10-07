# セキュアなシークレット管理ガイド

## 概要
NixOSでSOPS（Secrets OPerationS）を使用したベストプラクティスに基づくシークレット管理。

## セキュリティ原則
- **絶対にシークレットを平文でコミットしない**
- **環境変数やスクリプトに値を直接書かない**
- **最小権限の原則を適用**
- **監査可能な変更履歴を維持**

## シークレットの更新方法

### 方法1: SOPSエディタで直接編集（推奨）
```bash
cd ~/nixos-config
sops secrets/secrets.yaml
# エディタが開くので、値を編集して保存
```

### 方法2: 標準入力から安全に読み込み
```bash
cd ~/nixos-config
# パスワードマネージャーからコピー、または安全に入力
read -s TOKEN
echo "$TOKEN" | sops --set '["SLACK_USER_TOKEN_MEMENTOMORIS"] /dev/stdin' -i secrets/secrets.yaml
unset TOKEN  # メモリからクリア
```

### 方法3: 一時ファイル経由（複数シークレット）
```bash
cd ~/nixos-config
# 一時ファイルを作成（メモリ上のtmpfs推奨）
cat > /dev/shm/temp_secret.json <<'EOF'
{
  "SLACK_USER_TOKEN_MEMENTOMORIS": "xoxp-...",
  "ANOTHER_SECRET": "value"
}
EOF
# SOPSで暗号化して保存
sops --input-type json --output-type yaml -e /dev/shm/temp_secret.json > temp.yaml
# 既存のsecrets.yamlとマージ（手動で編集）
sops secrets/secrets.yaml
# 一時ファイルを安全に削除
shred -vfz /dev/shm/temp_secret.json
```

## システムへの適用
```bash
# 設定を適用
sudo nixos-rebuild switch --flake ~/nixos-config#home-lab-01

# サービスの状態確認
journalctl -u mementomoris -f
```

## セキュリティチェックリスト

### ✅ やるべきこと
- [ ] `.gitignore`に機密ファイルパターンを追加
- [ ] SOPSの暗号化キーを安全に管理
- [ ] シークレットへのアクセスを最小限に制限
- [ ] 定期的にシークレットをローテーション
- [ ] 変更履歴を監査

### ❌ やってはいけないこと
- [ ] シークレットを環境変数にエクスポートしたままにする
- [ ] スクリプトやコードに値をハードコード
- [ ] 暗号化されていないファイルをコミット
- [ ] ターミナル履歴にシークレットを残す
- [ ] クリップボードにシークレットを長時間保持

## トラブルシューティング

### シークレットが読み込めない場合
```bash
# SOPS設定の確認
cat secrets/.sops.yaml

# 暗号化キーの確認
age -d secrets/secrets.yaml  # エラーメッセージで問題を特定

# 権限の確認
ls -la /run/secrets.d/
```

### サービスがシークレットを取得できない場合
```bash
# systemdのCredentialsDirectoryを確認
sudo systemctl show mementomoris | grep Credential

# SOPSサービスの状態
sudo systemctl status sops-nix
```

## 緊急時の対応

### シークレットが漏洩した場合
1. **即座に無効化**: 漏洩したトークン/キーを無効化
2. **新しいシークレット生成**: 新しい値を生成
3. **SOPS更新**: `sops secrets/secrets.yaml`で更新
4. **システム適用**: `sudo nixos-rebuild switch`
5. **監査**: アクセスログを確認

## 参考資料
- [SOPS公式ドキュメント](https://github.com/mozilla/sops)
- [sops-nix](https://github.com/Mic92/sops-nix)
- [NixOS Wiki: Secrets](https://nixos.wiki/wiki/Comparison_of_secret_managing_schemes)