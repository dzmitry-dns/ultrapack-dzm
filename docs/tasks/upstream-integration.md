# Upstream integration: port the generic improvements from btseytlin/ultrapack

**Status:** validating — 2026-09-12, ports and bump on local main (d276a0e, 60df510, 0375134), reviewed; CK5 (reviewer agent loads after push + reinstall) still open
**Branch:** main
**Goal:** The two ported upstream changes (`a2e08e9` quoted reviewer description, `225058a` GPC3 wording) are in `plugins/up/` on `main`, the plugin version is bumped one patch above whatever `main` holds at merge time (0.3.37 on 2026-09-12, other agents bump in parallel), and every other upstream commit since merge-base `e4b96f6` has a skip reason recorded in this file. Confirmed by the diff plus one reinstall showing the reviewer agent still loads with its description intact. The fork's own decisions (model policy, plan-approval gates, ujira, requirements-reviewer, severity grading, context checkpoint) stay intact.

## Design

### Scope change — 2026-09-12
Cut to the two one-line ports after design approval. The `## Context` section had no observed problem behind it (the owner already writes pre-design facts by hand when they matter), so it is skipped, not deferred: revisit only if a reviewer misses a defect because pre-design facts were never written down. The `## Context` material below (per-file shape, IV4-IV6, UK2) records the approved-then-cut design and is not to be executed.

Purpose: bring the fork up to date with the generic content of upstream `btseytlin/ultrapack` (21 commits past merge-base `e4b96f6`) without touching the fork's own decisions. The audit (below) and the owner decisions (below) reduced the port to three items; this design covers how each lands.

Chosen approach for the `## Context` section (owner picked A of three, 2026-09-12): port it as upstream shaped it, adapted by hand to the fork's files. `## Context` is a top-level task-file section placed between the header and `## Design`. It holds 3-6 one-sentence checkable observations about the current state, written before any solution; "we should" phrasing is banned there. `up:udesign` writes it in step 1 (explore) and presents it for approval with the Design sections; `up:uplan`, `up:uexecute` and `up:reviewer` add it to what they read from the task file. The alternatives rejected: B (template line only, no writing rule; agents would fill it with opinions and the section would carry nothing the reviewer can check), C (`### Context` under `## Design`; diverges from upstream in name and place, so every future cherry-pick in these files conflicts).

Per-file shape (line numbers from the subagent map, 2026-09-12):
- `plugins/up/commands/make.md`: template gains `## Context` with its placeholder line above `## Design` (:53); step 5 says udesign populates `## Context` too (:100); the `## Context checkpoint` section (:177) gains one clause saying it is unrelated to the task file's `## Context` section, because the two names collide inside one file.
- `plugins/up/skills/udesign/SKILL.md`: description (:3), intro (:8), a new "## Context" explanatory block above "## The Goal" (:16) adapted from upstream's 22-line block and trimmed, step 9 (:39), output shape (:172), omit-empty rule (:203), terminal state (:207, Context wording only, no hands-off clause). `### Prior art` stays wherever the fork lists it; upstream lacks it.
- `plugins/up/skills/uplan/SKILL.md:44` and `plugins/up/agents/reviewer.md:24`: identical to upstream's old line, add `## Context` to the read list.
- `plugins/up/skills/uexecute/SKILL.md:13`: add "Context" to the read list; keep the fork's Trivial-task tail.
- `README.md:41-46`: the task-file section list gains Context and "four sections" becomes "five".
- `plugins/up/agents/reviewer.md:3`: description wrapped in double quotes, inner double quotes turned single (exact `a2e08e9` form).
- `plugins/up/skills/_principles.md:7`: GPC3 becomes "Separate read-only queries from state-changing commands. Commands may return their result."
- `plugins/up/.claude-plugin/plugin.json`: patch bump, one above the version on `main` at merge time (execute reads it fresh; 0.3.37 on 2026-09-12, and other agents bump in parallel).

Small and Trivial tasks: Design is skipped there, so `## Context` keeps its placeholder exactly as `## Design` already does; no new rule.

