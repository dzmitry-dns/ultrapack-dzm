# Session hygiene: status narration + context checkpoint

**Status:** done — 2026-09-11, pushed to origin/main (3906ba4), 0.3.35 installed and content-verified from the live cache
**Branch:** main
**Goal:** (1) ultrapack's own skill files carry a local reminder to narrate subagent dispatch and return at the point of dispatch, not only via the distant global CLAUDE.md rule; (2) `/up:make` itself suggests running `/up:summary` at stage transitions once a stage's subagent-dispatch or large-output count crosses a fixed threshold, instead of relying on someone remembering to run it.

## Design

Two independent reliability improvements to ultrapack itself, batched as one task (same shape as the T0+T1 batch).

1. **Dispatch narration.** A single-home reminder block in `_principles.md` (same shape as the existing "Manual-only skills" block): a dispatcher writes one line before dispatching a subagent and one line after it returns. One-line pointers at the four sites that actually dispatch subagents — `uexecute/SKILL.md` (explorer, researcher), `uexecute/waves.md` (parallel implementer dispatch), `ureview/SKILL.md` (reviewer, requirements-reviewer), `commands/summary.md` (summarizer). `uplan` and `uverify` dispatch no subagents and need no pointer.

2. **Context checkpoint.** A new standalone `## Context checkpoint` section in `commands/make.md`, mirroring the existing `## After task is done — docs refresh` section's style: a rule referenced by a one-line pointer from elsewhere, not inlined at each call site. One new sentence is added before the existing text at the start of steps 8 (execute), 9 (verify), and 10 (review): "Run the context checkpoint (see below)." No existing sentence is edited or removed; resume logic (step 2) and the plan-approval gate (step 7) are untouched. The checkpoint fires when, in the stage so far, 3 or more subagents were dispatched or 2 or more large tool outputs were produced; on trigger it prints one advisory line suggesting `/up:summary` and continues without waiting for a reply.

Considered grounding the trigger in a harness-tracked counter (a hook on `SubagentStop`/`TaskCompleted`) instead of the model's own count. Rejected: Claude Code does not document the payload these events carry (the GitHub issue asking for the schema was closed "not planned"), so a hook built on it would rest on unverifiable ground — the opposite of the goal. A separate reactive `PreCompact` hook (checkpoint-on-compaction) was also considered and rejected by the owner: hooks can only run shell commands, not draft a summary, so its value would have been a bare timestamp marker, and it would have been the pack's first hook, a new class of automation running in every project that installs the plugin.

TDD: no (reason: doc-only skill/prose changes, no runtime code; verified by install-and-invoke, matching every other task in this repo).

### Prior art
- `docs/tasks/skill-output-brevity.md:39` — extracted `_brevity.md` as the single home for a rule repeated across many skill files, with one-line pointers at each site; same pattern reused here for the narration rule.
- `docs/tasks/t2-template-realignment.md:19-20` — same single-source-of-truth reasoning (GPC4) applied to a different repeated rule.
- `plugins/up/commands/make.md` `## After task is done — docs refresh` — existing precedent, in this same file, for "standalone rule block + one-line pointer"; reused as the template for `## Context checkpoint`.

### Invariants
- IV1 — The narration rule's text lives in exactly one file (`_principles.md`); every dispatch site references it by a one-line pointer, never restates it.
- IV2 — The context-checkpoint suggestion in `/up:make` never blocks the flow; it is a single advisory line the user can ignore.
- IV3 — No mechanism in this task claims or implies an exact token count; the checkpoint uses only counts the model can observe in-session (dispatch count, large-output count).
- IV4 — The `make.md` edit adds text only; no existing sentence in steps 2, 7, 8, 9, or 10 is modified or removed.

### Assumptions
- AS1 — The dispatcher can reliably count, within one stage, how many subagents it dispatched and how many large tool outputs it produced, well enough to compare against the 3-dispatch / 2-large-output thresholds.

### Unknowns
- UK1 — Whether this checkpoint actually fires reliably in daily use, given that the similarly-worded global status-narration rule already failed to hold. Only real `/up:make` runs after install will show this.

## Plan

Approach: two independent phases, one per Design item, plus a version bump; all three commits land serially on `main`, no interface graph needed for work this small.

### PH1 — Dispatch narration

- **1.1** `plugins/up/skills/_principles.md` (modify) — insert a new `## Dispatch narration` section after the existing `## Manual-only skills` block (after line 16, before line 18): "Before dispatching a subagent (`Agent` tool call) and after it returns, state one line: what's being dispatched / what it returned. The user sees no tool calls, only text — an unannounced dispatch reads as silence. This is the single home of the rule; callers only point here." Respects: IV1.
- **1.2** `plugins/up/skills/uexecute/SKILL.md:75` (modify) — insert one line before the `## When to dispatch \`up:explorer\`` header: "Before dispatching `up:explorer` or `up:researcher` below, see `${CLAUDE_PLUGIN_ROOT}/skills/_principles.md` → Dispatch narration." Covers both the explorer section (75-88) and the researcher section (90-104) with one pointer. Respects: IV1.
- **1.3** `plugins/up/skills/uexecute/waves.md:103` (modify) — insert one line right after the `### Dispatching the wave` header, before the existing "All implementer dispatches..." sentence: "See `${CLAUDE_PLUGIN_ROOT}/skills/_principles.md` → Dispatch narration — one line firing the wave, one line as each implementer's notification arrives." Respects: IV1.
- **1.4** `plugins/up/skills/ureview/SKILL.md:48` (modify) — insert one line before `### 1. Dispatch \`up:reviewer\`` (covers both the 1 and 1b dispatches below it): "See `${CLAUDE_PLUGIN_ROOT}/skills/_principles.md` → Dispatch narration." Respects: IV1.
- **1.5** `plugins/up/commands/summary.md:35` (modify) — insert one line after the `</required>` closing the step-3 dispatch block, before "Dispatch via the Agent tool...": "State one line before dispatching and one line when the draft returns — see `${CLAUDE_PLUGIN_ROOT}/skills/_principles.md` → Dispatch narration." Respects: IV1.
- Commit: `docs(pack): dispatch-narration pointer at every subagent call site`

