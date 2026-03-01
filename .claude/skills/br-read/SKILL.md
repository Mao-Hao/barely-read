---
name: br-read
description: "Interactive paper walkthrough — AI explains the paper to you, saves notes as byproduct"
disable-model-invocation: false
argument-hint: "[paper reference]"
---

# /br-read — Paper Walkthrough

## What This Skill Adds

Claude can already read PDFs and explain them. This skill's real value:
- **User context loading**: personalize explanation to user's research background
- **Note saving**: structured notes from template on request
- **Library integration**: track read status in index

Everything else — how to explain, what structure to use, what depth — let Claude handle naturally based on the paper and the user's questions.

## Input

The user may refer to a paper in any form:

- arxiv ID: `2401.12345`
- File path: `library/papers/xxx.pdf` or any PDF path
- Search result: `#3`, "walk me through the third one"
- Fuzzy: "the one I just downloaded", "that attention paper"
- Browse library: "what haven't I read yet?"
- No arguments: list recently downloaded but unread papers, let user pick

**Core principle**: Find the paper. If it's not downloaded, offer to download it. Don't stop because of missing ID.

## Context

- `config/user.yaml`: user's research area, explanation preferences
- `library/index.yaml`: paper index (PDF paths, read status)
- `templates/paper-note.md`: note template (for saving)
- Conversation context (search results, recently mentioned papers)

## Steps

### 1. Locate Paper

Find the PDF:
- Exact reference → look up `library/index.yaml` for `pdf_path`
- File path → use directly
- Fuzzy reference → match from context or index
- No arguments → list unread papers (status: downloaded), let user pick
- Status is `pending_pdf` → the paper is tracked but the PDF isn't available (e.g., paywalled). Tell the user: "This paper's PDF hasn't been downloaded yet. You can place it at `library/papers/{id}.pdf` and I'll read it, or I can try downloading again."  Do NOT loop trying to re-download.
- PDF not found → "This paper isn't downloaded yet. Want me to get it?"

### 2. Ask About Depth

Before reading, briefly check what the user wants:

```
{title}
{authors} ({year})

How deep should I go?
  1. Quick overview — key findings, 1-2 min
  2. Standard — problem, method, results, 5 min (default)
  3. Deep dive — technical details and derivations
```

The user can pick a number or say it naturally ("just give me the gist", "I want all the details"). Default to `config/user.yaml` → `explanation.depth`.

### 3. Read Paper + Load Context

- Check if `library/papers/{id}.md` exists (markdown version, converted from LaTeX source)
  - If yes → read the markdown (faster, fewer tokens, more accurate)
  - If no → read the PDF using Claude's native Read tool
- For long papers, read in stages (abstract+intro+method first, then results+conclusion)
- Load user's research area and keywords from `config/user.yaml`

### 4. Explain the Paper

**Explain conversationally. Do NOT follow a rigid template.** Adapt your explanation to what's actually interesting and important about this specific paper. Use the user's research background to emphasize what's relevant to them.

General guidance by depth:
- **Quick**: core contribution + key findings + relevance to user. A few paragraphs.
- **Standard**: what problem, why it matters, how they solved it, what they found, strengths/weaknesses, relevance to user.
- **Deep**: everything in standard + technical details (formulas with intuitive explanations), experimental design, open questions.

But these are guidelines, not templates. If a paper's main contribution is a proof, focus on the proof. If it's an empirical study, focus on the experiments. Match the explanation to the paper.

### 5. Interactive Follow-up

After the initial explanation:

```
---
Anything you'd like to dig into? For example:
  "Tell me more about the method"
  "What does XX mean?"
  "How does this compare to [another paper]?"
  "Save notes"
  "Next paper"
```

The user can:
- Ask follow-up questions → answer in current context
- Say "save notes" → execute Step 6
- Move on to another paper → restart from Step 1
- Change topic → exit naturally

### 6. Save Notes (on request)

When the user says "save notes", "save this", etc.:

1. Organize the explanation into `templates/paper-note.md` format
2. Fill frontmatter (paper_id, title, authors, year, status: read, tags)
3. Write to `library/notes/{arxiv_id}.md`
4. Update `library/index.yaml` (status: read, read_date, tags)
5. Confirm: "Notes saved to library/notes/{arxiv_id}.md"

## Output

- Terminal: interactive paper walkthrough
- `library/notes/{arxiv_id}.md` — notes (only when user requests)
- `library/index.yaml` — updated (only when saving notes)

## Error Handling

- PDF not found → offer to download
- PDF unreadable → report error, suggest re-download
- config/user.yaml missing → use default preferences, suggest /br-init after
