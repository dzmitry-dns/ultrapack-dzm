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

Relation to the built-in `/code-review`: that skill hunts bugs in a diff and knows nothing about the task file. This skill is the maintainability audit against Plan, Invariants, and Assumptions, and it writes the Conclusion. They complement each other; for a Medium+ diff, offer `/code-review` first unless it already ran on this diff in the task (the owner's post-feature checklist often runs it), and hand its unresolved findings to the reviewer dispatch as context-free facts, never as rationale. One bug hunt per diff, never two.

## Brevity

<required>
Before writing the `## Conclusion`, read `${CLAUDE_PLUGIN_ROOT}/skills/_brevity.md`. Apply its six principles. `Outcome:` is ≤1 sentence + the commit SHA — never re-narrate the diff. Omit subsections whose content would be "none" / "clean" / "no deviations" / "no findings" / the default: `Deviations from plan`, `Known risks`, `Review findings`, `Scope flag`, `Future work`, `Deferred`, `Verified by`. `Invariants:`, `Assumptions check:`, and `Unknowns outcome:` stay when the task had any IV / AS / UK — they carry audit value even on pass. The Exception clause still holds: findings, deviations, risks, violated assumptions, and deferrals always carry evidence and "why".

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

See `${CLAUDE_PLUGIN_ROOT}/skills/_principles.md` → Dispatch narration.

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

<red-flags>
Do **not** pass session history to the reviewer. The reviewer must not see the rationale behind changes — only the Plan, Invariants, and diff. Independence is the point. The one exception is a re-dispatch after fixes (step 5): its prompt may carry the fix SHAs and the text of rejected findings, without reasons. Neither is session history or rationale.
</red-flags>

**Dispatch prompt skeleton** (guidance):

```
Task file: <docs/tasks/<slug>.md>
BASE_SHA: <merge-base with main, or branch point>
HEAD_SHA: <current HEAD>
Working directory: <absolute path>
Review fixes (re-dispatch only; not plan deviations): <fix commit SHAs>
Rejected earlier (re-dispatch only; text only, re-raise only on new evidence): <one line per finding>
```

Model: the agent pins its own default. When the user asks for a specific model for this review ("review on Fable", "review on the session model"), pass it as the dispatch-time model override for that run only — never edit the agent's frontmatter pin for a one-off. Applies equally to the 1b dispatch below.

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
- Below Important: no verdict needed; handled in step 5b

### 3. Evaluate each item fairly

<required>
For every finding:

1. Restate in your own words. If you can't restate it, ask the reviewer to clarify — don't guess.
2. Verify against the codebase. Does the issue actually exist as described? Open the file, read the lines.
3. Re-grade the tier as probability × damage. The reviewer's tier is an input, not the answer: for `up:reviewer` findings, apply the Important definition in `${CLAUDE_PLUGIN_ROOT}/agents/reviewer.md` → Severity, as written there; `up:requirements-reviewer` findings keep their own definition (the unmet clause is the trigger). A finding that fails its definition is deferred with justification, not fixed as Important. A finding that needs two operators on the same row inside one request window, or a state no existing code path produces yet, drops to Important at most, and to "deferred with justification" when the fix is more than one line.
4. Evaluate technically: is the suggested fix right for *this* codebase and the Design?
5. Decide: implement, push back with technical reasoning, or escalate to the user.
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
- Important #1: `parseConfig` swallows a malformed line instead of raising (IV2). Verdict: fix. Editing `config.ts:41`.
- Important #2: duplicate of an existing helper in `utils/slug.ts`. Verdict: fix. Replacing the copy with an import.

Applying now."
</good-example>

### 5. Apply fixes

Fix Critical and Important issues. Commit each as its own logical unit; message rules in `${CLAUDE_PLUGIN_ROOT}/skills/_principles.md` → Commits.

<required>
For every fix, run the consistency pass (same rule as `up:uexecute`): if you're tightening a rule or changing a pattern, grep the diff and the wider repo for the same pattern and apply the change everywhere in the same commit. Do not leave siblings in a mixed state — that's how the reviewer's next round finds the same class of issue four more times.
</required>

A fix that changes behavior (not only wording) gets one re-dispatch of `up:reviewer` per review, whatever the re-dispatch finds; a further round runs only on the owner's request. It covers the full task range, `BASE_SHA` to the new `HEAD`; a fix-only range would make every planned phase look missing. The prompt names the fix SHAs as review fixes, not plan deviations, and carries the text of the findings you rejected, without reasons, to be re-raised only on new evidence.

### 5b. Below Important

The reviewer's `### Below Important` block (when present) skips the fair-evaluation loop above (steps 2-4). Open each line once: a wording entry that checks out is applied, all of them in one commit `fix: review text fixes`; a duplicate or smell entry is appended to `## Code smells` as `file:line — smell` and decided at Future work. Nothing in the block changes the merge verdict.

### 6. Write the `## Conclusion`

Replace the placeholder line only. Any `### Handoff — <date>` blocks that follow it (written by `/up:summary`) stay below the written Conclusion.

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

### Deviations from plan   (omit entire subsection if no deviations; execute creates it, review keeps it)
- <what changed> — <why>

### Known risks   (omit entire subsection if none; execute creates it when a plan gap was left to raise)
- <risk> — <why it was left and what would resolve it>

Review findings:   (omit entire subsection if no Critical, Important, or text fixes)
- Critical: <resolved, how>
- Important: <resolved or explicitly deferred with justification>
- Text fixes: N applied (<sha>)   (omit when none)

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
