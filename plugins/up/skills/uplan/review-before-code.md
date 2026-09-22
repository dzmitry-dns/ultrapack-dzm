# Review before code

When, how, and how often an independent `up:plan-reviewer` reviews a task file's Design or Plan before any code is written. This file is the single home of the procedure: `up:udesign` and `up:uplan` run it at their step 11, `/up:make` points here, and none of them restate it.

## When it runs

Both points decide from the task file alone, never from a size held in session memory, so a resumed session reaches the same answer.

- **Plan point**: in `up:uplan`, after the scope-creep check, before the plan goes to the owner for approval. Runs when `## Design` holds a design `up:udesign` wrote. No review when the section is missing, holds only the template placeholder `<empty — filled by up:udesign>`, or records that Design was skipped: Small and Trivial tasks skip Design and write a note that opens with `Skipped`.
- **Design point**: in `up:udesign`, after the self-review, before the final approval. Runs only when the written `## Design` shows a Large signal:
  - a DB migration (schema or data) the design commits to;
  - a `Backwards compatibility:` line whose resolution is a hard break, or a removal or rename without a shim; "no break", "greenfield", deprecate with a shim, and a versioned new behavior do not fire;
  - the line `Size: Large (owner)`.

  A new API surface alone is not a signal.

### Skip

The owner skips with "skip pre-code review" or "без ревью до кода", in the ask or at any later point. Said once, it covers every remaining review point of the task. Each slot reached records `Reviewed before code: skipped by owner, <date>`. A skip said during design is written to the design slot even when the design point did not fire, so the plan point of a later session sees it. The phrase never covers the final `up:ureview` (`/up:make` → Rules).

### Resume

Before running a point, read its slot (see Record line):

- No line → round 1.
- `skipped by owner` → no review. A design slot reading `skipped by owner` also skips the plan point.
- `1 round` with at least one Critical/Important fixed → round 2.
- Anything else → no further round; go on to approval.

A re-plan that `up:uexecute` invokes on a structural deviation (`${CLAUDE_PLUGIN_ROOT}/skills/uexecute/SKILL.md` → Deviations from plan, item 4) is a new document: the plan point starts again at round 1, its line replaces the old one in the plan slot, and the same rules apply. A recorded skip still holds.

## Dispatch

1. One line before the dispatch, per `${CLAUDE_PLUGIN_ROOT}/skills/_principles.md` → Dispatch narration, naming the point and the round. No pause; the owner may answer the line with the skip phrase.
2. Dispatch `up:plan-reviewer`:

   ```
   Task file: <absolute path to docs/tasks/<slug>.md>
   Review point: <design | plan>
   Working directory: <absolute path>
   Owner's ask (verbatim): <the owner's own words that started the task>
   Jira ticket: <ticket summary and description text>
   Rejected in round 1 (text only, re-raise only on new evidence): <one line per finding>
   ```

   - `Owner's ask`: only when this session holds the owner's own words; never reconstructed from the task file.
   - `Jira ticket`: only when the task file has a `**Jira:**` header and an Atlassian read tool is available to fetch it.
   - `Rejected in round 1`: round 2 only; the finding text without the reason it was rejected.
   - Never session history or the reasons behind a choice.
   - Model override: `${CLAUDE_PLUGIN_ROOT}/skills/ureview/SKILL.md` step 1, the `Model:` paragraph, applies unchanged.
3. One line when it returns: counts per tier and the verdict.

## Findings

Process them by `${CLAUDE_PLUGIN_ROOT}/skills/ureview/SKILL.md` steps 2-4: classify, restate, verify against the code, re-grade, announce the verdict per finding before editing. Differences:

- Re-grade with the Important definition in `${CLAUDE_PLUGIN_ROOT}/agents/plan-reviewer.md` → Severity.
- Fixes edit the task file only.
- `Below Important`: open each line once; apply a wording entry that checks out, drop the rest.
- A `Scope flag` goes to the owner verbatim with the approval request; the stage does not act on it.

## Rounds

- Round 2 runs only when round 1 produced an accepted Critical or Important that changed the document.
- Every round is a fresh dispatch.
- At most 2 automatic rounds per review point; a third runs only on the owner's request.

## Record line

After every round, write or update in place one line in the point's slot:

`Reviewed before code: <N> rounds, <n> Critical/Important fixed, <m> rejected, <date>`

`n` and `m` count Critical and Important findings over all rounds of the point; `Below Important` is not counted. On a skip the line is `Reviewed before code: skipped by owner, <date>`.

Slots, never inside a subsection:

- Design point: the line right after `TDD:` in `## Design`.
- Plan point: the line right after `Approach:` in `## Plan`.
