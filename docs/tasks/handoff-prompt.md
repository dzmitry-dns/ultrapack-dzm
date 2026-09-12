# Handoff prompt: replace the summarizer round-trip with a prompt written from the live context

**Status:** design — 2026-09-11, research complete (handoff usage sweep, session-opener sweep, upstream summary check); design not started; see "Research findings" and "Next session" below
**Branch:** main
**Goal:** Ending a session inside `/up:make` (or ad hoc) costs one short main-session turn and yields a copy-pasteable prompt that the next session consumes as reliably as today's `/up:summary` draft; the summarizer subagent, the JSONL phrase search, and the "where to save" question are no longer on the path. Confirming it needs at least one real handoff on cccc-monorepo, not just the diff.

## Design
<empty — filled by up:udesign next session; the owner's constraints and the evidence are below>

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

### Candidate shapes to evaluate in design (not decided)
- S1: `/up:summary` rewritten to draft in the main session, no subagent; prints a fenced prompt block; optional one-line Status annotation write to the task file. Summarizer agent deleted or kept only for the "no task file, long ad hoc session" case.
- S2: new command (name to be chosen with the owner) that prints only the prompt: `/up:make <slug>` line plus the delta not yet in the task file (decisions with reasons, in-flight state, dead ends, first action, do-not list). Task file stays the single source of truth; the prompt is a pointer plus delta.
- S3: same as S2 but the context checkpoint in `make.md` offers it directly instead of suggesting `/up:summary`.
- Native alternative to compare against, not replace: `/compact` with instructions, `claude --resume`.

### Prior art
- `docs/tasks/summary-sonnet.md` — moved drafting to a Sonnet subagent to save main-model output; the measured cost now sits in re-read input, which that design did not anticipate.
- `docs/tasks/session-hygiene.md` — context checkpoint in `make.md` steps 8-10 currently points at `/up:summary`; must be repointed by this task.
- `plugins/up/commands/make.md` step 2 (resume check) and the rule "Don't assume prior session memory — the next agent may be a fresh context reading only the task file".

### Invariants
- IV1 — `/up:make` resume (step 2) keeps working unchanged: a task file with a valid Status resumes at the same stage as today.
- IV2 — No existing command or skill stops working mid-migration; if `/up:summary` is renamed or removed, the checkpoint line and any docs pointing at it change in the same commit.
- IV3 — The handoff never depends on locating a JSONL transcript.

### Principles
- PC1 — The task file remains the single source of truth; the prompt carries only what is not in it yet.
- PC2 — Minimal: one command, no new subagent, no hook.

### Assumptions
- AS1 — The main session can write an adequate prompt from its own context in one turn (evidence: 2026-09-08 and run D).

### Unknowns
- UK1 — Whether the prompt alone is enough when the session was compacted before the handoff (context already summarized by the harness).
- UK2 — Whether to write the delta into the task file as well, so a lost clipboard is recoverable, or keep the prompt chat-only.

## Plan
<empty — filled by up:uplan>

## Verify
<empty — filled by up:uverify>

## Conclusion
<empty — filled by up:ureview>

## Next session
Run `/up:make handoff-prompt`; it resumes at `design`. Start `up:udesign` from the "Candidate shapes" list and the findings above. Related task: `docs/tasks/upstream-integration.md` (independent, can run first or second).
