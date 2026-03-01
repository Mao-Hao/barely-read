# Barely Read

Academic research assistant as a Claude Code skill pack. Search, download, read, and understand papers — all from the terminal.

## What It Does

You talk to Claude. Claude talks to arxiv and Semantic Scholar. Papers get downloaded, explained, and organized into markdown notes you actually own.

```
you: /br-search "multi-agent reinforcement learning"
  → ranked results from arxiv + Semantic Scholar

you: download #3
  → PDF saved, stub note created, index updated

you: /br-read 2401.12345
  → Claude walks you through the paper interactively

you: what does the loss function in eq.3 actually do?
  → tailored explanation based on your research background
```

No web UI. No database. No vendor lock-in. Just markdown files and a conversation.

## Examples

**Explore a new field:**
```
you: /br-search "what's new in protein folding"
you: download the top 3
you: walk me through the first one
```

**Catch up on your area:**
```
you: /br-search
  → (no query — BR uses your profile to search your topics automatically)
you: anything interesting?
you: download that one and explain it
```

**Understand something from a paper:**
```
you: /br-explain "what's the difference between VAE and diffusion models?"
you: how is this used in the paper I just read?
```

**Batch download for a literature review:**
```
you: /br-download some recent papers on graph neural networks for molecules
  → BR searches, picks top results, downloads them all
you: what haven't I read yet?
you: /br-read
  → lists unread papers, you pick one
```

**Quick triage:**
```
you: /br-read 2401.12345
you: just give me the gist
  → quick overview, 2 paragraphs
you: ok save notes, next paper
```

All follow-up interaction is natural language. You don't need to remember command syntax — just say what you want.

## Workflow

```
/br-init                       → configure your research profile (once)
        ↓
/br-search "query"             → search arxiv + Semantic Scholar
        ↓                        returns numbered results
"download #3"                  → download PDF + create stub note
        ↓
/br-read 2401.12345            → interactive walkthrough
        ↓                        ask follow-ups in natural language
"save notes"                   → notes written to library/notes/
        ↓
/br-explain "some concept"     → concept explainer (links to your papers)
```

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (CLI)
- Recommended model: **Sonnet 4.6** (good balance of quality and cost). Opus 4.6 for deeper analysis.

## Install

```bash
git clone https://github.com/Mao-Hao/barely-read.git
cd barely-read
claude
```

Then run `/br-init`. It will check dependencies (install [uv](https://docs.astral.sh/uv/) if missing), set up directories, detect MCP servers, and configure your research profile — all in one step.

## Commands

| Command | What it does |
|---------|-------------|
| `/br-init` | First-time setup: research profile, preferences, MCP detection |
| `/br-search [query]` | Search papers across arxiv + Semantic Scholar |
| `/br-download [id]` | Download PDF, create stub note, update library index |
| `/br-read [id]` | Interactive paper walkthrough with adjustable depth |
| `/br-explain [concept]` | Explain a concept tailored to your background |

Commands accept flexible input — paper titles, search result numbers, fuzzy references like "that attention paper", or no arguments at all. Just say what you mean.

## How It Works

BR is a set of [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) — markdown instruction files that teach Claude domain-specific workflows. When you run `/br-search`, Claude reads the skill definition, calls MCP servers (arxiv, Semantic Scholar), and formats the results.

No custom runtime. No API wrapper. Claude Code *is* the runtime.

### Data

Everything stays local and human-readable:

```
library/
  papers/    → downloaded PDFs
  notes/     → reading notes (markdown)
  index.yaml → paper metadata index
config/
  user.yaml  → your preferences
```

Notes are standard markdown with relative links. Point Obsidian (or any editor) at `library/notes/` and it just works.

## Roadmap

- [x] Core skills: search, download, read, explain
- [ ] Polish: OpenAlex search source, usage logging, UX improvements
- [ ] Note format: standardized frontmatter + wiki-links (Obsidian-compatible)
- [ ] Paper comparison (`/br-compare`)
- [ ] Beyond papers: URL/PDF archiving + explanation
- [ ] Publish to Claude Code plugin marketplace

## License

MIT
