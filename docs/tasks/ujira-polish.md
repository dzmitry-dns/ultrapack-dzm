# ujira V1.1 polish — dogfood follow-ups

**Status:** validating
**Branch:** ujira-polish
**Depends on:** docs/tasks/jira-adapter.md (`### Follow-up — 2026-07-21`)
**Goal:** `plugins/up/skills/ujira/SKILL.md` unambiguously describes three description-draft behaviors (matches → skip, stale-field-only → targeted update, doesn't match → replace) and blesses bare `- key: value` lines as the sole config parse target; grep-proof of consistency with `make.md` ujira hooks is clean. Doc-only contract clarification — no separate dogfood run gates this.

## Design

Skipped — Small (single file + version bump). Scope fixed by the owner from the shipped adapter's dogfood findings (`docs/tasks/jira-adapter.md`, `### Follow-up — 2026-07-21`):

1. **Field-level merge for description drafts.** Today the draft contract offers only replace-whole or skip. The dogfood case "structurally matches the contract, one field stale" (e.g. an outdated `Details:` pointer) must produce a *targeted update*: the draft proposes replacing only the stale field, preserving human-written what+why and acceptance wording.
2. **"Matches contract" is explicitly non-binary.** Three verdicts: matches → skip; stale-field-only → targeted update; doesn't match → replace draft.
3. **Canonical config format.** Bare `- key: value` lines are the only parse target of the consumer's `## Jira adapter` section; surrounding prose is allowed, but keys must not be wrapped in backticks or prose (dogfood trap: the section is simultaneously docs and live config).

Out of scope (parked in jira-adapter.md `### Deferred scope-parking`): sync-state in the identity header (**Jira:** annotation scope flag from review) — parked until multi-ticket consumers; ticket-creation drafting.

### Prior art

- `docs/tasks/jira-adapter.md:155-161` — Follow-up section: dogfood evidence (UK2 resolution) and the two pack follow-ups this task implements.
- `plugins/up/skills/ujira/SKILL.md:36-45` — current Draft contract (replace-or-skip only, line 38: "refreshed only when it no longer matches reality").
- `plugins/up/skills/ujira/SKILL.md:21-34` — current Config section (fenced example, no canonical-format rule).
- `plugins/up/skills/ujira/SKILL.md:76` — draft block's `Description (replace):` item — the only draft-block shape for descriptions today.

### Invariants

- IV1: Thin-layer contract unchanged — a targeted update never introduces banned content (task-file ids, file:line, SHAs, technical detail).
- IV2: Approval gate unchanged — targeted updates are drafts like any other; never applied without per-draft approval; `manual` mode still never writes.
- IV3: `make.md` ujira hooks (make.md:39, make.md:112, make.md:147) stay consistent with SKILL.md — no hook references a behavior SKILL.md no longer describes, and vice versa.
- IV4: Config example in SKILL.md must itself satisfy the canonical format it prescribes.

### Assumptions

- AS1: The three-verdict model needs no make.md changes — hooks reference *when* drafting happens, not *how* descriptions are matched. (Checked at verify via grep-proof.)

### Unknowns

- UK1: Whether the draft block needs a distinct rendering for targeted updates (e.g. `Description (update <field>):`) or reuses the replace shape with a narrower payload. Resolve at plan.

## Plan

Approach: three surgical edits to the ujira skill contract, each landing where the current text already speaks — match semantics into `## Draft contract`, verdict reference into `## Triggers & coalescing` + `## Draft block`, parse rule into `## Config`. No new sections, no make.md changes (AS1).

UK1 resolved: targeted updates get a distinct draft-block rendering — `Description (update: <field>):` carrying only the replacement line(s) — so the owner sees at a glance that human wording elsewhere is untouched; reusing the replace shape would make skip-vs-clobber invisible.

### PH1 — SKILL.md contract edits

- **1.1** `plugins/up/skills/ujira/SKILL.md:36-45` (modify) — `## Draft contract`
  - Replace line 38's binary "refreshed only when it no longer matches reality" with a three-verdict match rule: matches → skip; structurally matches but one field stale (e.g. outdated `Details:` pointer) → targeted update replacing only that field, preserving human-written what+why and acceptance wording; doesn't match → full replace draft. One line per verdict. Respects: IV1.
- **1.2** `plugins/up/skills/ujira/SKILL.md:59` (modify) — `## Triggers & coalescing`
  - "a description draft when the current ticket description doesn't match the contract" → "a description draft per the match verdict (skip / targeted update / replace)". Respects: IV3.
- **1.3** `plugins/up/skills/ujira/SKILL.md:66-84` (modify) — `## Draft block`
  - After the block example: targeted-update rendering — item reads `Description (update: <field>):` with only the replacement line(s). Approval/skip semantics unchanged. Respects: IV2.
- **1.4** `plugins/up/skills/ujira/SKILL.md:21-34` (modify) — `## Config`
  - Add parse contract after the fenced example: bare `- key: value` lines are the sole parse target of the section; surrounding prose allowed; keys never wrapped in backticks or folded into sentences — the section is docs and live config at once. Existing fenced example already conforms. Respects: IV4.
- Commit: `docs(ujira): three-verdict description matching, targeted-update rendering, canonical config format`

### PH2 — version bump

- **2.1** `plugins/up/.claude-plugin/plugin.json:3` (modify) — `"version": "0.3.27"` → `"0.3.28"`.
- Commit: `chore: bump up to 0.3.28`

Backwards-compat: doc-only; the shipped consumer config (bare `- key: value` lines post-dogfood-fix) already satisfies the new parse rule — no consumer edit required.

### Test strategy

Doc-only — verification is read-through + grep-proof:
- grep `ujira|Jira` in `plugins/up/commands/make.md` (hooks at 39, 112, 147): every hook behavior still described by SKILL.md, no SKILL.md behavior contradicting a hook (AS1, IV3).
- SKILL.md self-consistency: draft-block renderings cover exactly the verdicts the contract names; config example passes its own parse rule (IV4).
- Banned-content list unchanged and reachable from the targeted-update path (IV1).

## Verify

**Result:** passed

Happy-path:
- CK1 — hunt a verdict without a rendering / rendering without a verdict, incl. no-MCP path — held: skip=no item, update=`Description (update: <field>):`, replace=block item 3; no-read fallback (SKILL.md:100) composes with "compare on later triggers"
- CK2 — make the config section violate its own parse rule — held: fenced example is bare lines; backticked key-docs bullets live in the pack SKILL.md, outside any consumer `## Jira adapter` section

Negative:
- CK3 — grep plugin for leftover binary-match language (`doesn't match the contract`, `no longer matches reality`, `replace-or-skip`) — held: clean

Invariants / assumptions:
- CK4 (IV3, AS1) — make.md hooks (39, 112, 147) vs SKILL.md behaviors — held: hooks name *when* drafting happens, never match semantics; AS1 held, no make.md edit needed
- CK5 (IV1) — reach targeted update while dodging the banned list — held: "Banned in any draft" (SKILL.md:52) covers the update path
- CK6 (IV2) — find an auto-apply path for targeted updates — held: update renders as block item 3, per-block approve/edit/skip unchanged

Interfaces:
- CK7 — manifests — held: plugin.json valid JSON at 0.3.28, marketplace.json pins no version

Smoke: SKILL.md frontmatter well-formed (name + description), section structure intact — doc-only change loads as a skill file.

## Conclusion

Outcome: Goal achieved — three-verdict matching, targeted-update rendering + apply path, and canonical config format all land in SKILL.md; make.md hooks grep-proof clean. Commits ee4d73a (contract), 6e785a2 (apply path), c60ed49 (bump 0.3.28).

Invariants:
- IV1 — "Banned in any draft" covers the targeted-update path unchanged (CK5)
- IV2 — targeted update renders inside the draft block; per-block approve/edit/skip untouched (CK6)
- IV3 — hooks at make.md:39/112/147 name *when* drafting fires, never match semantics (CK4)
- IV4 — fenced config example is bare `- key: value` lines, conforms to its own rule (CK2)

### Assumptions check
- AS1 — held — no make.md edit needed; grep-proof at verify (CK4)

### Unknowns outcome
- UK1 — resolved — distinct rendering `Description (update: <field>):`; reusing the replace shape would hide skip-vs-clobber from the owner

Review findings:
- Important: targeted-update fragment had no defined apply path — `mcp`'s "apply exactly that draft" would clobber the description down to the fragment. Resolved in 6e785a2: splice-into-live-description rule covering both apply modes.
