---
description: End a session so the next one can continue — in one main-session turn, append a dated Handoff block to the active task file and print the one-line `/up:make <task file>` prompt for the next session. Use when the owner asks for a handoff (hands-off, хендзов) or whether the session can be closed.
---

# /up:summary

Write the handoff from what this session already knows. The task file carries the state; the prompt is a pointer to it. One turn, one side effect (the append plus the Owner summary rewrite, committed by path), no questions unless the active task file is genuinely ambiguous.

## Process

### 1. Detect the active task file

```bash
find docs/tasks -maxdepth 2 -name '*.md' -exec ls -t {} + | head
```

(`find`, not a glob: under zsh an unmatched `docs/tasks/*/*.md` aborts the whole command and the command would wrongly conclude there is no task file.)

The active task file is the most recently modified entry whose `**Status:**` enum (the first word of the Status value) is not `done`, `shipped`, or `reference`. If more than one qualifies, take the one this session edited. Ask only if that still leaves more than one. None → see "No active task file" below.

### 2. Ground the state in git

```bash
git status --short
git log -3 --oneline
```

The block reports committed and uncommitted work from this output, not from memory.

### 3. Append the Handoff block

Append at the end of the task file, after `## Conclusion`, with the Edit tool (anchor on the file's last line). Never `cat >> file <<'EOF'`: a shell redirect into a repo file asks the owner for permission. English, 5–12 bullets. Earlier Handoff blocks stay; the newest is always last.

```markdown
### Handoff: YYYY-MM-DD
- Position: <stage or plan phase>; branch: <name>; checkout: <absolute path, when a worktree>; committed: <last sha, short name>; uncommitted: <files, or "none">
- Decided: <decision>, because <reason>
- Dead end: <what was tried>, <why it failed>
- Open: <question waiting on the owner>
- Owner has not seen: <results or findings the owner asked for and has not yet read in chat, or "none">
- First action: <one line, a command where possible>
```

`Decided` and `Dead end` repeat as needed and are omitted when empty; `Open` is at most one line. When step 2 shows uncommitted changes, `First action` starts with committing them. When `Owner has not seen` is not "none", `First action` is "tell the owner those results in plain words": the work step comes after.

Only what the file and git do not already say: decisions taken in chat and their reasons, dead ends, the open question, the next step. Do not restate Design, Plan, or the diff.

Then rewrite `## Owner summary` in place: three bullets, `Done:`, `Left:`, `Owner decides:`, plain English for the owner, no IDs or file paths. Unlike the Handoff block, it restates progress on purpose. A file without the section gets it inserted right under the header lines.

After the append, commit only the task file, by path: `git add <task file>`, run the Cyrillic check of `${CLAUDE_PLUGIN_ROOT}/skills/_principles.md` → Commits (this block carries the owner's chat decisions), then commit `docs(agents): <slug> handoff`. Push when the project's policy allows it. Other uncommitted work stays as it is.

### 4. Print the prompt

A fenced block so it copies whole:

```
/up:make docs/tasks/<slug>.md
```

Use the file's real path: an epic child lives at `docs/tasks/<epic>/<slug>.md`. When the task file's `**Worktree:**` line names a path, the prompt names that checkout path (a plain branch resumes from the main checkout through `/up:make` step 2): `/up:make <worktree>/docs/tasks/<slug>.md`. The prompt loads `/up:make`, whose step 2 reads the Owner summary and the latest Handoff block on resume, so the one line is enough.

Below the fence, outside the prompt, the Closing line (`${CLAUDE_PLUGIN_ROOT}/skills/_principles.md` → Closing line). At a handoff the task is normally not closable; `Left` names the first action. Below it, the Session line (`${CLAUDE_PLUGIN_ROOT}/skills/_principles.md` → Handoff at a wait).

## No active task file

Print the prompt with the state inline and touch no file:

```
Goal: <one sentence>
- Position: ...
- Decided: ...
- Dead end: ...
- Open: ...
- Owner has not seen: ...
- First action: ...
```

Same Closing line and Session line below the fence.

## Rules

- Main session only: no subagent, no transcript lookup, no JSONL.
- One append plus the Owner summary rewrite, no other side effects: the append and its commit (and push, when policy allows), plus, when this command ends a session, the checkout step the project's rules require (for example returning a shared checkout to its default branch). The automatic appends of `/up:make` (steps 1-3 only) never run it. No new file, no other edit.
- At most one question, and only to pick between several in-flight task files edited this session.
- Concrete: exact paths, exact commands, exact error text. Bullets, no prose.
