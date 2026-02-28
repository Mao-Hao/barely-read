---
name: br-init
description: "Initialize BR environment: guided setup for research profile, directories, and MCP detection"
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

### 1. Welcome + Research Profile

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

### 2. Explanation Preferences

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

### 3. Create Directories

Check and create if missing:

```
library/papers/
library/notes/
memory/
config/
```

### 4. Detect MCP Servers

Test availability of each MCP server:

- **arxiv** — call `search_papers` with "test"
- **semantic-scholar** — call `search_paper` with "test"
- **zotero** — call `zotero_search_items` with "test"

Output results:

```
MCP Servers:
  arxiv            ✓ available
  semantic-scholar ✓ available
  zotero           ✓ available / ✗ unavailable (optional)
```

### 5. Generate Config

Read `src/config/defaults.yaml` as template, fill with user input, write to `config/user.yaml`.

### 6. Welcome Summary

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

- MCP server unavailable → warn but don't block init (mark unavailable, skills degrade gracefully)
- `config/user.yaml` exists → ask whether to overwrite
- User skips an item → use defaults from defaults.yaml
