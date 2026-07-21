# Project verify recipe

**Status:** planning — parked 2026-07-21; plan ready; draft commits a77ae40 (PH1) + 11f7609 (PH2, bump 0.3.30) on this branch await review
**Branch:** verify-recipe
**Depends on:** docs/roadmap.md:90
**Goal:** `up:uverify` reads a consumer-declared `## Verify recipe` CLAUDE.md section (bare `- <command>` lines, same parse convention as `## Jira adapter`) and runs it as the smoke baseline instead of guessing; projects without the section keep byte-identical heuristic behavior; grep-proof: parse convention consistent with ujira's config wording.

## Design

Skipped — Small, pre-decided by `docs/roadmap.md:90` (uverify reads a per-project smoke recipe instead of guessing; cccc example at roadmap:26) plus the config-section pattern shipped with ujira (consumer CLAUDE.md section, bare-lines parse target, silent fallback when absent).

### Invariants

- IV1: No section → byte-identical current behavior (heuristic smoke inference); the recipe is opt-in per project.
- IV2: Parse convention matches the ujira precedent — bare `- ` lines are the sole parse target, surrounding prose allowed and non-breaking.
- IV3: Adversarial stance unchanged — the recipe feeds Phase 3 (smoke baseline); it never replaces the attack list, and a gated/unrunnable step surfaces as `deferred` with a reason, never silently skipped.

### Assumptions

- AS1: A flat ordered command list + one `smoke:` line + prose gates is expressive enough for real stacks (cccc's recipe at roadmap:26 fits).

## Plan

Approach: one insertion in uverify Phase 3 — recipe-first, heuristics as fallback — plus bump.

### PH1 — uverify reads the recipe

- **1.1** `plugins/up/skills/uverify/SKILL.md:78-88` (modify) — Phase 3:
  - Before "Run the shortest full path": recipe paragraph — check consumer project `CLAUDE.md` for a `## Verify recipe` section; bare `- <command>` lines are the sole parse target (prose around them is welcome — same convention as `## Jira adapter`); run the commands in order, freshly, as the smoke baseline; a `smoke: <description>` line names the end-to-end smoke; a prose-gated step that can't run (missing DB, no device) → `deferred` with the reason (IV3). No section → heuristics below (IV1).
  - Reword the heuristic list intro as the explicit fallback.
- Commit: `docs(uverify): read the project verify recipe before guessing the smoke`

### PH2 — bump

- **2.1** `plugins/up/.claude-plugin/plugin.json` — 0.3.29 → 0.3.30.
- Commit: `chore: bump up to 0.3.30`

### Test strategy

Grep-proof: uverify's parse wording consistent with ujira's ("bare", "parse target", prose-allowed); fallback path explicit (IV1); `deferred` vocabulary reused from the existing CK verdicts (IV3); no other pack file needs the recipe (make.md delegates verify wholesale).

## Verify
<empty — filled by up:uverify>

## Conclusion
<empty — filled by up:ureview>
