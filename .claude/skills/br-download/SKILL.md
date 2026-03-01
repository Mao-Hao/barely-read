---
name: br-download
description: "Download a paper PDF and add it to the library with stub note and index entry"
disable-model-invocation: false
argument-hint: "[paper reference]"
---

# /br-download — Download & Catalog

## What This Skill Adds

Claude can already call `download_paper`. This skill's real value:
- **Library management**: consistent file paths, stub notes from template, index tracking
- **Batch support**: download multiple papers in one request
- **Smart resolution**: figure out which paper the user means from any reference

## Input

The user may specify papers in any form:

- arxiv ID: `2401.12345`
- URL: `https://arxiv.org/abs/2401.12345`
- Search result reference: `#3`, "download the third one"
- Title/keyword: "that attention paper"
- Batch: "download the top 3", "download all of them"
- Fuzzy: "the one with the most citations", "download that one too"
- Discovery: "download some good papers on X" (search first, then download)
- No arguments: if context has obvious candidates (e.g., just searched), ask which ones

**Core principle**: Figure out what paper(s) the user wants. Search if needed. Don't reject because of format.

## Context

- `config/user.yaml`: user config (for note template)
- `library/index.yaml`: existing paper index
- Conversation context (search results, mentioned papers)

## Steps

### 1. Resolve Paper(s)

Determine one or more paper IDs. The paper_id is:
- **arxiv paper** → arxiv ID (e.g., `2401.12345`)
- **Non-arxiv paper** → DOI with `/` replaced by `_` (e.g., `10.1038_s41586-024-07487-w`)

Resolution:
- Exact reference → extract ID directly
- Search result reference → look up from session context
- Fuzzy reference → infer from context, confirm if ambiguous
- Discovery request → search first, select top results, tell user what you picked
- Batch → resolve each, execute steps 2-6 **sequentially** for each paper (avoid parallel index writes)

### 2. Check Existing

Read `library/index.yaml` (if exists), check if paper_id already present:
- Exists → tell user, ask whether to re-download
- New → continue

### 3. Fetch Metadata

Call arxiv MCP (`search_papers`) or Semantic Scholar MCP (`get_paper`):
- title, authors, year, abstract, doi, url

### 4. Download PDF + Convert to Markdown

Use `{safe_id}` (sanitized paper_id, `/` → `_`) for all file paths below.

**Step 4a: Download PDF**

For arxiv papers:
1. Call arxiv MCP (`download_paper`)
2. Copy from MCP storage: `cp .claude/papers/{arxiv_id}.pdf library/papers/{safe_id}.pdf`
3. Fallback: `curl -L -o library/papers/{safe_id}.pdf https://arxiv.org/pdf/{arxiv_id}.pdf`

For non-arxiv papers:
- Skip to Error Handling → paywalled fallback. Most non-arxiv papers require subscription access.

**Step 4b: Convert to Markdown (arxiv papers only)**

Call arxiv MCP (`read_paper`) to get the markdown version (converted from LaTeX source — much better quality than PDF parsing).

Write to `library/papers/{safe_id}.md`.

If `read_paper` fails (conversion not available), skip silently — br-read will fall back to reading the PDF directly.

### 5. Create Stub Note

Read `templates/paper-note.md`, fill metadata fields:
- paper_id, title, authors, year, url, doi
- status: stub
- created: today's date
- tags: 2-3 keywords extracted from abstract
- cites: if Semantic Scholar metadata includes references with arxiv IDs, list as `[[id]]`. Don't try to extract from abstract text — it rarely contains IDs.

Write to `library/notes/{safe_id}.md`.

### 6. Update Index

Update `library/index.yaml` (via `uv run tools/update_index.py` or direct Read+Write):

```yaml
papers:
  "{paper_id}":
    title: "..."
    authors: [...]
    year: 2025
    doi: "..."
    url: "https://arxiv.org/abs/{arxiv_id}"  # or https://doi.org/{doi} for non-arxiv
    tags: [...]
    status: downloaded  # or pending_pdf if PDF unavailable
    pdf_path: "library/papers/{safe_id}.pdf"
    note_path: "library/notes/{safe_id}.md"
    added_date: "YYYY-MM-DD"
    read_date: ""
```

### 7. Confirm

Single paper:
```
Downloaded: {title}
Authors: {authors}
PDF: library/papers/{arxiv_id}.pdf

Want me to walk you through this paper? Or download more.
```

Batch:
```
Downloaded N papers:
  1. {title_1}
  2. {title_2}
  ...

Want me to walk you through any of them?
```

## Output

- `library/papers/{safe_id}.pdf` — paper PDF (archive)
- `library/papers/{safe_id}.md` — paper markdown (for reading, if conversion succeeded)
- `library/notes/{safe_id}.md` — stub note (metadata filled, content pending)
- `library/index.yaml` — updated index

## Error Handling

- arxiv MCP unavailable → fall back to curl
- PDF download failed (paywalled or unavailable):
  1. Check if PMC has an open-access version (search by DOI or title)
  2. If not, provide the direct link and clear instructions:
     ```
     This paper requires subscription access.
     Link: https://doi.org/{doi}
     Please download the PDF and place it at: library/papers/{id}.pdf
     Once done, say "continue" and I'll create the note and index entry.
     ```
  3. Optionally try `open "https://doi.org/{doi}"` to open in browser (macOS)
  4. If Chrome MCP is connected, attempt to navigate and download automatically
  5. Still create the stub note (Step 5) and index entry (Step 6) with status: `pending_pdf` so the paper is tracked
- Paper already exists → ask whether to re-download (merge logic in update_index.py preserves user data)
- index.yaml missing → create new file
- Batch partial failure → report successes and failures, keep successful ones
