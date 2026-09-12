# Handoff prompt: replace the summarizer round-trip with a prompt written from the live context

**Status:** executing — plan approved 2026-09-12
**Branch:** main
**Goal:** `/up:summary` on cccc-monorepo, in one main-session turn with no subagent and no question, appends a dated `### Handoff` block to the active task file and prints a one-line prompt (`Продолжи docs/tasks/<slug>.md`); the next session, given only that line, reads the block via `/up:make` resume and starts with the recorded first action. Confirmed by one real handoff on cccc-monorepo, not by the diff alone.

## Design

Purpose: replace the summarizer round-trip (subagent, JSONL phrase search, verbatim re-quote, destination question) with a write the main session does itself from the context it already holds. Measured on 4 real runs, the old path cost 2.7M to 7.7M cache-read tokens and 3 to 8 minutes per handoff and failed its transcript search every time; the two hand-written prompts (2026-09-08, run D) took under a minute and were consumed identically.

Chosen approach: rewrite `/up:summary` in place (same name, so the checkpoint line in `make.md` and the owner's habit keep working), delete `agents/summarizer.md`, and make the task file carry the handoff so the prompt can be a single pointer.

What the rewritten command does, in order:
1. Detect the active task file: the most recently modified `docs/tasks/**/*.md` whose Status enum is not `done`, `shipped`, or `reference`. If several qualify, take the one this session edited. Ask only if that still leaves more than one.
2. Ground state with `git status --short` and `git log -3 --oneline`, so the block reports what is committed and what is not from evidence, not memory.
3. Append `### Handoff — YYYY-MM-DD` at the end of the task file (after `## Conclusion`), English, 5-12 bullets, only what the file and git do not already hold: position in the plan (phase, committed vs uncommitted), decisions taken in chat with reasons, dead ends tried, open question waiting on the owner, first action for the next session. No section is re-owned: `## Conclusion` stays `ureview`'s; blocks stack by date, newest last, and remain as history after `done`.
4. Print the prompt in a fenced block so it copies whole: one line, `Продолжи docs/tasks/<slug>.md`. Below the fence, outside the prompt, one sentence for the human in the owner's language: where the work stands and what happens next (run D showed a model-oriented prompt does not orient the owner hours later).
5. No commit: the command does not commit the task file; the block's first-action bullet says "commit the task file" when there are uncommitted changes, and the normal stage flow commits as usual.

No active task file (ad hoc session, e.g. the Bun 1.4 decision): print the prompt with a Goal line and the same bullets inline, touch no file. This matches run A, which was consumed from chat.

`/up:make` step 2 (resume check) gains one sentence: if the task file ends with one or more `### Handoff — <date>` blocks, read the latest one before resuming at the Status stage. This is what makes the one-line prompt sufficient. The task file template, steps 5-12, and the context checkpoint text are untouched; the checkpoint keeps saying "consider `/up:summary`".

Rejected alternatives:
- New command name with `/up:summary` kept or deleted: two mechanisms for one purpose, or a rename the owner has to relearn; "improve, never break" argues for in-place.
- Handoff block inside `## Conclusion` as `### Summary — <date>` (today's convention): `ureview` fills Conclusion later and could clobber or trip over it.
- Prompt carries the whole delta with no file write: measured pasted recaps cost about twice the turns of a pointer, and a closed chat loses the delta.
- Keep `summarizer` for the no-task-file case: keeps the broken transcript search alive for one rare path.

Backwards compatibility: nothing outside `commands/summary.md` and README references `up:summarizer` (checked in this repo, cccc-monorepo, and the global CLAUDE.md). Five cccc task files hold old `### Summary —` blocks; nothing reads them programmatically, they stay. `/up:make` resume behavior for files without a Handoff block is unchanged.

Parallel work: `docs/tasks/upstream-integration.md` is being executed in another session and may touch `make.md` (template, Context section) and `plugin.json` (version). This task edits `make.md` step 2 only, one sentence; merge conflicts are limited to that line and the version number.

TDD: no (reason: doc-only plugin prose, no runtime code; verified by install-and-invoke on a real cccc-monorepo handoff).

### Owner constraints (stated 2026-09-11)
- Ultrapack works today. Improve it; never break the working flow. Any change must keep `/up:make` resume (step 2, Status-driven) behaving exactly as now.
- This session is research plus at most an initial design pass. Planning, execution, and verification happen in later sessions.
- The owner uses only Claude Code, not Codex or Pi.

### Research findings (2026-09-11)

Source: sweep of all session transcripts (299 in cccc-monorepo, 6 in packages-db, 5 in ultrapack-dzm) by a subagent; details in the transcript of this session.

Usage. `/up:summary` (summarizer dispatch) ran 4 times, all in cccc-monorepo, all between 2026-09-03 and 2026-09-11. One more handoff on 2026-09-08 was done with no skill: the owner asked "напиши промпт и продолжим в новой сессии", the main session ran two git commands and wrote the prompt in chat in 52 seconds.

Cost and outcome per run:

| Run | Date | Wall time | Main-session cache-read tokens | Subagent cache-read tokens | Draft written to |
|---|---|---|---|---|---|
| A, CATS-1622, `f3c64613…` | 09-03 | 2m45s to draft, ~7m total | 2.7M | 0.7M | chat only |
| B, CATS-1699, `dc1fdd9a…` | 09-10 | 5m15s | 7.2M | 3.1M | task file Conclusion (after AskUserQuestion) |
| C, CATS-1576, `3cf581ad…` | 09-11 | 7m55s | 7.7M | 2.2M | chat, then task file after the owner asked separately |
| D, CATS-1576, `d7d867ff…` | 09-11 | killed at 48s | 5.0M wasted | 0.7M wasted | owner said "просто напиши prompt"; hand-written in 15s to `docs/local/cats-1576-continue-prompt.md` |

Failure patterns:
1. The summarizer's JSONL search failed 4 of 4 times: its grep lists `~/.claude-work/projects/…/*.jsonl`, that dir does not exist here, and zsh aborts the whole command on the unmatched glob. Three times the fallback read recovered in one step; in run B two same-day session files shared a timestamp and the subagent spent 59 turns disambiguating.
2. Cost is dominated by re-reading cached context (millions of tokens per run on both sides), not by new work.
3. Destination differed every run (chat, task file, `docs/local/`); the documented "ask where to save" step happened once in four.
4. Run D is direct evidence for the owner's proposal: a prompt written by the main session from what it already knew was consumed by the next session identically to a full summarizer draft.

What works and must be preserved:
- Every draft was consumed by the very next session, 6 to 90 seconds later, whether pasted verbatim (A, D) or referenced as a task-file section (B, C). The next session's `/up:make` resume read Status and continued correctly.
- After run D the owner returned hours later and asked "что тут о чём, объясни на русском": a prompt that orients the model does not orient the human. The design should account for a short human-facing line separate from the model prompt.

Upstream note: btseytlin/ultrapack's Codex variant (`skills/summary/SKILL.md` on `upstream/main`) already writes the handoff "from the current conversation, task file, git state, and repository; do not assume a Claude JSONL transcript exists", with seven sections and no subagent. Its wording is a candidate starting point.

Session-opener sweep (subagent report, 2026-09-11). 310 session files, 170 with 5+ real user messages (166 cccc-monorepo). "Turn" = one distinct assistant message id; tokens = input + cache tokens summed over turns until the first Edit/Write/Agent call (the first substantive action). Method spot-checked by hand on one session. Scratch data in this session's scratchpad (`__probe_metrics.ndjson`, `__probe_class_final.tsv`).

| Opener class | n | Mean turns to first action | Mean tokens to first action | Task file read in first 5 turns |
|---|---|---|---|---|
| a: `/up:make …` (only 16 of 52 carry continuation language; the rest are new-task kickoffs) | 52 | 14 | 84K | 71% |
| b: pasted recap or handoff text, no slash command | 20 | 28 | 111K | 85% |
| c: short pointer "продолжи docs/tasks/<file>.md" | 1 | 3 | 51K | yes |
| d: fresh unrelated request | 85 | not measured | | |
| e: other slash command | 11 | | | |

Median tokens to first action across the 73 resume-type sessions: 76K; p90 129K; max 345K.

Observations:
1. Pasted recaps (b) cost about twice the turns and roughly 30% more tokens than `/up:make` openers before the model acts: the model cross-checks a long narrative against the repo instead of being told which file holds the state.
2. The short-pointer opener (c) almost never occurs (1 of 73), although the owner often writes "продолжи": nearly every such message is a 500-1300 character recap. The one short-pointer session (2026-09-10, after run B) was the cheapest resume measured: 3 turns, 51K tokens, task file read immediately, first action was the fix flagged in the prior session's summary.
3. Reading the task file early does not by itself cap cost: the two most expensive resumes (287K and 345K tokens, 158 and 116 turns, both class b) read the task file early but carried long manual-QA narratives in the paste.
4. Orientation corrections in the first 10 messages are rare (2 of 73); 13 of 73 (18%) have at least one user interrupt in the first 10 messages.
5. All 73 resume-type sessions are in cccc-monorepo.

Design implication (for `up:udesign` to confirm): the cheapest consumed handoff is a pointer to the task file plus a small delta, not a narrative. The prompt should be short, name the task file and the Status, and carry only what the task file does not yet hold.

### Prior art
- `docs/tasks/summary-sonnet.md` — moved drafting to a Sonnet subagent to save main-model output; the measured cost now sits in re-read input, which that design did not anticipate.
- `docs/tasks/session-hygiene.md` — context checkpoint in `make.md` steps 8-10 currently points at `/up:summary`; must be repointed by this task.
- `plugins/up/commands/make.md` step 2 (resume check) and the rule "Don't assume prior session memory — the next agent may be a fresh context reading only the task file".

### Invariants
- IV1 — A task file with a valid Status and no Handoff block resumes in `/up:make` exactly as today; the only step 2 change is reading the latest Handoff block when one exists.
- IV2 — `/up:summary` keeps its name; the checkpoint line in `make.md` and the README entries stay valid after the change, and `agents/summarizer.md` is removed in the same commit that stops referencing it.
- IV3 — `/up:summary` never locates or reads a JSONL transcript and never dispatches a subagent.
- IV4 — `/up:summary` asks the owner at most one question, and only when more than one in-flight task file was edited this session.
- IV5 — The task file template and `/up:make` steps 3-12 are not edited by this task.

### Principles
- PC1 — The task file is the single source of truth; the Handoff block holds only what the file and git do not already say, and the prompt holds only the pointer.
- PC2 — The command has one side effect, the append to the task file; no commit, no new files, no hook.

### Assumptions
- AS1 — The main session can write an adequate Handoff block and prompt from its own context in one turn (evidence: 2026-09-08 and run D).
- AS2 — A fresh session given only `Продолжи docs/tasks/<slug>.md` invokes `/up:make` resume or reads the whole file, so the trailing Handoff block is seen either way.

### Unknowns
- UK1 — Whether the block is complete enough when the session was compacted by the harness before the handoff; only a real post-compaction handoff will show it.

## Plan

Approach: rewrite `commands/summary.md` around one main-session turn that appends a Handoff block and prints a one-line prompt, delete the summarizer agent, and teach `/up:make` step 2 to read the block; three commits, doc-only.

### Handoff block and prompt (the contract between PH1 and PH2)

Block appended at the end of the task file, English:

```markdown
### Handoff — YYYY-MM-DD
- Position: <stage or plan phase>; committed: <last sha, short name>; uncommitted: <files, or "none">
- Decided: <decision>, because <reason>            (0..n lines)
- Dead end: <what was tried>, <why it failed>        (0..n lines)
- Open: <question waiting on the owner>              (0..1 line)
- First action: <one line, a command where possible>
```

Printed prompt, in a fenced block: `Продолжи docs/tasks/<slug>.md`. Below the fence, one sentence for the owner in the owner's language. Without a task file: a `Goal:` line plus the same bullets inline in the fenced block, no file write.

### PH1 — Rewrite `/up:summary`, remove the summarizer

- **1.1** `plugins/up/commands/summary.md:1-85` (rewrite)
  - Frontmatter `description`: one sentence, "append a dated Handoff block to the active task file and print the one-line prompt for the next session".
  - Sections: Process (detect active task file; ground with `git status --short` and `git log -3 --oneline`; append the block; print the prompt and the owner line), No active task file, Rules (only what file and git do not already hold; one question at most, IV4; no subagent, no transcript, IV3; no commit, PC2).
  - Active-file rule: most recently modified `docs/tasks/**/*.md` whose Status enum is not `done`, `shipped`, `reference`; prefer the one edited this session; ask only if still ambiguous (IV4).
  - Respects: IV3, IV4, PC1, PC2, AS1.
- **1.2** `plugins/up/agents/summarizer.md` (delete). Respects: IV2, IV3.
- **1.3** `README.md:102` (modify): `/up:summary` line describes the Handoff block and the one-line prompt. `README.md:117` (modify): drop the `up:summarizer` row. Line 97 stays true. Respects: IV2.
- Commit: `feat(summary): write the handoff from the live session; drop the summarizer agent`

### PH2 — `/up:make` reads the Handoff block on resume

- **2.1** `plugins/up/commands/make.md:25` (modify): the "Exists:" bullet gains one sentence before "Resume from the next stage": if the file ends with one or more `### Handoff — <date>` blocks, read the latest one first; it holds what the previous session left uncommitted or undecided and its first action. No other line in step 2, no template change. Respects: IV1, IV5, AS2.
- Commit: `feat(make): read the latest Handoff block on resume`

### PH3 — Version

- **3.1** `plugins/up/.claude-plugin/plugin.json:3` (modify): `0.3.36` → `0.3.37`.
- Commit: `chore(pack): bump to 0.3.37`

### Test strategy
none (doc-only). Verification is install-and-invoke: install 0.3.37, run `/up:summary` in a real cccc-monorepo session, start a new session with only the printed line, confirm it reads the block and starts with the recorded first action (Goal, UK1).

### Risks
- RK1 — A paused parallel session holds untracked `docs/tasks/upstream-integration.md` and plans its own `make.md` and `plugin.json` edits; every commit here adds files by name, and the `make.md` edit is one sentence on line 25, so a later merge conflicts at most on that line and the version number.
- RK2 — `/up:summary` is model-invocable and the checkpoint line suggests it; the rewritten command still runs only when invoked, and its single side effect is one append, so an unwanted run costs one block, not a subagent.

Backwards compatibility: the summarizer agent is removed in PH1 together with its last references (`summary.md`, README), so no dangling `subagent_type`; old `### Summary —` blocks in cccc task files stay untouched; PH2's sentence is conditional on a Handoff block, so files without one resume exactly as before (IV1).

## Verify
<empty — filled by up:uverify>

## Conclusion
<empty — filled by up:ureview>