### PH2 — Context checkpoint in `/up:make`

- **2.1** `plugins/up/commands/make.md:119-129` (modify) — prepend one sentence, "Run the context checkpoint (see below).", before the existing text of step 8 ("Invoke `up:uexecute`..."), step 9 ("Status → `verifying`..."), and step 10 ("Status → `reviewing`..."). No existing sentence changes. Respects: IV2, IV4.
- **2.2** `plugins/up/commands/make.md:176` (modify) — insert a new `## Context checkpoint` section between the end of `## After task is done — docs refresh` (line 175) and `## Stop conditions` (line 177):

  ```markdown
  ## Context checkpoint

  Runs right before invoking the stage skill at steps 8, 9, and 10 — one check per transition, covering everything since the previous checkpoint (step 8's check covers steps 5–7). Count subagents dispatched and tool outputs long enough to fill roughly a screen. Either count at 3+ subagents or 2+ large outputs → print one line: "This session has grown large — consider `/up:summary` before continuing." Then proceed to the stage regardless; advisory only, never a pause.
  ```

  Respects: IV2, IV3, AS1.
- Commit: `docs(pack): advisory context checkpoint at /up:make stage transitions`

### PH3 — Version bump

- **3.1** `plugins/up/.claude-plugin/plugin.json` (modify) — patch bump `0.3.34` → `0.3.35`, per the fork's own versioning rule.
- Commit: `chore(pack): bump to 0.3.35`

### Test strategy
none — doc-only prose/config changes; verified by install-and-invoke (reinstall the fork, re-read the changed files, confirm the new pointers and section render as intended), matching every other task in this repo.

### Order & dependencies
PH1 and PH2 are independent (different files, no shared symbols) — order between them doesn't matter. PH3 comes last since it bumps the version once, after both content phases land.

## Verify

**Result:** passed

Happy-path:
- CK1 — each of the 4 pointer strings names an anchor that exists verbatim in `_principles.md` — held
- CK2 — new `## Dispatch narration` header sits at the same level as its siblings, no structural break — held

Negative:
- CK3 (IV2) — checkpoint text could get mistaken for a stop condition — held: `## Stop conditions` lists nothing about it, and the checkpoint's own text says "never a pause"

Invariants:
- CK4 (IV1) — grepped `plugins/up/` for the narration rule's wording — held, appears exactly once (`_principles.md`)
- CK5 (IV4) — grepped `make.md` for the original step-8/9/10 sentences — held, all three present verbatim

Smoke: fresh `grep`/`sed` reads of all 6 changed files from disk — structure and cross-references are what the plan intended

Goal: proxy only — smoke covers the doc edits themselves; confirming the Goal in practice needs the fork reinstalled as the daily driver (`/plugin marketplace update ultrapack` + `/reload-plugins`) and a live `/up:make` run showing the narration lines and the checkpoint advisory actually fire

## Conclusion

Outcome: both Goal items land in the planned locations (25c8da8, 1545a0b, 251d17d, review fix f53d50d), pushed and installed as 0.3.35 (`installed_plugins.json` gitCommitSha 3906ba4); read the live cache and confirmed the shipped text matches the diff. No live `/up:make` run has yet exercised the narration/checkpoint behavior — that's ordinary use, not a one-off test (UK1).

Invariants:
- IV1 — held. Two of the five pointers (`uexecute/waves.md`, `commands/summary.md`) add a short site-specific clause next to the pointer (wave cadence, dispatch/return cadence) rather than a bare "see X". The substantive rule text still lives only in `_principles.md`, so single-source-of-truth holds, but this reads looser than the invariant's own wording ("never restate") implies — reviewer flagged it below the reporting threshold (confidence 65).
- IV2 — held: checkpoint text is explicit ("advisory only, never a pause"), and `## Stop conditions` doesn't reference it.
- IV3 — held: the checkpoint's trigger uses only in-session-observable counts (dispatch count, large-output count), no token count anywhere in the diff.
- IV4 — held: the original step-8/9/10 sentences are preserved verbatim inside the edited lines.

### Assumptions check
- AS1 — unverifiable from the diff alone; whether the dispatcher actually counts its own dispatches accurately can only be seen from real `/up:make` runs.

### Unknowns outcome
- UK1 — still-open: whether the checkpoint fires reliably in daily use is only observable after install, from real sessions.

### Deviations from plan
- PH2.1 said to prepend the checkpoint sentence before the existing text of steps 9 and 10; shipped after the `Status →` sentence instead — a handoff taken at the checkpoint would otherwise leave the task file one status behind, and step 2's resume would re-run execute on an implemented plan (the case the resume table's `verifying` row exists to prevent). Step 8 keeps the prepended position: step 7 has already written `executing`.

Review findings:
- Important (second dispatch): checkpoint-before-Status ordering in steps 9 and 10 — resolved, see Deviations from plan.

Verified by: two `up:reviewer` dispatches on Fable (one-off dispatch-time overrides, not frontmatter pins), per the user's request; the second caught the ordering finding the first missed.
