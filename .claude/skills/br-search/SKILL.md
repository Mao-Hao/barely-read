---
name: br-search
description: "Search academic papers across arxiv and Semantic Scholar, rank by relevance to user's research"
disable-model-invocation: false
argument-hint: "[query]"
---

# /br-search — Paper Search

## What This Skill Adds

Claude can already call arxiv and Semantic Scholar individually. This skill's real value:
- **Dual-source parallel search** with merge and dedup
- **Personalized ranking** using the user's research profile
- **Relevance annotations** explaining why each paper matters to the user

## Input

The user may express search intent in any form:

- Specific query: "multi-agent reinforcement learning"
- Vague direction: "what's new in my field lately"
- Context-based: "search for papers related to what we just discussed"
- With constraints: "after 2024", "highly cited", "more theoretical"
- Multi-topic: "find papers on both X and Y"
- No arguments: use `config/user.yaml` research topics/keywords to search proactively

**Core principle**: Figure out what the user wants to find. Construct good queries. Don't demand perfect search terms.

## Context

- `config/user.yaml`: research area, keywords, search preferences
- Conversation context (papers, concepts mentioned earlier)

## Steps

### 1. Understand Search Intent

Infer from the user's expression:
- **What to search**: keywords, topics. If vague, supplement with profile from `config/user.yaml`.
- **Time range**: if mentioned; otherwise use `search.default_years_back`.
- **Domain**: infer arxiv categories if a specific field is mentioned (not limited to CS).
- **Quantity**: how many results? Default: `search.max_results`.

If intent is still unclear, ask one brief clarifying question (don't list format requirements).

### 2. Parallel Search

Call both MCP servers simultaneously:

**arxiv MCP** (`search_papers`):
- query: constructed keywords, quote core phrases
- categories: filter if domain info available
- date_from: per time range
- max_results: half of `search.max_results` (default 10)
- sort_by: "relevance"

**Semantic Scholar MCP** (`search_paper`):
- query: natural language query
- limit: half of `search.max_results` (default 10)
- year: per time range
- fields: "paperId,title,abstract,authors,year,citationCount,url,externalIds"

For multi-topic requests, search each topic separately.

### 3. Merge + Dedup + Rank

1. **Dedup**: match by arxiv ID or DOI, keep the richer entry
2. **Rank** by:
   - Semantic relevance to user's `research.topics` and `research.keywords`
   - Citation count (from Semantic Scholar)
   - Recency (weighted if user prefers recent)
3. **Annotate**: one-sentence explanation of relevance to user's research per paper

### 4. Present Results

Numbered table:

```
Search: "{query}"
Sources: arxiv + Semantic Scholar
Results: N papers (after dedup)

| # | Title | Authors | Year | Cites | Relevance |
|---|-------|---------|------|-------|-----------|
| 1 | ...   | ...     | 2025 | 142   | ...       |
| 2 | ...   | ...     | 2024 | 89    | ...       |

Want to download any of these? Or try a different search.
```

Result numbers are valid for the current session — user can reference them directly.

### 5. Detail View (optional)

If the user asks about a specific paper:
- Call Semantic Scholar MCP (`get_paper`) for full info
- Show: full abstract, all authors, venue, citation/reference counts, PDF link

## Output

- Terminal: numbered results table
- No file writes (search is read-only)

## Error Handling

- arxiv MCP unavailable → use Semantic Scholar only, inform user
- Semantic Scholar MCP unavailable → use arxiv only, inform user
- Both unavailable → fall back to WebSearch on arxiv.org, note limited functionality
- No results → suggest adjusting terms or broadening time range
- config/user.yaml missing → skip personalized ranking, suggest running /br-init after

ARGUMENTS: $ARGUMENTS
