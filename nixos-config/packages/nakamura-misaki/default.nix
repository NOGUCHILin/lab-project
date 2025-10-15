{ lib
, python3
, src
}:

python3.pkgs.buildPythonApplication rec {
  pname = "nakamura-misaki";
  version = "4.0.0";
  format = "pyproject";

  # Flake inputから渡されたソースを使用
  # デプロイ時に path:../nakamura-misaki が参照される
  inherit src;

  # ビルド時の依存関係
  nativeBuildInputs = with python3.pkgs; [
    hatchling  # pyproject.tomlのbuild-backend
  ];

  # 実行時の依存関係（propagatedBuildInputsに明示的に記載）
  propagatedBuildInputs = with python3.pkgs; [
    fastapi
    uvicorn
    # slack-boltのテスト失敗を回避するため、doCheck=falseでオーバーライド
    (slack-bolt.overridePythonAttrs (old: { doCheck = false; }))
    slack-sdk
    anthropic
    aiohttp
    psycopg  # psycopg[binary,pool]
    sqlalchemy
    pgvector
    pydantic
    pydantic-settings
    python-dateutil
    # claude-agent-sdkはnixpkgsにないため、追加インストールが必要な場合は別途対応
  ];

  # テスト時の依存関係（本番環境では不要）
  nativeCheckInputs = with python3.pkgs; [
    pytest
    pytest-asyncio
    pytest-cov
    httpx
  ];

  # テストをスキップ（slack-boltのテスト失敗を回避）
  doCheck = false;

  # 最低限のimportチェック（実行可能性を保証）
  pythonImportsCheck = [
    "src.adapters.primary.api"
    "src.adapters.secondary.slack"
    "src.application.use_cases"
    "src.domain.models"
  ];

  meta = with lib; {
    description = "Task management AI assistant with Kusanagi Motoko personality";
    homepage = "https://github.com/NOGUCHILin/lab-project";
    license = licenses.mit;
    maintainers = [ "noguchilin" ];
    mainProgram = "uvicorn";
  };
}
