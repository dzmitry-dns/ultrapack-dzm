# Add /up:e explain command

**Status:** done
**Branch:** main
**Worktree:** none
**Goal:** `/up:e` exists at `plugins/up/commands/e.md`, matches the style of sibling commands (try.md, step-back.md), and produces a terse, colleague-to-colleague explanation with named follow-up threads when invoked.
**Mode:** interactive

## Design
Skipped (Small task — single new command file, pattern already established by sibling commands try.md/step-back.md).

The ask (from conversation): a `/e` command that explains something the way one engineer explains it to another — plain language, assumes only vague recall of prior context, picks a realistic depth instead of dumping everything, ends with named (not answered) follow-up threads.

### Invariants
- IV1: Command file lives at `plugins/up/commands/e.md`, invoked as `/up:e` (plugin-prefixed, per repo naming convention).
- IV2: Frontmatter `description:` present, matching the style of `try.md`/`step-back.md`/`make.md`.
- IV3: No runtime code — doc-only, per repo's design principle.

### Principles
- PC1: Match the terseness and structure of the simplest sibling commands (try.md, step-back.md) rather than the heavier orchestration ones (make.md, reflect.md) — this command is a single-shot response, not a multi-stage flow.
- PC2: Explicit `## Arguments` section since the command needs to know its target, unlike try.md/step-back.md which infer from git state.

## Plan

Single file, single commit (bundled with the plugin.json patch bump already staged).

1. `plugins/up/commands/e.md` — add `## Arguments` section clarifying: optional arg names the target; if omitted, infer from the most recent open topic and state which one was picked. Add a rule for the genuinely-ambiguous case (ask once instead of guessing) instead of silently guessing.
2. No other files change. Version bump (`0.3.20` → `0.3.21`) already applied to `plugins/up/.claude-plugin/plugin.json`.

Order: edit e.md, re-read for consistency, done — no dependencies.

## Verify

- Read the final `e.md` cold: does it stand alone without the conversation that produced it (no conversation-bleed)? Yes — content generalizes; no reference to "the user said X".
- Structural check against `try.md`/`step-back.md`/`make.md`: frontmatter present, `# /up:e` title, numbered `## Process`, `## Rules`. Consistent.
- Argument-handling check: explicit fallback for no-argument case, explicit rule for ambiguous case — was the one gap in the first draft, now closed.

## Code smells
None found.

## Conclusion
`/up:e` added: explains a target (named by argument, or inferred from the most recent open topic if omitted) in one terse message, then names — but doesn't answer — 1-3 follow-up threads. Matches sibling command structure (frontmatter, `# /up:e` title, numbered process, rules). Bundled with the plugin.json patch bump to `0.3.21`.

Deviation from the original two drafts: added an explicit `## Arguments` section and an ask-once-if-ambiguous rule — the earlier drafts silently assumed "whatever follows the command, or the thing under discussion" without saying what to do when neither is clear.

Second pass caught a correctness gap: the process went straight from "assume vague recall" to "pick the depth" without ever telling the agent to look at the actual target first — risked confidently explaining from stale memory. Added a "Ground it" step ahead of everything else, split it from the audience-calibration step (different concerns), and cut a Rules bullet that just restated the "write it" step verbatim.
