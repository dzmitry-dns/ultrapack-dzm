# Reviewer calibration: severity by real trigger, and no commit trailers from any stage

**Status:** planning
**Branch:** main
**Goal:** After the change, an `up:reviewer` dispatch reports as Important only findings with a named input that exists in today's code (or in a change the task file names) and produces a wrong result, a lost or doubled write, an exposure, a crash, or a failing build; every reported finding carries a three-part Trigger line (who, how often, what breaks); text nits land in a separate no-severity block. Separately, no commit made by any pack stage (including the `/up:make` Status-transition commits) carries a `Co-authored-by` or other trailer, stated once pack-wide. Confirmed by one `up:reviewer` dispatch on this task's own diff (Trigger line present on every finding, no wording-only finding above the text block) and by the commits of this task carrying no trailer.

## Design

Purpose: stop `up:reviewer` from labelling real-but-costless findings as Important, and close the one gap through which Claude attribution reached the repo's commits.

Evidence (transcript audit, 2026-09-12, 19 dispatches from 2026-08-30 to 2026-09-12, 57 findings): every Critical was justified; 24 of 50 Important were not (duplicated logic with no failing input today 10, wording with no behavior change 8, hypothetical state or race 3, type-shape style 2, commit bookkeeping 1); one finding was under-graded (a bare `z.url()` on an unauthenticated form stores `javascript:` links, Critical, reported as Important). The Trigger clause added in 6b8e276 was filled in 3 of 58 findings. Three lines of `reviewer.md` produce the pattern together: line 49 makes every scan hit "≥ 80 confidence", so being real is mistaken for being costly; line 72 ("below Important, don't report") leaves no lower shelf, so a real nit is promoted rather than dropped; the scan items name an imagined future maintainer with no requirement that the future change exists.

Chosen approach (A of three): tighten the existing two-tier scheme in place, no new tiers, no new agent.

1. Confidence and severity are separated. Hitting a scan item sets confidence (the issue is real), never severity (the issue costs something). One sentence replaces the "(all are ≥ 80 confidence when found)" clause.
2. Important gets a checkable definition: a named input that exists in today's code, or in a change the task file already names (a UK, a follow-up, a plan item), and that produces a wrong result, a lost or doubled write, an exposure, a crash, or a failing build. Duplicated logic, naming drift, comment or description wording, file placement, and type-shape choices never reach Important on their own. Critical keeps its definition and gains one clause: a public or unauthenticated caller counts as high frequency whatever the traffic, so stored or rendered attacker-controlled content is Critical.
3. The Trigger becomes a required second line under every Critical and Important finding, three parts: who, how often, what breaks on that input. A finding whose Trigger line cannot be filled in all three parts is dropped, not downgraded. The line moves out of the parenthetical because the parenthetical form was filled 3 times in 58.
4. A lower shelf: `### Below Important (no fix required)` in the output, at most 5 one-line entries, no Fix line, no confidence. Conversation bleed, brevity violations, duplicated helpers and other GPC8 smells go there. `up:ureview` handles the block in one pass: a wording entry that checks out is applied in one commit with no Conclusion entry beyond an optional "Text fixes: N applied" line; a smell entry is appended to `## Code smells` and decided at Future work like any other smell. Nothing in the block enters the fair-evaluation loop, and nothing in it blocks the merge verdict.
5. `up:ureview` step 3.3 (re-grade as probability × damage) keeps its own independent check but names the same Important definition, so the two files cannot disagree about what Important means.

Trailer rule: one pack-wide rule in `_principles.md` under a new "Commits" section, same single-home pattern as "Manual-only skills": every commit made by any stage or by `/up:make` itself is English, `<type>: <concise>`, and carries no `Co-authored-by` or other trailer. `/up:make` Rules gains one pointer line (the Status-transition commits are made by the main session under `/up:make`, and no stage text governs them today, which is how six commits on 2026-09-12 got the trailer). `up:uexecute` step 3 points at the section instead of restating it. `agents/implementer.md` keeps its inline ban: a subagent cannot be assumed to read pack files, and the inline line is what has kept implementer commits clean. The settings-level fix (`attribution` key in `~/.claude/settings.json`, applied 2026-09-12) is outside the pack and is what actually stops the harness from adding the trailer; the pack rule is the second layer for any machine without that key.

