---
name: br-init
description: "Initialize BR environment: dependency check, directory setup, research profile, MCP detection"
disable-model-invocation: false
argument-hint: ""
---

# /br-init — First-Time Setup

## Input

Usually no arguments — interactive guided setup. But the user may provide info upfront:

- "I'm a PhD student working on NLP, focusing on LLM alignment" → extract profile, only confirm/fill gaps
- No arguments → guide step by step

If `config/user.yaml` already exists, ask: reconfigure / keep / modify specific items.

## Steps

### 1. Check Dependencies

Run these checks silently using Bash. Only report problems.

**uv** (required for MCP servers and Python tools):
```bash
command -v uv
```
- If missing → tell the user: "BR needs uv (a Python package manager). Install it with:" and show: `curl -LsSf https://astral.sh/uv/install.sh | sh`. Wait for user to install, then re-check.
- If present → continue silently.

**Python dependencies** (pyyaml for index management):
```bash
uv sync
```
- Run this in the project directory. It installs dependencies from pyproject.toml.
- If it fails, try `uv pip install pyyaml` as fallback.
- Don't bother the user with this unless it fails.

### 2. Create Directories

Check and create if missing (silently, just do it):

```
library/papers/
library/notes/
memory/
config/
.claude/papers/
```

If `library/index.yaml` does not exist, create it with initial content:
```yaml
papers: {}
```

### 3. Welcome + Research Profile

Collect the following. Adapt your approach based on how much the user provides at once — don't mechanically ask one by one if they've already told you everything.

Information needed:
- Research area
- Specific topics of interest
- Common search keywords
- Career stage (undergrad / master / PhD / postdoc / faculty / industry)

Guided prompts (only use when user hasn't provided info proactively):

```
Welcome to Barely Read!

What's your research area?
> [user input]

Specific topics you care about (comma-separated):
> [user input]

Common search keywords (comma-separated):
> [user input]

Your current stage:
  1. Undergrad
  2. Master's
  3. PhD (default)
  4. Postdoc
  5. Faculty
  6. Industry
```

### 4. Explanation Preferences

```
Paper explanation depth:
  1. Brief (key points only)
  2. Standard
  3. Detailed (with derivations) (default)

Include math formulas? [Y/n]

Preferred language:
  1. English (default)
  2. 中文
  3. Mixed
```

### 5. Detect Search Sources

Test availability of each search source:

**MCP servers** (call each with a test query):
- **arxiv** — call `search_papers` with "test"
- **semantic-scholar** — call `search_paper` with "test"
- **zotero** — call `zotero_search_items` with "test"

**APIs** (test via Bash):
- **OpenAlex** — run: `curl -s -o /dev/null -w "%{http_code}" "https://api.openalex.org/works?search=test&per_page=1"` (expect 200)

Output results:

```
Search Sources:
  arxiv            ✓ available (MCP)
  semantic-scholar ✓ available (MCP)
  openalex         ✓ available (API, no key needed)
  zotero           ✓ available / ✗ unavailable (optional)
```

### 6. Generate Config

Read `config/defaults.yaml` as template, fill with user input, write to `config/user.yaml`.

### 7. Welcome Summary

```
BR setup complete!

Research area: {area}
Topics: {topics}
Preferences: {depth}, {language}

You can:
  /br-search [query]     search papers
  /br-download [paper]   download a paper
  /br-read [paper]       walk through a paper with me
  /br-explain [concept]  explain a concept

Try it out — tell me what you'd like to search for.
```

## Output

- `config/user.yaml` — user config file
- Terminal: welcome summary + available commands

## Error Handling

- uv not installed → guide user through installation, don't proceed until ready
- Python deps fail → try fallback install, warn if still failing (skills still work, just index updates may need manual handling)
- MCP server unavailable → warn but don't block init (mark unavailable, skills degrade gracefully)
- `config/user.yaml` exists → ask whether to overwrite
- User skips an item → use defaults from defaults.yaml
