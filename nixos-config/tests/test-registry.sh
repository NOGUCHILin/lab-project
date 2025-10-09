#!/usr/bin/env bash

# Service Registry Test Runner - TDD Approach
# テスト駆動開発: テストが先、実装が後

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║             Service Registry Tests - TDD                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -n "Testing: $test_name ... "
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Passed${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ Failed${NC}"
        ((FAILED++))
    fi
}

# Test 1: Check if service registry file exists
run_test "Service registry module exists" \
    "test -f ../modules/core/service-registry.nix"

# Test 2: Check if registry can be evaluated
run_test "Service registry can be evaluated" \
    "nix-instantiate --eval --expr 'import ../modules/core/service-registry.nix { pkgs = import <nixpkgs> {}; lib = (import <nixpkgs> {}).lib; }' > /dev/null"

# Test 3: Test registerService function
run_test "registerService adds defaults" \
    "nix-instantiate --eval --expr '
        let 
          registry = import ../modules/core/service-registry.nix { 
            pkgs = import <nixpkgs> {}; 
            lib = (import <nixpkgs> {}).lib; 
          };
          result = registry.registerService { name = \"test\"; port = 8000; type = \"python\"; };
        in result.user == \"test\"
    ' | grep true"

# Test 4: Test Python service generation
run_test "Python service generation" \
    "nix-instantiate --eval --expr '
        let 
          registry = import ../modules/core/service-registry.nix { 
            pkgs = import <nixpkgs> {}; 
            lib = (import <nixpkgs> {}).lib; 
          };
          svc = { name = \"test-python\"; port = 8000; type = \"python\"; workDir = \"/tmp\"; };
          result = registry.generateSystemdService svc;
        in result ? systemd
    ' | grep true"

# Test 5: Test security profile
run_test "Security profile application" \
    "nix-instantiate --eval --expr '
        let 
          registry = import ../modules/core/service-registry.nix { 
            pkgs = import <nixpkgs> {}; 
            lib = (import <nixpkgs> {}).lib; 
          };
          svc = { name = \"test\"; port = 8000; securityProfile = \"strict\"; };
          result = registry.applySecurityProfile svc;
        in result.ProtectSystem == \"strict\"
    ' | grep true"

# Test 6: Test port management
run_test "Port management - no conflicts" \
    "nix-instantiate --eval --expr '
        let 
          registry = import ../modules/core/service-registry.nix { 
            pkgs = import <nixpkgs> {}; 
            lib = (import <nixpkgs> {}).lib; 
          };
          services = {
            svc1 = { port = 8000; };
            svc2 = { port = 8001; };
          };
          result = registry.managePorts services;
        in builtins.length result.conflicts == 0
    ' | grep true"

# Test 7: Test dependency resolution
run_test "Dependency resolution" \
    "nix-instantiate --eval --expr '
        let 
          registry = import ../modules/core/service-registry.nix { 
            pkgs = import <nixpkgs> {}; 
            lib = (import <nixpkgs> {}).lib; 
          };
          svc = { dependencies = [ \"database\" \"cache\" ]; };
          result = registry.resolveDependencies svc;
        in builtins.elem \"database.service\" result.after
    ' | grep true"

# Test 8: Test environment handling
run_test "Environment and secrets handling" \
    "nix-instantiate --eval --expr '
        let 
          registry = import ../modules/core/service-registry.nix { 
            pkgs = import <nixpkgs> {}; 
            lib = (import <nixpkgs> {}).lib; 
          };
          svc = { port = 8000; environment = { NODE_ENV = \"production\"; }; useSops = true; };
          result = registry.handleEnvironment svc;
        in result.environment.NODE_ENV == \"production\"
    ' | grep true"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo -e "Total: $((PASSED + FAILED)) | ${GREEN}Passed: $PASSED${NC} | ${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✅${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed! ❌${NC}"
    exit 1
fi