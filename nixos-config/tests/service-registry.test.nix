# Service Registry Tests - TDD approach
# テスト駆動開発: まずテストを書いてから実装する

{ pkgs, lib, ... }:

let
  # Import the service registry (test helper)
  registry = import ./lib/service-registry.nix { inherit pkgs lib; };

  # Test data
  testService = {
    name = "test-service";
    port = 9999;
    type = "python";
    workDir = "/home/test/service";
  };
in
rec {
  # Test 1: サービス登録が正しく動作すること
  test_registerService = {
    description = "Service should be registered with minimal config";

    expected = {
      name = "test-service";
      port = 9999;
      type = "python";
      workDir = "/home/test/service";
      # Defaults that should be added
      user = "test-service";
      group = "test-service";
      serviceHome = "/var/lib/test-service";
    };

    actual = registry.registerService testService;

    assertion = actual == expected;
  };

  # Test 2: Pythonサービスが正しくsystemdサービスを生成すること
  test_pythonServiceGeneration = {
    description = "Python service should generate correct systemd config";

    input = {
      name = "ai-gateway";
      port = 8892;
      type = "python";
      workDir = "/home/noguchilin/projects/ai-gateway";
      useVenv = true;
    };

    result = registry.generateSystemdService input;

    assertions = [
      # サービスが有効化されていること
      (result.systemd.services."ai-gateway".wantedBy == [ "multi-user.target" ])
      # ポートが設定されていること
      (result.systemd.services."ai-gateway".environment.PORT == "8892")
      # Pythonが使用されること
      (lib.hasInfix "python" result.systemd.services."ai-gateway".script)
      # venvが使用されること
      (lib.hasInfix "venv" result.systemd.services."ai-gateway".script)
    ];
  };

  # Test 3: セキュリティプロファイルが適用されること
  test_securityProfile = {
    description = "Security profile should be applied correctly";

    input = {
      name = "secure-service";
      port = 8000;
      type = "python";
      securityProfile = "strict";
    };

    result = registry.applySecurityProfile input;

    assertions = [
      # Strict security settings
      (result.serviceConfig.NoNewPrivileges == true)
      (result.serviceConfig.PrivateTmp == true)
      (result.serviceConfig.ProtectSystem == "strict")
      (result.serviceConfig.ProtectHome == true)
    ];
  };

  # Test 4: ポート管理が正しく動作すること
  test_portManagement = {
    description = "Port should be managed centrally";

    services = {
      service1 = { name = "service1"; port = 8000; };
      service2 = { name = "service2"; port = 8001; };
    };

    result = registry.managePorts services;

    assertions = [
      # All ports are registered
      (builtins.length result.ports == 2)
      # Firewall rules are created
      (result.networking.firewall.allowedTCPPorts == [ 8000 8001 ])
      # No port conflicts
      (result.conflicts == [ ])
    ];
  };

  # Test 5: 依存関係が正しく解決されること
  test_dependencies = {
    description = "Service dependencies should be resolved";

    input = {
      name = "dependent-service";
      port = 8000;
      dependencies = [ "database" "cache" ];
    };

    result = registry.resolveDependencies input;

    assertions = [
      # After includes dependencies
      (builtins.elem "database.service" result.after)
      (builtins.elem "cache.service" result.after)
      # Wants includes dependencies
      (builtins.elem "database.service" result.wants)
    ];
  };

  # Test 6: 環境変数とシークレット管理
  test_environmentAndSecrets = {
    description = "Environment variables and secrets should be handled";

    input = {
      name = "secret-service";
      port = 8000;
      useSops = true;
      environment = {
        NODE_ENV = "production";
        LOG_LEVEL = "info";
      };
    };

    result = registry.handleEnvironment input;

    assertions = [
      # Environment variables are set
      (result.environment.NODE_ENV == "production")
      (result.environment.LOG_LEVEL == "info")
      # SOPS integration
      (result.environment ? OPENAI_API_KEY_FILE)
    ];
  };

  # Export tests for runner
  inherit
    test_registerService
    test_pythonServiceGeneration
    test_securityProfile
    test_portManagement
    test_dependencies
    test_environmentAndSecrets;
}
