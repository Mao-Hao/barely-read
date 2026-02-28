#!/usr/bin/env bash
# BR Setup Script (Product)
# Run once after cloning to set up directories and check dependencies.
#
# Usage: bash scripts/setup.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== Barely Read Setup ==="
echo ""

# --- 1. Check dependencies ---
echo "[1/4] Checking dependencies..."

errors=0

if command -v uv &> /dev/null; then
  echo "  uv — OK ($(uv --version))"
else
  echo "  uv — NOT FOUND"
  echo "         Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
  errors=$((errors + 1))
fi

if command -v npx &> /dev/null; then
  echo "  npx — OK"
else
  echo "  npx — NOT FOUND (optional, needed for some MCP servers)"
fi

if [ "$errors" -gt 0 ]; then
  echo ""
  echo "Please install missing dependencies and re-run."
  exit 1
fi

# --- 2. Create data directories ---
echo "[2/4] Creating data directories..."
mkdir -p library/papers library/notes memory config .claude/papers
echo "  library/papers/  library/notes/  memory/  config/"

# --- 3. Install Python dependencies ---
echo "[3/4] Installing Python dependencies..."
uv sync 2>&1 | tail -1

# --- 4. Verify MCP servers ---
echo "[4/4] Checking MCP servers..."

if [ -f ".mcp.json" ]; then
  echo "  .mcp.json found"

  # Test arxiv MCP
  if uv tool run arxiv-mcp-server --help &> /dev/null; then
    echo "  arxiv MCP — OK"
  else
    echo "  arxiv MCP — installing..."
    uv tool install arxiv-mcp-server 2>&1 | tail -1
  fi

  echo "  semantic-scholar MCP — will be fetched on first use"
else
  echo "  WARNING: .mcp.json not found. MCP servers may not work."
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Start Claude Code:  claude"
echo "  2. Run:  /br-init"
echo "  3. Try:  /br-search \"your research topic\""
