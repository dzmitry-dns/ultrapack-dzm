---
name: ureview
description: Use after verify passes for the future maintainer's audit — sit in the chair of the person who'll touch this code in 3-6 months and ask "what will bite us later?" at the decision level. Surfaces wrong abstractions, load-bearing-but-unobvious shapes, next-change traps, drift from surrounding code; raises a Scope flag if the whole change looks like the wrong call. Dispatches up:reviewer (critical, high-confidence filter), processes findings fairly, fills the task file's `## Conclusion`.
---

# Review

Review's stance: the future maintainer's audit. Sit in the chair of the person who'll touch this code in 3-6 months and ask the headline question — what will bite us later?

The job is to spot the design or structural choice that will force a nasty rewrite when someone next has to extend, migrate, or refactor. Catch the shape you'll regret in 6 months while it's still cheap to change.

The four audit angles — wrong abstraction / premature commit, load-bearing but unobvious, bites the next change, inconsistent with surrounding code — are defined in `${CLAUDE_PLUGIN_ROOT}/agents/reviewer.md`, their single home.

Review has license to question scope, surfacing it as a flag for the user. If review notices "this whole change may have been the wrong call" or "the design rests on a premise that looks wrong now that the code exists," it goes into the Conclusion as a `Scope flag` for the user to act on. Review surfaces; redesign belongs to udesign.

Review is a process, not just a section. Its end product is the `## Conclusion` section of the task file, filled in based on an independent code review and the work that was done.

## When to invoke

- After `up:uverify` passes
- Before merge to main
- Before opening a PR
- Never skipped, regardless of task size

## Brevity

<required>
Before writing the `## Conclusion`, read `${CLAUDE_PLUGIN_ROOT}/skills/_brevity.md`. Apply its five principles. `Outcome:` is ≤1 sentence + the commit SHA — never re-narrate the diff. Omit subsections whose content would be "none" / "clean" / "no deviations" / "no findings" / the default: `Plan adherence`, `Review findings`, `Scope flag`, `Future work`, `Deferred`, `Verified by`, `Deviations from plan`, `Known risks`. `Invariants:`, `Assumptions check:`, and `Unknowns outcome:` stay when the task had any IV / AS / UK — they carry audit value even on pass. The Exception clause still holds: findings, deviations, risks, violated assumptions, and deferrals always carry evidence and "why".

`## Code smells` is shared across stages, not a Conclusion subsection: at task end delete the header if it stayed empty (brevity 1). Leave recorded smells in their own section; promote one to `Future work` only if this task decides to schedule its fix — don't duplicate.
</required>

## Two roles, two attitudes

<reviewer-role>
The `up:reviewer` subagent is **critical**. It is dispatched with a diff, a plan, and invariants — but not the rationale behind the changes. It looks for violated invariants, plan misalignment, bugs, and risks. Confidence-filtered (≥80). Severity-tiered.
</reviewer-role>

<dispatcher-role>
You (the dispatcher) are **fair**. Fair means: take every finding seriously, but verify it against the codebase before acting. Fair is neither reflexive agreement nor reflexive pushback. Fair is: restate → verify → evaluate → decide.
</dispatcher-role>

The asymmetry is deliberate. A tough reviewer catches more real issues; a fair dispatcher avoids overcorrecting on mistaken calls.

## Process

### 1. Dispatch `up:reviewer`

Get git SHAs:
```bash
BASE_SHA=$(git merge-base HEAD main)   # or the branch point for this task
HEAD_SHA=$(git rev-parse HEAD)
```

Dispatch the `up:reviewer` agent with:
- Task file path (`docs/tasks/<slug>.md`)
- `BASE_SHA` and `HEAD_SHA`
- Working directory (explicitly — the agent does not inherit `cwd` reliably)

<system-reminder>
Do **not** pass session history to the reviewer. The reviewer must not see the rationale behind changes — only the Plan, Invariants, and diff. Independence is the point.
</system-reminder>

**Dispatch prompt skeleton** (guidance):

```
Task file: <docs/tasks/<slug>.md>
BASE_SHA: <merge-base with main, or branch point>
HEAD_SHA: <current HEAD>
Working directory: <absolute path>
```

Model: the agent pins its own default. When the owner asks for a specific model for this review ("review on Fable", "review on the session model"), pass it as the dispatch-time model override for that run only — never edit the agent's frontmatter pin for a one-off. Applies equally to the 1b dispatch below.

### 1b. Optional second dispatch — `up:requirements-reviewer`

A requirements-level audit that catches "built cleanly, but not the right thing". Suggest it for Medium+ or high-stakes changes; the user opts in — never auto-run it, and it complements (never replaces) `up:reviewer`.

Dispatch with ONLY:
- The verbatim original requirement — the user's own words that started the task, unparaphrased. Source it from the session's original ask; in a fresh session, ask the user to paste it. Never reconstruct it from the task file.
- `BASE_SHA` and `HEAD_SHA`
- Working directory

