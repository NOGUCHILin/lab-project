# デプロイ時データベース初期化エラー - 調査レポート

**作成日**: 2025-10-24
**ステータス**: 調査完了
**優先度**: High（本番デプロイがブロックされている）

---

## 📊 問題の概要

GitHub Actionsによる本番デプロイ時、nakamura-misaki-init-db.serviceが以下のエラーで失敗：

```
CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'completed', 'cancelled')
(psycopg.errors.DuplicateObject) type "task_status" already exists
```

### 影響範囲
- すべての本番デプロイが失敗（自動ロールバックされる）
- 新しいコード変更が本番環境に適用できない
- 現在、nakamura-misakiの担当者割り当て機能修正がデプロイ待ち

---

## 🔍 根本原因分析

### 1. Alembicマイグレーション001に冪等性がない

**ファイル**: [alembic/versions/001_initial_schema.py:27](../alembic/versions/001_initial_schema.py#L27)

```python
# 問題のあるコード
op.execute("CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'completed', 'cancelled')")
```

**問題点**:
- `IF NOT EXISTS`チェックがない
- 既にENUMが存在する場合、即座にエラーになる
- PostgreSQLはENUMの重複作成を許可しない

### 2. systemdサービスが毎デプロイ時に実行される

**ファイル**: [nixos-config/modules/services/registry/nakamura-misaki-db.nix:57-85](../../nixos-config/modules/services/registry/nakamura-misaki-db.nix#L57-L85)

```nix
systemd.services.nakamura-misaki-init-db = {
  description = "Initialize nakamura-misaki v6.0.0 database";
  wantedBy = [ "multi-user.target" ];

  serviceConfig = {
    Type = "oneshot";
    # 69行目のコメント: 「冪等性があるため毎回実行可能」
    # → 実際には冪等性がない
    ExecStart = pkgs.writeShellScript "init-nakamura-db" ''
      ${nakamura-misaki-venv}/bin/nakamura-init-db
    '';
  };
};
```

**問題点**:
- コメントには「冪等性がある」と記載されているが、実際にはない
- `Type = "oneshot"` + `wantedBy = [ "multi-user.target" ]` で毎回実行
- デプロイごとにサービスが再起動→Alembicマイグレーション再実行→エラー

### 3. Alembicバージョン管理が機能していない可能性

**期待される動作**:
- Alembicは`alembic_version`テーブルで適用済みマイグレーションを追跡
- 既に適用済みのマイグレーションはスキップされる

**実際の動作**:
- エラーログから、001マイグレーションが再実行されている
- 原因: 不明（要追加調査）
  - alembic_versionテーブルが存在しない？
  - マイグレーションチェーンの破損？
  - Nix store内のAlembicディレクトリパス問題？

---

## 📋 マイグレーションチェーン分析

### 現在のマイグレーション順序

```
001 (initial_schema - tasks, handoffs, conversations, notes, sessions + task_status ENUM)
  ↓
b0bbf866ebc2 (drop unused tables: handoffs, notes, sessions)
  ↓
002_add_tasks_table (tasksテーブル再作成 - statusはString型)
  ↓
79bb97c4352b (workforce management tables)
  ↓
ca1f08e0bc8a (fix task_status enum to lowercase)
  ↓
003_add_slack_users_table
  ↓
004_add_unique_constraint_to_conversations
```

### 問題点

1. **001でtasksテーブル作成 → b0bbf866ebc2で削除せず → 002で再作成**
   - データ損失のリスクあり
   - 001と002の間で整合性が取れていない

2. **task_status ENUMの管理が不明瞭**
   - 001でCREATE TYPE
   - ca1f08e0bc8aで修正（lowercase化）
   - 002_add_tasks_tableではString型を使用（ENUMを使わない）

3. **マイグレーションファイル命名規則が混在**
   - 番号付き: 001, 002, 003, 004
   - ハッシュ付き: b0bbf866ebc2, 79bb97c4352b, ca1f08e0bc8a

---

## 🛠️ 長期的な修正方針（3つの選択肢）

### 方針1: Alembicマイグレーションを冪等にする ✅ **推奨**

#### メリット
- ✅ ベストプラクティスに準拠
- ✅ デプロイパイプラインのロバストネス向上
- ✅ データベース状態に関わらず安全に実行可能
- ✅ 将来的なマイグレーション追加も安全

#### デメリット
- ⚠️ 既存マイグレーションファイルの修正が必要（001, ca1f08e0bc8a等）
- ⚠️ 複雑なマイグレーションの冪等化が困難な場合がある

#### 実装詳細

**Step 1**: 001マイグレーションを冪等化

```python
# Before (alembic/versions/001_initial_schema.py:27)
op.execute("CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'completed', 'cancelled')")

# After
op.execute("""
    DO $$ BEGIN
        CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'completed', 'cancelled');
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
""")
```

**Step 2**: その他のマイグレーションも冪等化（必要に応じて）

**Step 3**: ドキュメントに冪等性ガイドライン追加

---

### 方針2: systemdサービスを一度だけ実行

#### メリット
- ✅ マイグレーションファイルの修正不要
- ✅ シンプルな実装

#### デメリット
- ❌ 新しいマイグレーション追加時、手動実行が必要
- ❌ デプロイパイプラインとして脆弱
- ❌ CI/CDの自動化の恩恵を受けられない

#### 実装詳細

```nix
# nixos-config/modules/services/registry/nakamura-misaki-db.nix

systemd.services.nakamura-misaki-init-db = {
  # ... existing config ...

  unitConfig = {
    # 一度だけ実行（フラグファイルが存在する場合スキップ）
    ConditionPathExists = "!/var/lib/nakamura-misaki/.db-initialized";
  };

  serviceConfig = {
    # ... existing config ...

    # 成功時にフラグファイルを作成
    ExecStartPost = "${pkgs.coreutils}/bin/touch /var/lib/nakamura-misaki/.db-initialized";
  };
};
```

**Note**: pgvector拡張有効化サービス（nakamura-misaki-enable-vector）は既にこのパターンを使用しています。

---

### 方針3: Alembic実行前にバージョンチェック

#### メリット
- ✅ 不要なマイグレーション実行を防ぐ
- ✅ Alembicの正常な動作を確保

#### デメリット
- ❌ 実装が複雑
- ❌ `init_db.py`スクリプトの大幅な変更が必要
- ❌ Alembicの内部実装に依存

#### 実装詳細（スケッチ）

```python
# scripts/init_db.py

def get_current_db_version():
    """Get current database schema version from alembic_version table"""
    # SQLAlchemy connection -> SELECT version_num FROM alembic_version
    pass

def get_latest_migration_version():
    """Get latest migration version from alembic/versions/"""
    # Parse migration files -> return latest revision
    pass

def run_alembic_upgrade():
    current = get_current_db_version()
    latest = get_latest_migration_version()

    if current == latest:
        print("Database is up to date, skipping migrations")
        return

    # Run alembic upgrade head
    # ...
```

---

## 💡 推奨アプローチ

### **方針1（Alembicマイグレーションを冪等にする）を強く推奨**

#### 理由

1. **長期的な安定性**
   - 一度冪等化すれば、将来的なマイグレーションも同じパターンで作成可能
   - データベース状態に関わらず安全にデプロイできる

2. **業界標準のベストプラクティス**
   - RailsのActive Record、Django、Laravelなど主要フレームワークが推奨
   - 「マイグレーションは何度実行しても安全」が原則

3. **デプロイパイプラインの簡素化**
   - 条件分岐不要
   - 手動介入不要
   - ロールバック/再デプロイが安全

4. **トラブルシューティングの容易さ**
   - 本番環境でマイグレーションを手動で再実行しても安全
   - データベース復旧時も同じスクリプトが使える

---

## 🚀 実装ステップ（方針1）

### Phase 1: 001マイグレーションの冪等化（最優先）

1. ✅ `alembic/versions/001_initial_schema.py` を修正
2. ✅ ローカル環境でテスト（clean DB + 既存DB両方）
3. ✅ コミット・プッシュ
4. ✅ 本番デプロイ検証

### Phase 2: マイグレーションチェーンの整理（推奨）

1. 📋 全マイグレーションファイルのdown_revisionを確認
2. 📋 不要なマイグレーション（002でtasksテーブル再作成等）を整理
3. 📋 マイグレーション命名規則を統一（番号 vs ハッシュ）
4. 📋 マイグレーションチェーン図を作成（mermaid）

### Phase 3: その他のマイグレーション冪等化（必要に応じて）

1. ca1f08e0bc8a (fix task_status enum)
2. 79bb97c4352b (workforce management tables)
3. その他

### Phase 4: ドキュメント整備

1. マイグレーション作成ガイドライン
2. 冪等性チェックリスト
3. トラブルシューティングガイド

---

## 📝 緊急対応（短期）

**今回のデプロイをブロック解除するための最小限の修正**:

### オプションA: 001マイグレーションのみ冪等化

```python
# alembic/versions/001_initial_schema.py:27

# Before
op.execute("CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'completed', 'cancelled')")

# After
op.execute("""
    DO $$ BEGIN
        CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'completed', 'cancelled');
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
""")
```

**所要時間**: 5分
**リスク**: 低

### オプションB: nakamura-misaki-init-db.serviceを一度だけ実行

```nix
# nixos-config/modules/services/registry/nakamura-misaki-db.nix

unitConfig = {
  ConditionPathExists = "!/var/lib/nakamura-misaki/.db-initialized";
};

serviceConfig = {
  ExecStartPost = "${pkgs.coreutils}/bin/touch /var/lib/nakamura-misaki/.db-initialized";
};
```

**所要時間**: 3分
**リスク**: 中（将来的なマイグレーション実行が手動になる）

---

## ⚠️ 追加調査が必要な項目

1. **Alembicバージョン管理テーブルの状態確認**
   ```bash
   ssh home-lab-01
   psql -U nakamura_misaki -d nakamura_misaki \
     -c "SELECT * FROM alembic_version;"
   ```

2. **マイグレーション002でのtasksテーブル再作成の意図**
   - 001で作成 → b0bbf866ebc2で削除せず → 002で再作成は意図的？

3. **本番データベースの現在のスキーマ状態**
   - どのマイグレーションまで適用済みか？
   - task_status ENUMの現在の値は？

---

## 📚 参考資料

- [Alembic公式ドキュメント - Best Practices](https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script)
- [PostgreSQL CREATE TYPE IF NOT EXISTS](https://www.postgresql.org/docs/current/sql-createtype.html)
- [systemd oneshot services](https://www.freedesktop.org/software/systemd/man/systemd.service.html#Type=)

---

**Generated with [Claude Code](https://claude.com/claude-code)**
