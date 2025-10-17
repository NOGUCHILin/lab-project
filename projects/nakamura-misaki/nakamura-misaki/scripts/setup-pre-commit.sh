#!/bin/bash
# Pre-commit hook setup script for nakamura-misaki v6.0.0

set -e

echo "🔧 Setting up pre-commit hooks for TDD + UDD workflow..."

# 1. Install pre-commit dependencies
echo "📦 Installing pre-commit..."
uv sync --extra dev

# 2. Install pre-commit hooks
echo "🪝 Installing git hooks..."
uv run pre-commit install
uv run pre-commit install --hook-type pre-push

# 3. Test pre-commit setup
echo "✅ Testing pre-commit configuration..."
uv run pre-commit run --all-files || true

echo ""
echo "✅ Pre-commit hooks setup complete!"
echo ""
echo "📝 Hooks installed:"
echo "  - pre-commit: Runs ruff, mypy, unit tests"
echo "  - pre-push: Runs all tests (including integration & E2E)"
echo ""
echo "💡 Usage:"
echo "  - Normal commit: git commit (auto-runs unit tests)"
echo "  - Skip hooks: git commit --no-verify (use sparingly!)"
echo "  - Manual run: uv run pre-commit run --all-files"
echo ""
