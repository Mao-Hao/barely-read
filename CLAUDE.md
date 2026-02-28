# Barely Read (BR)

Academic research assistant built on LLM CLI. Helps you search, download, read, and understand papers.

## Commands

| Command | Description |
|---------|-------------|
| `/br-init` | First-time setup: configure your research profile |
| `/br-search [query]` | Search papers across arxiv + Semantic Scholar |
| `/br-download [paper]` | Download a paper and add to library |
| `/br-read [paper]` | Deep-read a paper, generate structured notes |
| `/br-explain [concept]` | Explain a concept tailored to your background |

## Quick Start

```
/br-init                          → configure your profile
/br-search "your research topic"  → find papers
/br-download #1                   → download a paper
/br-read 2401.12345               → generate reading notes
/br-explain "attention mechanism"  → explain a concept
```

## Data

All your data stays local and human-readable:

```
library/papers/  → downloaded PDFs
library/notes/   → reading notes (markdown)
config/          → your preferences (yaml)
```
