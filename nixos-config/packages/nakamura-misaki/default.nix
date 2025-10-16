{ lib
, python3
, src
}:

let
  # Python環境（すべての依存関係を含む）
  pythonEnv = python3.withPackages (ps: with ps; [
    fastapi
    uvicorn
    # slack-boltのテスト失敗を回避するため、doCheck=falseでオーバーライド
    (slack-bolt.overridePythonAttrs (old: { doCheck = false; }))
    slack-sdk
    anthropic
    aiohttp
    asyncpg  # required for postgresql+asyncpg:// connection
    psycopg  # psycopg[binary,pool]
    sqlalchemy
    alembic  # database migrations
    pgvector
    pydantic
    pydantic-settings
    python-dateutil
  ]);

  app = python3.pkgs.buildPythonApplication rec {
    pname = "nakamura-misaki";
    version = "4.0.0";
    format = "pyproject";

    # Flake inputから渡されたソースを使用
    inherit src;

    # ビルド時の依存関係
    nativeBuildInputs = with python3.pkgs; [
      hatchling
    ];

    # 実行時の依存関係
    propagatedBuildInputs = with python3.pkgs; [
      fastapi
      uvicorn
      (slack-bolt.overridePythonAttrs (old: { doCheck = false; }))
      slack-sdk
      anthropic
      aiohttp
      asyncpg
      psycopg
      sqlalchemy
      alembic
      pgvector
      pydantic
      pydantic-settings
      python-dateutil
    ];

    # テスト時の依存関係
    nativeCheckInputs = with python3.pkgs; [
      pytest
      pytest-asyncio
      pytest-cov
      httpx
    ];

    doCheck = false;
    pythonImportsCheck = [];

    # Python環境をpassthru経由で公開
    passthru = {
      python = pythonEnv;
    };

    meta = with lib; {
      description = "Task management AI assistant with Kusanagi Motoko personality";
      homepage = "https://github.com/NOGUCHILin/lab-project";
      license = licenses.mit;
      maintainers = [ "noguchilin" ];
      mainProgram = "uvicorn";
    };
  };
in
app