Never pass the task file, plan, design, or rationale — the agent's blindness to the implementer's worldview is the point. Its findings join the same loop below; keep only requirement-vs-delivery deltas (code-quality overlap belongs to `up:reviewer`).

### 2. Read feedback without reacting

Receive the reviewer's output. Do not immediately reply with fixes or pushback. Classify first:

- Critical: fix before proceeding
- Important: fix before merge
- Plan finding: the plan itself may be wrong

### 3. Evaluate each item fairly

<required>
For every finding:

1. Restate in your own words. If you can't restate it, ask the reviewer to clarify — don't guess.
2. Verify against the codebase. Does the issue actually exist as described? Open the file, read the lines.
3. Evaluate technically: is the suggested fix right for *this* codebase and the Design?
4. Decide: implement, push back with technical reasoning, or escalate to the user.
</required>

### 4. Announce the plan before editing

<required>
Before any fix goes in, tell the user what you decided for each finding. One line per finding:
- what the reviewer said,
- your verdict (fix / push back / defer),
- if fixing: the exact change you are about to make.

This is a short summary — the user can interject, then you apply the fixes.
</required>

<bad-example>
"Evaluating reviewer findings fairly." *(then a flurry of edits with no explanation)*
</bad-example>

<good-example>
"Reviewer findings:
- Important #1: reviewer tool list missing `Bash`. Verdict: fix. Editing Design section of task file.
- Important #2: try.md and step-back.md missing frontmatter. Verdict: fix. Adding frontmatter to both.

Applying now."
</good-example>

### 5. Apply fixes

Fix Critical and Important issues. Commit each as its own logical unit.

<required>
For every fix, run the consistency pass (same rule as `up:uexecute`): if you're tightening a rule or changing a pattern, grep the diff and the wider repo for the same pattern and apply the change everywhere in the same commit. Do not leave siblings in a mixed state — that's how the reviewer's next round finds the same class of issue four more times.
</required>

If fixes are substantial, re-dispatch the reviewer on the new diff.

### 6. Write the `## Conclusion`

```markdown
## Conclusion

Outcome: <≤1 sentence on whether the Goal is achieved or what real-world validation remains, + commit SHA. Don't re-narrate the diff.>

Invariants:
- IV1 — <how it was verified>
- IV2 — <...>

### Assumptions check   (omit entire subsection if the task had no AS)
- AS1 — held | violated | unverifiable — <one-line evidence or "why unverifiable">
- AS2 — ...

### Unknowns outcome   (omit entire subsection if the task had no UK)
- UK1 — resolved | still-open — <one-line resolution, or why it's still open>
- UK2 — ...

Plan adherence: <deviations>   (omit entire subsection if no deviations)

Review findings:   (omit entire subsection if no Critical or Important)
- Critical: <resolved, how>
- Important: <resolved or explicitly deferred with justification>

Scope flag:   (omit unless reviewer raised one — never auto-act; surface verbatim for the user)
- <reviewer's flag, 1-2 sentences>

Future work:   (omit entire subsection if none — do not write "none")
- <item> — Justification: <Design-scope line> OR <new fact discovered>

### Deferred   (omit if nothing was parked — scope intentionally punted out of this task)
- <what> → <ticket | task file>

Verified by: <only non-default items: deferred smokes, manual checks the next reader needs to know about>   (omit if only the routine reviewer+verify ran)
```

A violated AS is always material — it means the design rested on a premise that turned out false. Record evidence and, if it invalidates the outcome, either redo the affected phase or surface it to the user.

After `done`/`shipped`, the Conclusion is a living log: post-merge reality gets appended as dated subsections — `### Follow-up — <date>`, `### Scope change — <date>` — never by rewriting the original review record.

## Receiving feedback — rules

<dispatcher-rules>
Never:
- "You're absolutely right" / "Great catch" / "Thanks for catching that"
- Implement blindly without verifying against the codebase
- Batch fixes without checking each independently
- Respond partial when multiple findings may be linked — clarify all first

Do:
- Verify against codebase reality before acting
- Push back with technical reasoning when the reviewer is wrong
- Ask for clarification when a finding is unclear
- Show the fix in a diff — actions over words

Pushback is legitimate when:
- The suggestion breaks existing behavior
- The reviewer lacks context only the Design has (e.g. intentional tradeoff)
- The suggestion violates YAGNI (over-engineering an unused path)
- The suggestion conflicts with explicit Design / Invariants decisions
</dispatcher-rules>

## Never

- Accept "ready to merge" without evidence
- Merge with open Critical or Important findings
- Skip the Conclusion write-up
- Run review on yourself (always use the subagent — preserve independence)

## Terminal state

Conclusion written, all Critical/Important resolved or explicitly deferred with justification → Status → `validating`. Review does not mark `done`: control returns to `/up:make` to validate the Goal (step 11) before any finish action. The user chooses the finish action; you don't auto-merge.
