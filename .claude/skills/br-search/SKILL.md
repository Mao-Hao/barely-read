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
- Use `curl -G --data-urlencode "search={query}" "https://api.openalex.org/works" -d "per_page={half of search.max_results, default 10}" -d "sort=relevance_score:desc"`
- No API key required, 100k requests/day
- Response: JSON with `results` array. Fields may be null — handle gracefully.
- Field mapping: `display_name` (title), `authorships[].author.display_name` (authors), `publication_year`, `doi` (may be null; when present, full URL format `https://doi.org/...`), `cited_by_count`, `topics` (not `concepts` — deprecated 2024), `open_access.is_oa`
- If curl fails or returns non-200, skip OpenAlex silently and continue with other sources.

For multi-topic requests, search each topic separately.

**Web Search Fallback**: If total unique results after dedup < 3, or if any API source returned 0 results, supplement with WebSearch:
- Search `site:scholar.google.com "{query}"` or `site:arxiv.org "{query}"`
- Only include results that have an arxiv ID, DOI, or appear on recognized academic sites (arxiv.org, semanticscholar.org, openreview.net). Discard blog posts, course pages, news articles.
- Merge into the API results before final ranking

This is a personal tool with low volume — web search as a supplementary source is fine.

### 3. Merge + Dedup + Rank

1. **Dedup** (try each method in order):
   - Match by arxiv ID (from arXiv results or Semantic Scholar `externalIds.ArXiv`)
   - Match by DOI — normalize first: strip any `https://doi.org/`, `http://doi.org/`, `http://dx.doi.org/`, `doi:` prefix, then lowercase
   - If neither ID matches, compare titles: lowercase + strip punctuation. If near-identical, treat as duplicate.
   - When duplicates found, **merge fields** from all matching entries (don't just pick one): prefer Semantic Scholar for citation count, arXiv for abstract and categories, OpenAlex for open access status and topics. Keep the most complete author list.

2. **Rank** by (in priority order):
   - **Primary**: semantic relevance to user's `research.topics` and `research.keywords`
   - **Tiebreaker**: citation count
   - **Recency boost**: if `search.prefer_recent` is true, papers from the last 2 years get a significant boost

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

- arxiv MCP unavailable → use Semantic Scholar + OpenAlex, inform user
- Semantic Scholar MCP unavailable → use arxiv + OpenAlex, inform user
- Semantic Scholar rate limited (429) → skip S2 for this search, use other sources
- OpenAlex API error (non-200, timeout, parse failure) → skip silently, use other sources
- All API sources unavailable → fall back to WebSearch on arxiv.org and Google Scholar, note limited functionality
- No results → suggest adjusting terms or broadening time range
- config/user.yaml missing → skip personalized ranking, suggest running /br-init after
- No search terms available (no arguments + no config) → ask user: "What topic should I search for?"
