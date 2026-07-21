# T2 — Template & flow realignment

**Status:** executing
**Branch:** t2-template-realignment
**Goal:** The pack's template and flow match observed usage (157-file census): template carries Prior art / Rollback / Rollout / Jira / Depends-on slots and the `<enum> — <annotation>` status format with `shipped` + `reference`; Conclusion gets dated post-merge log + Deferred-as-scope-parking; verify has a CK-lite tier; epic folder convention blessed; hands-off mode and implementer-sonnet fully removed; wave machinery lives only in `skills/uexecute/waves.md`; grep proves zero dangling references. Confirmed by reinstalling the updated pack and a `/up:make` pass showing the new template and no hands-off/worktree prompts.

## Design

Realign the pack with how 157 real task files are written (census in `docs/roadmap.md`), execute resolved Open questions 1–3 (hands-off cut, worktree prompt cut, interface graph demoted), and fold in SSOT dedup. Owner decisions this session: status model = `done + shipped + reference` with blessed `<enum> — <annotation>`; `implementer-sonnet` cut in favor of dispatch-time `model: sonnet`.

Blocks:

1. **Hands-off removal.** Delete `skills/handsoff/` (102 lines). Strip from `commands/make.md`: token activation (l.13), Mode field (36–37, 48), hands-off branches in steps 4/6/7/12 (94, 104–110, 117, 146), rule l.190, section 196–198. Strip stage-skill deltas: udesign 195 + 202–208, uplan 54 + 195–201, uexecute 22–26 (hands-off parts) + 326–328, uverify 217–219, ureview 106–107 + 196–198. Template loses `**Mode:**`, `### Hands-off decisions`, `### Deferred (needs user input)`. `job-guardian` (l.17, 51, 54, 119) gets a self-contained decision-log contract: decisions and open questions recorded in its own watch-record lists, no hands-off references.
2. **Deferred repurposed as scope-parking.** New meaning: Conclusion subsection `### Deferred`, entries `- <what> → <ticket | task file>` (census: ~20 freeform uses). The user-input-gate meaning dies with hands-off. uverify's per-CK `deferred` verdict is unrelated and stays.
3. **Template additions** (all census-backed): optional headers `**Jira:**` (49+10 files) and `**Depends on:**` (28); `### Prior art` under Design (107 files) with a udesign step — consult `docs/tasks/` + `archive/` if present, cite file:line or "none found"; `### Rollback` (91) and `### Rollout` (73) slots in Plan, omitted when N/A; Conclusion dated post-merge log — `### Follow-up — <date>`, `### Scope change — <date>`. `**Worktree:**` field cut; make step 6 becomes a branch-only decision with a one-line pointer to `up:git-worktrees`.
4. **Status model.** Enum: `design | planning | executing | reviewing | validating | done | shipped`, plus `reference` for epic overviews. `<enum> — <annotation>` blessed; reopen = revert to an earlier enum value with a dated annotation. Resume-check: `shipped` treated as done, `reference` skipped, unknown → ask. Enum defined only in `make.md` (IV3).
5. **Verify tiering.** CK-lite for small changes: ≥3 attacks (happy-path + negative + invariant/interface) + smoke, one-screen summary. Full protocol otherwise. uverify infers the tier from artifacts (plan ≤2 phases and small diff → lite); no new `**Size:**` header.
6. **Epic convention.** `docs/tasks/<epic>/` with `overview.md` (`Status: reference`, links to children); children are normal task files. Resume-check scans `docs/tasks/**/*.md`.
7. **Interface graph → reference file.** New `skills/uexecute/waves.md` is the single home: declaration format (from uplan 113–138) + wave derivation/dispatch/wiring (from uexecute 40–76, 133–188). uexecute mainline = serial per-phase loop + one line "plan declares `### Interface graph` → read waves.md"; uplan keeps a 2–3 line pointer. Expected shrink: uexecute 345 → ~220, uplan 201 → ~170.
8. **SSOT dedup.** Delete `agents/implementer-sonnet.md` (~100/118 lines duplicate implementer.md); uexecute dispatches `up:implementer` with dispatch-time `model: sonnet` for trivial phases, the sonnet scope-check paragraph moves into the dispatch prompt. ureview compresses its restated reviewer stance (four audit angles, 12–16) to one line pointing at `agents/reviewer.md`.

Backwards compat: legacy task files with `**Mode:**`/`**Worktree:**`/hands-off sections need no migration — resume ignores unknown headers. `handsoff` token becomes plain description text (zero adoption). T2 is opinionated fork work, not upstreamed; upstream cherry-picks will conflict more in these files — accepted. cccc's `workflow.md` realignment is a follow-up in that repo, out of scope here.

TDD: no (doc-only pack; verification is grep sweeps + install smoke).

