---
name: br-search
description: "Search academic papers across arxiv, Semantic Scholar, OpenAlex, and web, rank by relevance to user's research"
disable-model-invocation: false
argument-hint: "[query]"
---

# /br-search — Paper Search

## What This Skill Adds

Claude can already call arxiv and Semantic Scholar individually. This skill's real value:
- **Multi-source search** (arxiv + Semantic Scholar + OpenAlex + web fallback) with merge and dedup
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

Call all search sources in parallel:

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

**OpenAlex API** (direct HTTP via Bash, no MCP needed):
- Endpoint: `https://api.openalex.org/works?search={query}&per_page=10&sort=relevance_score:desc`
- No API key required, 100k requests/day
- Response structure: results are in the `results` array (not top-level)
- Field mapping: `display_name` (title), `authorships[].author.display_name` (authors), `publication_year`, `doi` (full URL format: `https://doi.org/...` — strip prefix for matching), `cited_by_count`, `topics` (not `concepts` — deprecated 2024), `open_access.is_oa`
- Call strategy: **always call in parallel** with arxiv + S2 for maximum coverage. Especially valuable for non-CS fields, interdisciplinary searches, and citation analysis

For multi-topic requests, search each topic separately.

**Web Search Fallback**: If API results are sparse (< 3 papers) or the user's query is broad/exploratory, supplement with WebSearch:
- Search `site:scholar.google.com "{query}"` or `site:arxiv.org "{query}"`
- Extract paper titles and IDs from results
- Merge into the API results before dedup

This is a personal tool with low volume — web search as a supplementary source is fine.

### 3. Merge + Dedup + Rank

1. **Dedup**: match by arxiv ID or DOI (normalize DOIs by stripping `https://doi.org/` prefix before comparing), keep the richer entry
2. **Rank** by:
   - Semantic relevance to user's `research.topics` and `research.keywords`
   - Citation count (from Semantic Scholar)
   - Recency (weighted if user prefers recent)
3. **Annotate**: one-sentence explanation of relevance to user's research per paper

### 4. Present Results

Numbered table:

```
Search: "{query}"
Sources: {list sources actually used, e.g. "arxiv + Semantic Scholar + OpenAlex"}
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
- Both unavailable → fall back to WebSearch on arxiv.org and Google Scholar, note limited functionality
- No results → suggest adjusting terms or broadening time range
- config/user.yaml missing → skip personalized ranking, suggest running /br-init after
- No search terms available (no arguments + no config) → ask user: "What topic should I search for?"
