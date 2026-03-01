---
name: br-explain
description: "Explain an academic concept tailored to user's research background and preferences"
disable-model-invocation: false
argument-hint: "[concept or question]"
---

# /br-explain — Concept Explainer

## What This Skill Adds

Claude is already great at explaining things. This skill adds:
- **User context**: load research background from profile for personalized explanations
- **Library linking**: find and reference related papers from the user's own library

That's it. Don't constrain how Claude explains — just give it context and let it teach.

## Input

The user may ask about anything in any form:

- Specific term: "variational inference", "KL divergence"
- Question from a paper: "what does the loss in eq.3 actually do?"
- Comparison: "what's the difference between LSTM and Transformer?"
- Vague: "I don't get the regularization part"
- Broad topic: "reinforcement learning" → ask which aspect they want to understand
- Research connection: "could this method work for my research?"

**Core principle**: Understand what the user wants to learn. Use their background and current context to explain it well. Don't be a dictionary — be a teacher.

## Context

- `config/user.yaml`: user's background, explanation preferences (depth, math, language)
- `library/notes/`: existing paper notes (for linking related papers)
- Conversation context (papers being discussed, previous explanations)

## Steps

### 1. Understand the Question + Load Context

Read `config/user.yaml` (if missing, use defaults: detailed, include_math, graduate, en):
- Research area, explanation depth, math preference, language

Determine what to explain:
- If referencing current conversation (a paper, a concept just mentioned), use that context
- If too broad, ask briefly which aspect they care about

### 2. Search Library for Related Papers

Search `library/notes/` for papers related to the concept:
- Grep for keywords
- If found, note paper_id and relevant passages for reference

### 3. Explain (Knowledge-First)

**Start from your own knowledge. Then verify.**

First, explain the concept using what you know — intuition, definitions, examples. Don't search first. The user is here to learn, not to wait for API calls.

Guidance (not a template):
- Start with intuition — why does this concept exist? What problem does it solve?
- Give precision where needed — definitions, formulas (if user wants math)
- Connect to the user's research — how is this relevant to what they do?
- Reference library papers if found in Step 2

### 3b. Verify + Cite Real Papers

After explaining, search to verify and enrich:
- Use Semantic Scholar or arxiv MCP to find the seminal paper(s) for this concept
- Confirm key claims are accurate (avoid hallucinated citations)
- If verification reveals your explanation was inaccurate or incomplete, correct it explicitly: "Actually, I should clarify..." — don't silently drop the correction
- Add real paper references with IDs:
  ```
  Key references:
  - Vaswani et al. (2017) "Attention Is All You Need" [arxiv:1706.03762]
  - ...
  Want me to download any of these?
  ```

This "explain first, cite after" flow avoids blocking the explanation on API calls while ensuring accuracy.

### 4. Link Related Papers

If Step 2 found related notes:

```
Related papers in your library:
- [{title}](library/notes/{id}.md): {how this paper uses/discusses the concept}
```

### 5. Output

Print explanation to terminal (no file writes).

End with:
```
---
Want to go deeper? For example:
  "Explain more"
  "Give me an example"
  "Search for related papers"
```

## Output

- Terminal: explanation
- No file writes (explanations are ephemeral)

## Error Handling

- Overly broad concept → ask which aspect to focus on
- config missing → use defaults, suggest /br-init after
- MCP unavailable for verification → explain anyway, note that citations are unverified
