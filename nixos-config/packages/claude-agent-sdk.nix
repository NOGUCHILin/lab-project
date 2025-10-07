{ lib, buildPythonPackage, fetchPypi }:

buildPythonPackage rec {
  pname = "claude-agent-sdk";
  version = "0.1.0";  # バージョンを指定

  src = fetchPypi {
    inherit pname version;
    sha256 = ""; # 初回ビルドで取得
  };

  # 依存関係
  propagatedBuildInputs = [
    # 必要な依存パッケージをここに追加
  ];

  meta = with lib; {
    description = "Claude Code Python SDK";
    license = licenses.mit;
  };
}