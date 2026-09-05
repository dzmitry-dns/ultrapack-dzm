# Audit fixes 2026-09: broken refs, rule alignment, disable unused skills

**Status:** validating — code reviewed 2026-09-05; Goal needs the 0.3.33 install and one live cccc smoke
**Branch:** main
**Goal:** v0.3.33 installs from the fork and `/up:make` on one small cccc task runs with no broken reference, ujira proposes no ticket transition, uverify sets `verifying`, and the eight zero-use skills no longer load into model context.

## Design

Source: `docs/audit-2026-09-05.md` (two months of transcripts, full pack read, Claude Code and Anthropic guidance through 2026-09-05). Owner decisions 2026-09-05: em dashes stay in agent-facing files; zero-use skills are disabled with `disable-model-invocation: true`, not deleted; the tests rule keeps `### Test strategy` in every plan as the cap on test count, with `none` as a valid value.

### Prior art
- `docs/roadmap.md:91-104` T3/T4/T5 open items; T0/T1 checkboxes never ticked though shipped.
- `docs/tasks/skill-output-brevity.md` introduced `_brevity.md` with six principles; four callers still say five.

### Invariants
- IV1 — No skill, agent, or command references a tool, file, or skill that does not exist.
- IV2 — Absent consumer config, ujira never proposes a ticket transition.
- IV3 — Disabled skills keep their files and frontmatter valid; `claude plugin validate` passes.
- IV4 — Model pins unchanged (reviewer/requirements-reviewer opus, explorer haiku, researcher/summarizer sonnet, implementer inherits).

### Assumptions
- AS1 — `disable-model-invocation: true` is honored on plugin skills and on `commands/*.md`.
- AS2 — `TodoWrite` is absent from the current tool list; a checklist in the task file replaces it.

### Unknowns
- UK1 — Whether `effort:` in agent frontmatter is accepted by the installed Claude Code build.

## Plan

Approach: one patch release, edits grouped by file, no behaviour change beyond the audit's A/B/C lists.

### PH1 — Broken references and internal drift
- `commands/summary.md` Task tool to Agent; scan `docs/tasks/**/*.md`; `shipped`/`reference` inactive.
- `skills/uexecute/waves.md` drop `run_in_background`.
- `skills/uexecute/SKILL.md` TodoWrite to task-file checklist; six to six principles; `### Known risks` name.
- `skills/udesign/SKILL.md`, `skills/uplan/SKILL.md`, `skills/uexecute/SKILL.md` prefix `_brevity.md` / `_principles.md` with `${CLAUDE_PLUGIN_ROOT}/skills/`.
- `skills/uplan`, `skills/uverify`, `skills/ureview` "five principles" to "six".
- `skills/ureview/SKILL.md` Conclusion template: `### Deviations from plan`, `### Known risks`; stale good-example replaced.
- `skills/uverify/SKILL.md` `Future Work` to `Future work`; sets Status `verifying`.
- `commands/make.md` Status enum gains `verifying`; resume from it runs uverify.
- Five skills: `<system-reminder>` blocks to `<red-flags>`.
- `agents/explorer.md` smell heading to `## Code smells`.
- Commit: `fix(pack): dead tool refs, six principles, verifying status, red-flags tag`

### PH2 — Align with owner rules
- `skills/uplan/SKILL.md` Test strategy wording: tests the change needs, `none` valid, list is the cap; bug fix = one red reproduction.
- `skills/uexecute/SKILL.md` mutation check for new coverage; three test-only edits stop and ask; commit rules (English, no `Co-authored-by`); scope line.
- `agents/implementer.md` scope line; no `Co-authored-by`.
- `skills/ujira/SKILL.md` transitions only under `transitions: propose`.
- `commands/make.md` plan-approval gate: Medium/Large always; Small when 3+ files, DB migration, or new API surface.
- `skills/ureview/SKILL.md` relation to built-in `/code-review`.
- `agents/reviewer.md`, `agents/requirements-reviewer.md` two-pass (find all, then filter); `effort: high`. `agents/explorer.md` `effort: low`.
- Commit: `feat(pack): tests cap, no ujira transitions by default, plan gate, two-pass review`

