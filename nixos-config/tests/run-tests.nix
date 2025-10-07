# Test Runner for Service Registry
# TDD: テストを実行して結果を確認する

{ pkgs ? import <nixpkgs> {}, lib ? pkgs.lib }:

let
  # Import test file
  tests = import ./service-registry.test.nix { inherit pkgs lib; };
  
  # Color codes for output
  green = "\\033[0;32m";
  red = "\\033[0;31m";
  reset = "\\033[0m";
  
  # Run a single test
  runTest = name: test:
    let
      result = 
        if test ? assertion then
          test.assertion
        else if test ? assertions then
          builtins.all (x: x) test.assertions
        else
          false;
          
      status = if result then "${green}✓${reset}" else "${red}✗${reset}";
      message = "${status} ${test.description or name}";
    in {
      inherit name result message;
      passed = result;
    };
  
  # Get all test names
  testNames = builtins.filter 
    (name: lib.hasPrefix "test_" name) 
    (builtins.attrNames tests);
  
  # Run all tests
  testResults = map (name: runTest name tests.${name}) testNames;
  
  # Summary
  totalTests = builtins.length testResults;
  passedTests = builtins.length (builtins.filter (t: t.passed) testResults);
  failedTests = totalTests - passedTests;
  
  # Format output
  output = ''
    ╔════════════════════════════════════════════════════════════╗
    ║                    Service Registry Tests                  ║
    ╚════════════════════════════════════════════════════════════╝
    
    ${lib.concatMapStringsSep "\n" (t: t.message) testResults}
    
    ═══════════════════════════════════════════════════════════════
    Total: ${toString totalTests} | Passed: ${toString passedTests} | Failed: ${toString failedTests}
    ${if failedTests == 0 then "${green}All tests passed!${reset}" else "${red}Some tests failed!${reset}"}
  '';
in
  pkgs.writeScriptBin "test-service-registry" ''
    #!${pkgs.bash}/bin/bash
    echo -e "${output}"
    exit ${if failedTests == 0 then "0" else "1"}
  ''