### Invariants
- IV1 — `grep -ri 'handsoff\|hands-off' plugins/up/` returns zero hits after the change.
- IV2 — Wave/interface machinery is stated only in `skills/uexecute/waves.md`; uexecute/uplan mainlines point to it without restating derivation rules.
- IV3 — The status enum and resume behavior are defined only in `commands/make.md`; no other pack file lists the enum.
- IV4 — The template section set is defined only in `make.md`'s template; stage skills reference sections by name.
- IV5 — Zero references anywhere in `plugins/up/` to deleted artifacts: `implementer-sonnet`, `handsoff` skill, `**Mode:**`, `**Worktree:**`, `### Hands-off decisions`, `### Deferred (needs user input)`.
- IV6 — Core untouched in meaning: ID system (IV/PC/AS/UK/PH/RK/CK), independent no-rationale reviewer, adversarial verify stance, `_brevity`/`_principles`.

### Principles
- PC1 — Census over aspiration: every template addition names its census signal; nothing lands without observed usage.
- PC2 — Omit-if-empty (per `_brevity` p.1): Jira / Depends-on / Rollback / Rollout / Prior art("none found" allowed) / Deferred appear only when they carry content.
- PC3 — Static model policy lives in agent frontmatter; contextual choice is a dispatch-time param (continues T1's line).

### Assumptions
- AS1 — Resume-check tolerates legacy headers in old task files by ignoring what it doesn't recognize; no migration needed (6 files here, 157 in cccc).
- AS2 — Reference files inside a skill dir (`skills/uexecute/waves.md`) are readable at runtime via `${CLAUDE_PLUGIN_ROOT}` paths — same mechanism T1's smoke proved for `skills/_brevity.md`.
- AS3 — Dispatch-time `model: sonnet` on `up:implementer` behaves identically to the removed frontmatter pin (same harness mechanism as the pre-T1 owner override).

### Unknowns
- UK1 — Final uexecute/uplan line counts after the shrink (targets ~220/~170) — resolved at execute.
- UK2 — Whether uverify's artifact-inferred CK-lite threshold (≤2 phases + small diff) matches owner intuition in practice — validated over fork usage; revisit if it misfires.
- UK3 — When/how the owner realigns cccc's `.claude/rules/workflow.md` (old 5-status enum, plan gates) — out-of-repo follow-up, T3 territory.

## Plan

Approach: six serial commits — eradicate hands-off first, rebuild the template, extract wave machinery, dedup, tier verify, document last. Serial because make.md is shared by PH1/PH2 and uexecute by PH1/PH3/PH4. Line refs are from the 2026-07-21 explorer map; re-anchor by heading text if drifted (RK1).

### PH1 — Hands-off eradication

- **1.1** `plugins/up/skills/handsoff/` (delete, 102 lines).
- **1.2** `plugins/up/commands/make.md` (modify) — drop: frontmatter mention (l.2), token activation (13), Mode assignment (36–37), template fields `**Mode:**` (48) + `### Hands-off decisions` + `### Deferred (needs user input)` (77–81), hands-off paragraphs in steps 4/6/7/12 (94, 104–110 keep interactive text, 117, 146), rule (190), section (196–198).
- **1.3** stage skills (modify) — delete hands-off sections/lines: `udesign` 195, 202–208; `uplan` 54, 195–201 (ambiguity handling becomes "stop and ask the user"); `uexecute` 22–26 hands-off list rules, 326–328; `uverify` 217–219; `ureview` 106–107, 196–198.
- **1.4** `plugins/up/skills/job-guardian/SKILL.md:17,51,54,119` (modify) — hands-off list refs → self-contained watch-record lists (`### Decisions`, `### Needs user input`). Respects IV1, IV5.
- Commit: `feat(t2): remove hands-off mode (0/82 adoption)`

### PH2 — Template & status realignment

- **2.1** `make.md:39-82` template (modify) — Status enum `design|planning|executing|reviewing|validating|done|shipped` with `<enum> — <annotation>` format; optional `**Jira:**`, `**Depends on:**` headers; `**Worktree:**` dropped; Design gains `### Prior art`; Plan gains `### Rollback`/`### Rollout` slots; Conclusion notes optional `### Deferred` (`- <what> → <ticket|task>`) and dated `### Follow-up — <date>`/`### Scope change — <date>`. Respects IV3, IV4, PC2.
- **2.2** `make.md:25-31` resume-check (modify) — parse `<enum> — <annotation>`; `shipped` ≙ done; `reference` skipped; unknown enum → ask; scan `docs/tasks/**/*.md`; unrecognized legacy headers ignored (AS1).
- **2.3** `make.md:100-111` (modify) — step 6 becomes branch-only decision; one-line pointer to `up:git-worktrees` for on-demand isolation.
- **2.4** `make.md` steps 11–12 (modify) — document `shipped` as owner-set post-merge/deploy state; finish options drop worktree cleanup.
- **2.5** `make.md` (modify) — epic convention: `docs/tasks/<epic>/` + `overview.md` at Status `reference`; slug step notes epic placement.
- **2.6** `skills/udesign/SKILL.md` (modify) — process step 1 gains prior-art consultation (`docs/tasks/` + `archive/` if present; cite file:line or "none found"); output shape gains `### Prior art`.
- **2.7** `skills/uplan/SKILL.md` (modify) — Format gains optional `### Rollback`/`### Rollout` with one-line inclusion criteria.
- **2.8** `skills/ureview/SKILL.md` (modify) — Conclusion guidance: park punted work as `### Deferred` → ticket/task.
- Commit: `feat(t2): census-backed template — status model, Prior art, Rollback/Rollout, Jira/Depends-on, epic folders`

### PH3 — Wave machinery → waves.md

- **3.1** `plugins/up/skills/uexecute/waves.md` (create) — single home: declaration format (from uplan 113–138) + wave derivation/disjointness/dispatch/wiring (from uexecute 40–76, 133–188); internal "log under Deferred" phrasing → "stop and ask the user"; must read standalone (RK3).
- **3.2** `skills/uexecute/SKILL.md` (modify) — mainline = serial per-phase loop (in_progress → implement inline or dispatch → plan-diff + consistency sweep); one line: plan declares `### Interface graph` → read `${CLAUDE_PLUGIN_ROOT}/skills/uexecute/waves.md`. Target ~220 lines (UK1). Respects IV2, AS2.
- **3.3** `skills/uplan/SKILL.md:113-138` (modify) — → 2–3 line pointer to waves.md; Format block IF/graph examples compressed. Target ~170 (UK1).
- Commit: `feat(t2): wave machinery single-homed in uexecute/waves.md`

### PH4 — SSOT dedup

- **4.1** `plugins/up/agents/implementer-sonnet.md` (delete).
- **4.2** `skills/uexecute/SKILL.md:82-93` (modify) — trivial phase → dispatch `up:implementer` with dispatch-time `model: sonnet`; scope-check paragraph (from implementer-sonnet.md 24–26) appended to the dispatch prompt. Respects PC3, AS3, IV5.
- **4.3** `skills/ureview/SKILL.md:12-16` (modify) — four-angle restatement → one line + pointer to `agents/reviewer.md`. Respects IV6.
- Commit: `feat(t2): drop implementer-sonnet; reviewer stance single-homed`

### PH5 — Verify tiering

- **5.1** `skills/uverify/SKILL.md` (modify) — new `## Tier` section after the preamble: CK-lite when plan ≤2 phases and diff is small (≥3 attacks — happy-path, negative, invariant/interface — plus smoke; one-screen summary); full protocol otherwise (UK2).
- Commit: `feat(t2): uverify CK-lite tier for small changes`

### PH6 — Docs + bump

- **6.1** `README.md` (modify) — drop Hands-off section, handsoff/implementer-sonnet mentions; task-file section reflects new statuses/slots; quickstart drops worktree prompt. Written against post-PH5 state (RK4).
- **6.2** `plugins/up/.claude-plugin/plugin.json` (modify) — version 0.3.25 → 0.3.26.
- Commit: `docs(t2): README realignment; bump 0.3.26`

### Risks / rollback
- RK1 — Line refs drift as phases edit shared files; mitigation: strict PH order, re-anchor by heading text.
- RK2 — Hands-off strip leaves orphaned clauses ("In hands-off, …"); mitigation: `grep -ri 'handsoff\|hands-off'` after PH1 (IV1 checked early, not just at verify).
- RK3 — waves.md not standalone-readable after extraction; mitigation: fresh read of waves.md after PH3 checking for references to text left in SKILL.md.
- RK4 — README describes pre-T2 flow; mitigation: PH6 last.
- Rollback: per-phase commits on `t2-template-realignment`; revert or drop branch.

Backwards-compat (restated): PH1 removes token parsing — `handsoff` becomes plain description text (design-accepted, 0/82 adoption); PH2.2 makes resume-check ignore unknown legacy headers so the 6 local + 157 cccc files need no migration (AS1). No other consumer-visible surface changes.

## Verify
<empty — filled by up:uverify>

## Code smells
- `skills/ureview/SKILL.md:29-35` — restates `_brevity` content locally instead of pointing (same pattern as uexecute:19-26); defensible locality, left as-is.

## Conclusion
<empty — filled by up:ureview>

### Deviations from plan
- PH2: also edited Worktree references at `uexecute/SKILL.md:15,32` beyond the 2.x bullets — consistency pass for the dropped `**Worktree:**` header (IV5).
- PH4.2 applied in `skills/uexecute/waves.md` ("Choosing the implementer model"), not `uexecute/SKILL.md:82-93` — PH3's extraction had already moved the agent-choice section there.
- PH3.1: dropped the extracted text's cross-references to the source task's IDs (PC4, IV2, AS1, IF3, IF5, IF6) — they point into another task's ID space, orphaned in a standalone waves.md (`_brevity` p.6).
