# Barely Read (BR)

Academic research assistant built on LLM CLI. Helps you search, download, read, and understand papers.

## Commands

| Command | Description |
|---------|-------------|
| `/br-init` | First-time setup: configure your research profile |
| `/br-search [query]` | Search papers across arxiv + Semantic Scholar + OpenAlex |
| `/br-download [paper]` | Download paper(s), create stub notes, update library index |
| `/br-read [paper]` | Interactive paper walkthrough with adjustable depth |
| `/br-explain [concept]` | Explain a concept tailored to your background |

All commands accept flexible input — paper titles, search result numbers (#3), fuzzy references ("that attention paper"), or no arguments at all. Just say what you mean.

## Quick Start

```
/br-init                          → configure your profile
/br-search "your research topic"  → find papers
"download #1"                     → download a paper
/br-read 2401.12345               → walk through a paper
/br-explain "attention mechanism"  → explain a concept
```

After the initial command, all follow-up is natural language. Ask questions, go deeper, compare papers — just talk.

## Data

All your data stays local and human-readable:

```
library/papers/  → downloaded PDFs
library/notes/   → reading notes (markdown)
config/          → your preferences (yaml)
```

Notes are standard markdown with relative links. Point Obsidian (or any editor) at `library/notes/` and it just works.
