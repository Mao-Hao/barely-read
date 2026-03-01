---
name: br-update
description: "Refresh BR environment after updates: re-check dependencies and search sources"
argument-hint: ""
---

# /br-update — Post-Update Refresh

Run this after pulling a new version of BR. Skips profile setup, only refreshes environment checks.

## Steps

### 1. Check Dependencies

Run silently, only report problems:

```bash
command -v uv
uv sync
```

If `uv sync` fails, try `uv pip install pyyaml` as fallback.

### 2. Detect Search Sources

**MCP servers** (call each with a test query):
- **arxiv** — call `search_papers` with "test"
- **semantic-scholar** — call `search_paper` with "test"
- **zotero** — call `zotero_search_items` with "test"

**APIs** (test via Bash):
- **OpenAlex** — run: `curl -s -o /dev/null -w "%{http_code}" "https://api.openalex.org/works?search=test&per_page=1"` (expect 200)

### 3. Create Missing Directories

Check and create if missing (silently):

```
library/papers/
library/notes/
memory/
config/
.claude/papers/
```

### 4. Report

```
BR environment refreshed!

Search Sources:
  arxiv            ✓ available (MCP)
  semantic-scholar ✓ available (MCP)
  openalex         ✓ available (API, no key needed)
  zotero           ✓ available / ✗ unavailable (optional)

Config: config/user.yaml ✓ (unchanged)
```

If `config/user.yaml` is missing, suggest running `/br-init` instead.
