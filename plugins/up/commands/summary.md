---
description: End a session so the next one can continue — append a dated Handoff block to the active task file and print the one-line prompt for the next session. Runs in the main session in one turn, no subagent, no transcript.
---

# /up:summary

Write the handoff from what this session already knows. The task file carries the state; the prompt is a pointer to it. One turn, one side effect (the append), no questions unless the active task file is genuinely ambiguous.

## Process

### 1. Detect the active task file

```bash
ls -t docs/tasks/*.md docs/tasks/*/*.md 2>/dev/null | head
```

The active task file is the most recently modified entry whose `**Status:**` enum (the text before the first ` — `) is not `done`, `shipped`, or `reference`. If more than one qualifies, take the one this session edited. Ask only if that still leaves more than one. None → see "No active task file" below.

### 2. Ground the state in git

```bash
git status --short
git log -3 --oneline
```

The block reports committed and uncommitted work from this output, not from memory.

### 3. Append the Handoff block

Append at the end of the task file, after `## Conclusion`. English, 5–12 bullets. Earlier Handoff blocks stay; the newest is always last.

```markdown
### Handoff — YYYY-MM-DD
- Position: <stage or plan phase>; committed: <last sha, short name>; uncommitted: <files, or "none">
- Decided: <decision>, because <reason>
- Dead end: <what was tried>, <why it failed>
- Open: <question waiting on the owner>
- First action: <one line, a command where possible>
```

`Decided` and `Dead end` repeat as needed and are omitted when empty; `Open` is at most one line. When step 2 shows uncommitted changes, `First action` starts with committing them.

Only what the file and git do not already say: decisions taken in chat and their reasons, dead ends, the open question, the next step. Do not restate Design, Plan, or the diff.

### 4. Print the prompt

A fenced block so it copies whole:

```
Продолжи docs/tasks/<slug>.md
```

`/up:make` reads the latest Handoff block on resume, so the one line is enough.

Below the fence, outside the prompt, one sentence for the owner in the owner's language: where the work stands and what happens next.

## No active task file

Print the prompt with the state inline and touch no file:

```
Goal: <one sentence>
- Position: ...
- Decided: ...
- Dead end: ...
- Open: ...
- First action: ...
```

Same owner sentence below the fence.

## Rules

- Main session only: no subagent, no transcript lookup, no JSONL.
- One side effect: the append. No commit, no new file, no other edit.
- At most one question, and only to pick between several in-flight task files edited this session.
- Concrete: exact paths, exact commands, exact error text. Bullets, no prose.