### PH3 — Disable zero-use skills, bookkeeping, version
- `disable-model-invocation: true` on commands e, try, reflect, step-back and skills test-driven-development, git-worktrees, job-guardian, udocument.
- `plugin.json` author, repository, version 0.3.33.
- `docs/roadmap.md` tick T0/T1; three task files lose "pending"; `ujira-auto-comments.md` Status `validating`.
- `.claude/settings.local.json` drop `Bash(...)` entries.
- README status chain adds `verifying`, `reference`.
- Commit: `chore(pack): disable eight zero-use skills, bump 0.3.33`

### Test strategy
none (doc-only pack; verify is `claude plugin validate --strict` plus grep for dangling refs)

### Risks
- RK1 — A disabled skill the owner wanted auto-triggered (udocument on `.md` edits) stops firing; mitigated by the owner's explicit decision.

## Verify

**Result:** passed

Happy-path:
- CK1 — `claude plugin validate plugins/up --strict` — held (Validation passed, 2026-09-05)
- CK2 — every `up:<name>` mention resolves to a skill, command, or agent file — held (0 missing)
- CK3 — every `${CLAUDE_PLUGIN_ROOT}/...` path exists — held (0 missing)

Negative:
- CK4 — leftovers of `system-reminder`, `TodoWrite`, `Task tool`, `five principles`, `run_in_background` in the pack — held (0 hits)
- CK5 — any file outside ujira still says transitions are always proposed — held (0 hits)

Invariant:
- CK6 — IV4 model pins unchanged — held (reviewer/requirements-reviewer opus, explorer haiku, researcher/summarizer sonnet, implementer none)
- CK7 — Status `verifying` set by both entry paths (make step 9, uverify on entry) — held after the uverify edit

Smoke: deferred — a live `/up:make` run on a small cccc task needs the 0.3.33 install first (see Conclusion).

## Conclusion

Outcome: pack side done and reviewed; Goal pending the 0.3.33 install and one live `/up:make` smoke in cccc. Commits bdab382, 67c3ccb, 1ac57c6, 29fb830, 2288cbc plus the review-fix commit.

Invariants:
- IV1 — grep: every `up:<name>` resolves to a file; every `${CLAUDE_PLUGIN_ROOT}` path exists; disabled skills are reached by file read, never by Skill invocation
- IV2 — ujira drafts a transition only under `transitions: propose` (description, config, triggers, draft example, rules, README all say so)
- IV3 — `claude plugin validate plugins/up --strict` passed after the last edit
- IV4 — model pins unchanged

### Assumptions check
- AS1 — held — `skills.md` docs line 172: command files support the same frontmatter except `name` and `paths`
- AS2 — held — `TodoWrite` absent from the session tool list; replaced by a session checklist

### Unknowns outcome
- UK1 — resolved — `effort:` is a documented subagent field (low/medium/high/xhigh/max), Claude Code 2.1.261

### Deviations from plan
- `plan-approval: always` consumer key added in PH2, then removed after review — the gate now has one home (make step 7) and no config surface
- plugin.json keywords and description edited beyond author/repository/version — fork identity, no behaviour
- Disabled skills that the pack itself calls (test-driven-development, git-worktrees) are reached by reading the file, not by invoking the skill; the callers were reworded (udesign, uexecute, implementer, make)

Review findings:
- Critical: TDD and git-worktrees invocation paths severed by `disable-model-invocation` — resolved, callers read the file
- Critical: plan-approval gate depended on a size never stored — resolved, uplan waits unless make said Small-under-threshold in the same invocation
- Important: README and two descriptions still promised auto-triggers and always-proposed transitions — resolved
- Important: Test strategy not passed to wave implementers — resolved, added to the dispatch prompt and implementer input
- Important: ujira start draft had no pause to ride for Small tasks — resolved, gated items move to the terminal draft
- Not accepted: `/up:ujira` "has no command file" — plugin skills create their slash command (skills docs lines 16 and 130)

Scope flag:
- Reviewer: "zero-use" counted the owner's explicit calls, not the pack's own control flow; TDD and git-worktrees are invoked by udesign/uexecute/make. Addressed by the read-the-file rewiring; the owner's decision to disable stands.

Future work:
- `context: fork` on uverify and ureview — Justification: audit D3, out of this patch's scope
- `hooks/hooks.json` SessionStart task index; udebug as the bug entry of make; CI validate — Justification: audit D5-D7, roadmap T3/T5
- Trim SKILL.md files over 150 lines into reference files — Justification: audit C1

Verified by: `claude plugin validate --strict`, reference greps, one opus reviewer pass; live smoke deferred to the install.
