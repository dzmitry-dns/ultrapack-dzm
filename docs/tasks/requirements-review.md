# Requirements-review fold-in

**Status:** planning
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
<empty — filled by up:uverify>

## Conclusion
<empty — filled by up:ureview>