Rejected alternatives:
- B, move grading out of the reviewer: the reviewer reports everything at ≥ 80 with no tier and `up:ureview` grades. Gives up the reviewer's tier as an independent signal and moves judgment work into the main session, against the owner's lean-main-context instruction.
- C, adopt the `/review` user skill's frequency × damage matrix (High / Medium / Low) inside the pack: three tiers would rename what `up:ureview`, the Conclusion template, and every past task file call Critical / Important; a rename ripples through files this task has no reason to touch, and the two-tier scheme is not the defect, the definition of Important is.

Scope: `up:requirements-reviewer` is not touched. Its findings are requirement-vs-delivery gaps where the trigger is the unmet clause itself, and the audit did not measure it. Recorded as deferred scope below the Conclusion when the task closes.

Backwards compatibility: no break. `up:ureview` reads the reviewer's output as text, not by a parser, and the new block is optional (a reviewer output without it is handled exactly as today). The Conclusion template gains one optional line. Tier names are unchanged, so every past task file's "Review findings" reads the same. `/up:make` resume reads only the Status header. The trailer rule adds text and removes none.

TDD: no (reason: doc-only plugin, no runtime code; verified by one reviewer dispatch on this task's own diff and by the diff itself).

### Prior art
- `docs/tasks/audit-fixes.md:52` — the two-pass (find all, then filter) shape of `reviewer.md` was set there; this task keeps it and changes only what the filter admits.
- `docs/tasks/audit-fixes.md:47-48` — the `Co-authored-by` ban was placed in `uexecute` and `implementer` only; the stage commits of `/up:make` were never covered, which this task closes.
- `plugins/up/skills/_principles.md` "Manual-only skills" — the single-home pattern ("callers only point here") reused for the Commits section.
- `docs/tasks/requirements-review.md:16` — the requirements reviewer's contract (two tiers, ≥ 80) is a separate agent, left untouched here.
- `~/.claude/skills/review/SKILL.md` — the owner's probability × damage grading for `/code-review`; the source of the "who, how often" wording, adapted, not adopted wholesale (see rejected C).

### Invariants
- IV1 — Tier names stay `Critical` and `Important`; no tier is added, renamed, or removed, and a reviewer output without the new block is processed by `up:ureview` exactly as before.
- IV2 — Every Critical or Important finding in the reviewer output format carries a Trigger line with all three parts, and the reviewer text states that a finding without all three is dropped, not downgraded.
- IV3 — The definition of Important is one sentence in `reviewer.md`, and `ureview` step 3.3 uses the same criterion by name, not a paraphrase that could diverge.
- IV4 — The no-trailer rule has one home, `_principles.md` → Commits; `make.md` and `uexecute` point there; `implementer.md` keeps its inline copy with identical meaning.
- IV5 — The plugin version moves by exactly one patch step above what `main` holds when the change lands.

### Assumptions
- AS1 — A required second line is filled by the reviewer more reliably than a parenthetical clause on the same line (the parenthetical was filled 3 times in 58).
- AS2 — Dropping findings that lack a three-part Trigger does not hide real Critical findings, because the Critical scan already requires opening the entry point and its role guard.

### Unknowns
- UK1 — Whether the narrowed Important definition hides duplication the owner would still have fixed; measurable after the next five reviewer dispatches by counting `Below Important` smells the owner acts on.
- UK2 — Whether a dispatched agent can read `${CLAUDE_PLUGIN_ROOT}` paths at all; if yes, `implementer.md` could point at the Commits section instead of keeping the inline copy.

## Plan
<empty — filled by up:uplan; gains ### Rollout / ### Rollback when the change ships to a live system>

## Verify
<empty — filled by up:uverify>

## Code smells
<empty — file:line + one-line smell passed while exploring and left unfixed (out of scope, non-trivial); deleted if none>

## Conclusion
<empty — filled by up:ureview; after done/shipped grows dated ### Follow-up — <date> / ### Scope change — <date> entries and ### Deferred scope-parking>
