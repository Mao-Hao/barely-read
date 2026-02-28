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

### 3. Explain

**Explain naturally. Adapt to the concept and the user's level.** Don't force a rigid structure. Some concepts need an analogy first. Some need a formal definition. Some need a worked example. Match your approach to what works best.

Guidance (not a template):
- Start with intuition — why does this concept exist? What problem does it solve?
- Give precision where needed — definitions, formulas (if user wants math)
- Connect to the user's research — how is this relevant to what they do?
- Reference library papers if found in Step 2

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

ARGUMENTS: $ARGUMENTS
