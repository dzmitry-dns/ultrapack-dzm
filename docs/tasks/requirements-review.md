# Requirements-review fold-in

**Status:** shipped — merged 2026-07-21; push + reinstall to 0.3.29 pending
**Branch:** requirements-review
**Depends on:** docs/roadmap.md:89
**Goal:** The pack ships `up:requirements-reviewer` (agent) and `up:ureview` offers it as an optional second dispatch — verbatim original requirement + BASE_SHA/HEAD_SHA only, auto-suggested for Medium+ tasks; README lists the agent; grep-proof: no pack file still points at `~/.claude/agents/requirements-reviewer.md`.

## Design

Skipped — design pre-decided by `docs/roadmap.md:89`: optional second dispatch in `ureview`, agent sees only the verbatim requirement + SHAs, auto-suggested for Medium+, agent file folded from `~/.claude/agents/requirements-reviewer.md`.

### Invariants

- IV1: Agent blindness intact — the pack agent never receives or reads the task file, plan, design, or session rationale; only verbatim requirement + SHAs + working dir.
- IV2: Opt-in stays opt-in — ureview *suggests* the dispatch for Medium+; it never auto-runs without the user's yes. Complements, never replaces, `up:reviewer`.
- IV3: Agent contract (stance, five failure modes, two-tier output, confidence ≥80) ports unchanged; only the entry-path wording adapts (manual → ureview-suggested).

### Assumptions

- AS1: Plugin agent namespacing (`up:` prefix) avoids collision with the user-level `~/.claude/agents/requirements-reviewer.md` copy while both exist.

### Unknowns

- UK1: Where the dispatcher sources the verbatim requirement when the review runs in a later session than the ask. Resolve at plan.

## Plan

Approach: copy the agent into the pack with entry-path wording adapted, add one dispatch subsection to ureview, one README row, bump.

### PH1 — agent file

- **1.1** `plugins/up/agents/requirements-reviewer.md` (create) — body ported verbatim from the user-level agent (IV3); frontmatter description reworded: dispatched as optional second reviewer from `up:ureview` (auto-suggested Medium+) instead of "dispatched manually". Keep `model: opus`, tools `Glob, Grep, Read, Bash`.
- Commit: `feat(agents): fold requirements-reviewer into the pack`

### PH2 — ureview wiring + README

- **2.1** `plugins/up/skills/ureview/SKILL.md` (modify) — after the `up:reviewer` dispatch step: optional second dispatch subsection — when to suggest (Medium+ / high-stakes), what to pass (verbatim requirement + SHAs + cwd, nothing else — IV1), findings join the same fair-evaluation loop. UK1: requirement comes from the session's original ask; when reviewing in a fresh session, ask the user to paste it — never reconstruct it from the task file.
- **2.2** `README.md:112` area (modify) — agent table row for `up:requirements-reviewer`.
- Commit: `docs(ureview): optional requirements-review second dispatch`

### PH3 — bump

- **3.1** `plugins/up/.claude-plugin/plugin.json` — 0.3.28 → 0.3.29.
- Commit: `chore: bump up to 0.3.29`

### Test strategy

Grep-proof: no pack reference to the user-level agent path; ureview names the agent exactly as the file's frontmatter `name`; README row present; agent file carries no task-file/plan references (IV1).

## Verify

**Result:** passed

- CK1 — grep pack + README for the user-level agent path — held: only `docs/roadmap.md:89` (the roadmap item itself) references it
- CK2 — agent name consistency — held: frontmatter `requirements-reviewer`, referenced as `up:requirements-reviewer` in ureview + README (same pattern as other agents)
- CK3 (IV1) — hunt a leak path for task-file/plan into the dispatch — held: dispatch list is requirement + SHAs + cwd only; agent body forbids reading `docs/tasks/**`
- CK4 (IV2) — hunt auto-run language — held: "the user opts in — never auto-run it" (ureview:75)
- CK5 — manifest — held: valid JSON, 0.3.29
- CK6 (IV3) — diff pack agent body vs user-level source — held: identical below frontmatter; only description reworded (entry path)

Smoke: agent frontmatter well-formed (name/tools/model), ureview section renders between steps 1 and 2 — doc-only change loads as plugin files.

## Conclusion

Outcome: Goal achieved — pack ships `up:requirements-reviewer`, ureview offers it as opt-in second dispatch, README row in, grep-proof clean. Commits 3565579 (agent), 8ebc3b1 (wiring), 8187573 (bump 0.3.29).

Invariants:
- IV1 — dispatch list is requirement + SHAs + cwd only; agent body forbids `docs/tasks/**` (CK3)
- IV2 — "the user opts in — never auto-run it" in ureview 1b (CK4)
- IV3 — body byte-identical below frontmatter, only description reworded (CK6)

### Assumptions check
- AS1 — held — `up:` namespacing keeps pack and user-level copies distinct while both exist

### Unknowns outcome
- UK1 — resolved — verbatim requirement comes from the session's ask; fresh session asks the user to paste it, never reconstructs from the task file

Scope flag:
- Fold-in leaves a byte-identical duplicate at `~/.claude/agents/requirements-reviewer.md`, and the user's global CLAUDE.md still instructs "Invoke only when the user explicitly asks for it" — conflicting with ureview's suggest-for-Medium+ path. Both files are outside this repo; the two copies will drift.

### Deferred
- Retire `~/.claude/agents/requirements-reviewer.md` and reconcile the global CLAUDE.md Ultrapack note → owner, after 0.3.29 installs.

### Follow-up — 2026-07-22
- Deferred owner-cleanup done: user-level `requirements-reviewer.md` deleted, global CLAUDE.md Ultrapack note now points at `up:requirements-reviewer` via `up:ureview` step 1b.