Backwards compatibility: no break. Resume (`make.md:19-36`) reads only the `**Status:**` header and ignores unknown fields; nothing in `plugins/up/` or `hooks/` parses section names; a task file without `## Context` gives the stage skills nothing to read and they continue. Trim style (`01a6d83`) is applied only inside the udesign block being added, never as a pass over other text.

TDD: no (reason: doc-only plugin, no runtime code; verification is reinstall and invoke)

### Owner constraints (stated 2026-09-11)
- Ultrapack works today. Improve it; never break the working flow.
- Only Claude Code is in use; skip Codex/Pi packaging and skills.
- This session is research only; design, plan, execute later.

### Owner decisions (2026-09-12)
Data behind them: across all project transcripts `/up:make` was invoked 47 times, every other pack command (`/up:e`, `/up:try`, `/up:summary`) 0 times. Two of the three open task files already carry an ad hoc pre-design facts section ("Research findings"). The owner's rule: add only what gives measurable, tangible benefit.

- PORT `a2e08e9` (quote the reviewer description; the fork's `plugins/up/agents/reviewer.md` line 3 still has the unquoted string with embedded quotes).
- PORT `225058a` GPC3 wording only (commands may return a value); the fork's `_principles.md` line 7 has the strict form.
- ~~PORT `4aea8cf` Context section~~ SKIP (owner, 2026-09-12, after design approval): no observed problem it solves; see "Scope change" under Design.
- SKIP `42075d8` attack-loop and `4f02672..a4e65cd` qplan: standalone commands see zero use in the fork; qplan duplicates `/up:make` Small sizing (Design skipped, Plan kept, same approval pause).
- SKIP the gate cluster as one decision: `b12c8b7`, `225058a` pause removal, `4a43515`, `6d4a81d`. The fork keeps every pause and the venv symlink. UK1 resolved: philosophy change the fork rejects.
- `01a6d83` trim style: opportunistically only, in files this task touches anyway. No separate pass.
- SKIP `9b96f25` timing wording: no measurable benefit.
- Everything else per the audit table: SKIP (layout, Codex/Pi, version bumps).

### Research findings (2026-09-11)

Divergence (measured): merge-base `e4b96f6`; `upstream/main` is 21 commits ahead of it, the fork 87. Upstream moved the plugin from `plugins/up/` to the repo root (`agents/`, `commands/`, `skills/`, `hooks/`, `scripts/`, `.codex-plugin`, `.agents`), so `git cherry-pick` will not apply; changes have to be ported by hand into `plugins/up/`.

Upstream commits since the fork point (newest first):

```
4a43515 Remove dependency approval gate and bump to 0.3.39
225058a Relax approved routine-work guidance
b12c8b7 fix: remove routine setup and workflow approval gates
ad219c9 fix: use native Pi skills as the only workflow interface
6d4a81d fix: preserve Pi arguments and enforce task authority
01a6d83 Trim skill guidance and repair workflow references (#4)
a4e65cd fix: require saved qplan before approval
6953636 fix: require qplan approval before execution
ed4861f chore: bump package version to 0.3.31
b29ba50 Merge remote-tracking branch 'origin/main' into feat/qplan
50b358f refine qplan scope guidance and document Pi invocation
4f02672 feat: add qplan quick planning skill
9b96f25 fix: load shared rules across Pi workflows
fbcc549 feat: add Pi package support
4aea8cf feat: add Context section to task files
007df99 rename codex command skills
70de9fe chore: bump plugin version to 0.3.27
42075d8 feat: add attack loop skill
e681de4 chore: bump plugin version to 0.3.26
a2e08e9 fix: validate Claude reviewer metadata
272822d feat: package ultrapack for Claude and Codex
```

Already observed: `agents/summarizer.md` upstream is byte-identical to the fork's; `commands/summary.md` differs by a few lines; upstream's Codex `skills/summary/SKILL.md` drafts the handoff from the live conversation with no subagent (relevant to `docs/tasks/handoff-prompt.md`).

Candidates flagged for a closer look (from commit titles; audit pending): qplan quick-planning skill, attack loop skill, Context section in task files, "enforce task authority", trimmed skill guidance and repaired references (#4), removal of approval gates (b12c8b7, 4a43515, 225058a) against the fork's own plan-approval gate in `make.md` step 7.

### Audit results (subagent report, 2026-09-11)

Bottom line: most of the 21 commits are Codex/Pi packaging or the root-layout move. Five commits carry portable content. Three commits (`b12c8b7`, `225058a`, `4a43515`) roll back approval gates the fork deliberately keeps, and `6d4a81d` forbids the venv-symlink technique the fork built in `worktree-venv-symlink.md`. Those need the owner's decision, not a port.

| Commit | What | Category | Fork status | Recommendation | Effort |
|---|---|---|---|---|---|
| 272822d | Moves `plugins/up/*` to root, adds `.codex-plugin`, `.agents` | LAYOUT | Fork keeps `plugins/up/` (CLAUDE.md) | SKIP | large |
| a2e08e9 | Quotes `agents/reviewer.md` description (embedded quotes broke the packaging validator) | GENERIC | Fork's `plugins/up/agents/reviewer.md` has the same unquoted string | PORT → `plugins/up/agents/reviewer.md` | small |
| e681de4, 70de9fe, ed4861f, b29ba50 | Version bumps, no-op merge | N/A | Fork versions independently | SKIP | n/a |
| 42075d8 | New `attack-loop` skill (bounded implement/attack/repair) | GENERIC | No equivalent | PORT → new `plugins/up/commands/attack-loop.md` | medium |
| 007df99 | Renames Codex skill dirs | CODEX/PI | N/A | SKIP | n/a |
| 4aea8cf | `## Context` section in task files (checkable observations before Design) | GENERIC | Template has no Context section | PORT → `make.md`, `udesign`, `uexecute`, `uplan`, `agents/reviewer.md` | medium |
| fbcc549 | Pi `package.json` | CODEX/PI | N/A | SKIP | n/a |
| 9b96f25 | Pi shared-rules wiring; also moves the brevity/principles read trigger from "before writing" to "before responding or writing" | CODEX/PI + 1 generic line | Fork's `uexecute` says "before writing"; `make.md` has no required-read block | SKIP bulk; DISCUSS the timing wording | small |
| 4f02672, 50b358f, 6953636, a4e65cd | `qplan` skill: design+plan in one pass, mandatory approval, plan must be saved to disk before approval | GENERIC + POLICY | No equivalent tier between ad hoc chat and full `make` | PORT → new `plugins/up/commands/qplan.md`, reuse the fork's plan-gate wording | medium |
| 01a6d83 | Halves every process skill's prose, converts skill mentions to markdown links, keeps approval steps | GENERIC | Same files the fork customized heavily | DISCUSS: take the link convention and trim style opportunistically, never a blind merge | large |
| 6d4a81d | Pi `$ARGUMENTS` fix + "task authority": never infer permission; job-guardian recovery disabled unless pre-approved; forbids `.venv`/`node_modules` symlinks in worktrees | CODEX/PI + POLICY | Conflicts with fork's job-guardian "away by default, never ask" and with `worktree-venv-symlink.md` | SKIP Pi part; DISCUSS authority language | medium |
| ad219c9 | Removes Pi prompt wrappers | CODEX/PI | N/A | SKIP | n/a |
| b12c8b7 | Removes per-section design approval, worktree confirmation, summary destination ask | POLICY | Fork keeps all three (`make.md` worktree confirm, `udesign` per-section approval) | DISCUSS | n/a |
| 225058a | Removes ureview "user can interject" pause; lets uexecute pass design rationale to implementers; loosens GPC3 (commands may return a value) | POLICY + 1 generic | Fork keeps the pause; fork's GPC3 is the strict form | SKIP pause removal; PORT GPC3 wording | small |
| 4a43515 | Drops "required dependency missing" as a stop-and-ask trigger in uexecute | POLICY | Fork's uexecute still lists it | SKIP | n/a |

Details on the items worth porting:

- qplan (4f02672 → a4e65cd): one skill for work too big for a prompt and too small for the full pipeline. Reads code, asks only blocking questions, writes one compact task file (Context, Desired design, Invariants, phased plan, Verification), stops for explicit plan approval, then executes phases in the same session with no subagent dispatch. `6953636` made approval mandatory; `a4e65cd` requires the plan to be on disk before approval can be requested. Port needs a name that fits the fork's `u`-prefix convention and the approval line written to match `make.md` lines 115-117 so there is one approval mechanism.
- attack-loop (42075d8): bounded implement/attack/repair loop with no task file and no ureview. User supplies target, max rounds, observable stop condition. Each round dispatches one fresh attacker with no prior rationale (matches uverify's categories); findings classified Fix/Record/Defer before any change; stops only on evidence. Lighter complement to uverify; no wording conflicts.
- Context section (4aea8cf): 3-6 one-sentence checkable observations about the current state, written before any solution, "we should" phrasing banned. udesign writes it, uexecute/uplan read it, reviewer reads it with Invariants/Principles. Additive; does not touch the IV/PC/AS/UK scheme.
- Task authority (6d4a81d): replaces job-guardian's "pick the safest reversible choice and log it" with "recovery disabled unless the exact command was pre-approved", and forbids the venv symlink. Direct, deliberate conflicts with two fork decisions.
- Trim (01a6d83): udesign 238→124 lines, uexecute 349→158, uplan 201→124, ureview 206→112, uverify 223→115, udocument 112→63. Grep confirms approval mentions preserved (5 removed, 7 added). Only the discipline and link convention are portable.
- Gate removals (b12c8b7, 225058a, 4a43515): what went away upstream is per-section design approval, worktree confirmation, summary confirm-before-write, ureview interject pause, missing-dependency stop. The fork relies on the opposite in `make.md` (worktree confirm, plan gate), `udesign` line 36, `ureview` line 118, `uexecute` stop list, and in `t2-template-realignment.md` (removed hands-off mode rather than loosen gates). Tradeoff: fewer low-stakes prompts vs the owner's global "propose a plan and wait" policy.
- Summary wording: upstream's Codex `skills/summary/SKILL.md` phrase "use the requested destination, otherwise append to the active task file; ask only when the destination is ambiguous" is cleaner than the fork's ask-every-time step 5. Feeds `docs/tasks/handoff-prompt.md`.

Facts: upstream manifest version 0.3.39; upstream `.claude-plugin/marketplace.json` has `"source": "."` resolving root-level dirs; upstream `hooks/` holds only `.gitkeep`.

Suggested port order:
1. `a2e08e9` quote fix in `plugins/up/agents/reviewer.md` (small, zero risk).
2. GPC3 wording from `225058a` in `plugins/up/skills/_principles.md` (small).
3. attack-loop, new `plugins/up/commands/attack-loop.md` (medium, additive).
4. Context section across `make.md`, `udesign`, `uplan`, `uexecute`, `reviewer.md` (medium, additive).
5. qplan, new command written to the fork's plan-gate wording (medium).
6. Gate-removal cluster (`b12c8b7`, `225058a` pause, `4a43515`, `6d4a81d` authority) as one owner decision, item by item.
7. `01a6d83` trim style opportunistically when a skill file is touched for another reason.

### Prior art
- `CLAUDE.md` "Fork policy": generic fixes go upstream as PRs, opinionated features stay in the fork, cherry-pick upstream periodically.
- `docs/tasks/t2-template-realignment.md:15` — how `### Prior art` was added to the template last time: one template line in `make.md` plus one udesign step; the same shape for `## Context`.
- `docs/tasks/t2-template-realignment.md:22` — backwards compat precedent: legacy task files need no migration because resume ignores unknown headers.
- `docs/tasks/t2-template-realignment.md:30` — IV4 there: the template section set is defined only in `make.md`'s template; stage skills reference sections by name. Carried here as IV4.
- `docs/tasks/audit-fixes.md:38` — earlier realignment of a stage skill's template block with upstream.

### Invariants
- IV1 — The fork keeps the `plugins/up/` layout and its marketplace manifest; no move to upstream's root layout.
- IV2 — Fork-specific behavior listed in the Goal is unchanged; the gate cluster (`b12c8b7`, `225058a` pause, `4a43515`, `6d4a81d`) stays skipped.
- IV3 — Each upstream commit since `e4b96f6` ends up in exactly one of: ported (with target file) or skipped (with reason), recorded in this file.
- IV4 — `## Context` is defined once, in `make.md`'s template; every other file references it by name only.
- IV5 — A task file with no `## Context` section resumes and runs every stage exactly as before; no file gains a parser for section names.
- IV6 — The `## Context` section holds observations only; the udesign rule bans "we should" phrasing there.

### Principles
- PC1 — Port content, not packaging.
- PC2 — One commit per ported upstream change, referencing the upstream hash, so the mapping is auditable.
- PC3 — Trim style from `01a6d83` applies only to text this task adds or edits, never as a pass over neighbouring text.

### Assumptions
- AS1 — Upstream's markdown changes are separable from its Codex/Pi packaging. Held: the audit found every portable change is a plain markdown hunk.
- AS2 — Reinstalling the pack from the marketplace picks up the bumped version so the reinstalled `/up:make` shows the new template.

### Unknowns
- UK1 — Whether upstream's removal of approval gates is a philosophy change the fork rejects, or a cleanup the fork can adopt in part. Resolved 2026-09-12: rejected as a whole, owner decision, see "Owner decisions".
- UK2 — The exact trimmed wording of the udesign `## Context` block; settled in the plan against upstream's 22-line original.

## Verify
Stance: two one-line doc changes; the attack surface is "the YAML no longer parses" and "the port is not what upstream shipped".

- CK1 — `claude plugin validate plugins/up`: passed (manifest at 0.3.38).
- CK2 — `claude plugin validate .` (marketplace): passed with two pre-existing warnings, see Code smells.
- CK3 — reviewer description line byte-identical to `upstream/main:agents/reviewer.md` line 3: `diff` empty.
- CK4 — GPC3 line byte-identical to `upstream/main:skills/_principles.md`: `diff` empty.
- CK5 — reviewer agent loads with the quoted description: pending. `claude plugin details` reads only installed plugins, and the installed copy is 0.3.36; run `claude plugin update up@ultrapack` after the push, then `claude plugin details up@ultrapack` must list the reviewer agent with its description. No local YAML parser is available (no yq; inline interpreters are denied by the shell hook).

## Code smells
- `.claude-plugin/marketplace.json`: `metadata.repository` is an unknown field Claude Code ignores, and the marketplace has no `description`. Reported by `claude plugin validate .`; out of scope here.

## Conclusion

Outcome: both ports and the bump are on local `main` (d276a0e, 60df510, 0375134); the Goal closes once the push lands and CK5 (reviewer agent loads from the reinstalled 0.3.38) passes.

Invariants:
- IV1 — diff touches only `plugins/up/`; layout and manifest unchanged.
- IV2 — gate cluster untouched; grep shows no fork pause or confirmation removed.
- IV3 — every commit since `e4b96f6` has a row in the audit table or a line under Owner decisions.
- IV4-IV6 — not exercised; `## Context` was cut (see Scope change).

### Assumptions check
- AS1 — held: both ported hunks are plain markdown lines, byte-identical to `upstream/main`.
- AS2 — unverifiable until the push and `claude plugin update up@ultrapack`; CK5 records the check.

### Unknowns outcome
- UK1 — resolved: gate removals rejected as a whole, owner decision 2026-09-12.
- UK2 — moot: the udesign `## Context` block is not written.

Review findings:
- Important: the three commits carried a `Co-Authored-By` trailer the owner's global rules forbid. Resolved by recreating the commits without it (reviewer suggested the fix; nothing had been pushed).

Verified by: CK5 is a manual step after push: `claude plugin update up@ultrapack`, then `claude plugin details up@ultrapack` must list the reviewer agent with its description.

## Next session
Run `/up:make upstream-integration`; it resumes from the Status enum. The port list is fixed in "Owner decisions"; do not reopen skipped items. Read the plugin version on `main` fresh before bumping: other agents bump in parallel.
