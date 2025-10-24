#!/usr/bin/env bash
# Auto-update npmDepsHash in Nix flake when package-lock.json changes
# Usage: ./scripts/update-npm-hash.sh <project-path>

set -euo pipefail

PROJECT_DIR="${1:-projects/nakamura-misaki/web-ui}"
PACKAGE_LOCK="$PROJECT_DIR/package-lock.json"
FLAKE_NIX="$PROJECT_DIR/flake.nix"

# Check if files exist
if [ ! -f "$PACKAGE_LOCK" ]; then
    echo "❌ package-lock.json not found at $PACKAGE_LOCK"
    exit 1
fi

if [ ! -f "$FLAKE_NIX" ]; then
    echo "❌ flake.nix not found at $FLAKE_NIX"
    exit 1
fi

# Calculate correct hash using prefetch-npm-deps
echo "🔄 Calculating npmDepsHash for $PROJECT_DIR..."
NEW_HASH=$(nix run nixpkgs#prefetch-npm-deps "$PACKAGE_LOCK" 2>/dev/null)

if [ -z "$NEW_HASH" ]; then
    echo "❌ Failed to calculate hash"
    exit 1
fi

# Get current hash from flake.nix
CURRENT_HASH=$(grep -oP 'npmDepsHash\s*=\s*"\K[^"]+' "$FLAKE_NIX" || echo "")

# Check if hash needs updating
if [ "$CURRENT_HASH" = "$NEW_HASH" ]; then
    echo "✅ npmDepsHash is already up to date: $NEW_HASH"
    exit 0
fi

# Update hash in flake.nix
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|npmDepsHash = \".*\"|npmDepsHash = \"$NEW_HASH\"|" "$FLAKE_NIX"
else
    # Linux
    sed -i "s|npmDepsHash = \".*\"|npmDepsHash = \"$NEW_HASH\"|" "$FLAKE_NIX"
fi

# Also update if using pkgs.lib.fakeHash
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s|npmDepsHash = pkgs.lib.fakeHash|npmDepsHash = \"$NEW_HASH\"|" "$FLAKE_NIX"
else
    sed -i "s|npmDepsHash = pkgs.lib.fakeHash|npmDepsHash = \"$NEW_HASH\"|" "$FLAKE_NIX"
fi

echo "✅ Updated npmDepsHash in $FLAKE_NIX"
echo "   Old: $CURRENT_HASH"
echo "   New: $NEW_HASH"
