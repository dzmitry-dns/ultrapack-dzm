# ujira V1.1 polish — dogfood follow-ups

**Status:** planning
**Branch:** main
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
<empty — filled by up:uplan>

## Verify
<empty — filled by up:uverify>

## Conclusion
<empty — filled by up:ureview>
