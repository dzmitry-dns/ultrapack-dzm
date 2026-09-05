# ujira — comments post without approval

**Status:** validating — pack side landed on `main` at v0.3.32; the dogfood gate below is open
**Branch:** main
**Goal:** In a project configured with `apply: mcp` + `auto: comment`, a `/up:make` run that crosses a drafting transition posts its phase comment to Jira unattended and records it in the `**Jira:**` header, while the ticket transition and any description rewrite still reach the owner as proposals. In a project without `auto`, behavior is byte-identical to v0.3.31.

## Design

The owner's complaint: the draft-then-approve ritual costs more attention than the comment is worth. A phase comment is one plain-language line whose whole job is to keep a board reader oriented. Reading it, approving it, then pasting it is three interactions for a sentence nobody disputes.

The gate was not built because comments are risky. It was built because the Jira MCP was read-only in this setup (`docs/roadmap.md` audit, 2026-07-20) — draft-then-approve was the only shape that could work. That constraint is gone: user-scope settings now allow `mcp__claude_ai_Atlassian_Rovo__*`, writes included. What remains is a design question rather than a capability one.

Asymmetry is the answer, not a global switch:

- A **comment** is additive and reversible. A wrong one is edited or deleted in Jira in seconds, and nothing downstream depends on it. Safe to send unattended.
- A **transition** moves the ticket for the whole team, and in this owner's process QA closes tickets — an agent asserting board state is the failure mode the gate exists for.
- A **description** overwrites prose a human wrote. Silent replacement destroys work.

So `auto` is a per-item opt-in whose only honored value is `comment`, and the two dangerous items are not expressible in it.

Two smaller decisions:

- The comment posts **before** the block is presented, and renders as a receipt (`Comment (posted):`). Showing it as a proposal that was already applied would train the owner to ignore the block.
- The sync annotation updates the moment the post succeeds, decoupled from the rest of the block. The owner can abandon the block; a comment that landed without being recorded is a duplicate next run. This is the one real bug the feature can introduce, so the rule is stated where the annotation is defined and again in the `auto` section.

Rejected: a global `apply: auto` covering every item. It would collapse the asymmetry above into one flag and put transitions one typo away from automation.

### Prior art

- `jira-adapter.md` — shipped the draft-then-approve core (5053d48, v0.3.27). Its Design fixed the thin-layer contract, which this change deliberately does not touch: automation makes the contract matter more, not less, since no owner reads the text before it lands.
- `ujira-polish.md` — established that bare `- key: value` lines are the sole config parse target. `auto` follows that form, so no parser change is implied.

## Plan

### 1. `plugins/up/skills/ujira/SKILL.md`

- Frontmatter description + intro paragraph: state the bounded-automation model instead of "never writes without approval".
- Config section: document the `auto` key next to `apply`; show it in the sample block.
- New `## auto: comment — comments post unattended` section after Apply modes: the rationale, the four-step per-comment procedure, the `apply: manual` contradiction, MCP-failure handling.
- Triggers section: annotation updates on a landed auto comment, not only on owner response.
- Draft block section: `Comment (posted):` rendering and what it means.
- Rules: the single exception, plus an absolute for transitions and descriptions.
- Terminal state: mention posted comments.

### 2. `plugins/up/commands/make.md`

- Step 7 (line 112) and step 12 (line 147): the pause carries what is left after auto-apply; auto-applied items appear as receipts.

### 3. `README.md`, `plugins/up/.claude-plugin/plugin.json`

- Skill one-liner; version 0.3.31 → 0.3.32.

### 4. `docs/roadmap.md`

- Line 23 asserted the Jira MCP is read-only. Stale — correct it in this change rather than leaving a doc that argues against the feature.

### 5. Consumer — `cccc-monorepo/CLAUDE.md`

- `apply: manual` → `apply: mcp`; add `auto: comment`; rewrite the surrounding prose, which described the manual flow in four places.

### Rollout / Verification

- Config-shape check: the `## Jira adapter` section in the consumer still parses as bare `- key: value` lines.
- Write path is reachable: user-scope settings allow `mcp__claude_ai_Atlassian_Rovo__*` (verified 2026-08-02), so no permission prompt stands between the skill and `addCommentToJiraIssue`.
- Real proof needs a dogfood run: the next `/up:make` in cccc that crosses a transition should post one comment, show it as a receipt, and leave the transition as a proposal.
- Reinstall to 0.3.32 before the dogfood — the marketplace serves `dzmitry-dns/ultrapack-dzm`, so the change is not live until push + update.

### Rollback

Delete the `auto` line from the consumer `CLAUDE.md`. The key is opt-in and absent means the old behavior, so no pack revert is needed to stop auto-posting.

## Verify

Done in-repo (doc-only change; install-and-invoke is the only local proxy):

- Consistency sweep over the whole diff for surviving absolutes. Two contradictions found and fixed in this change: the SKILL.md sample config paired `apply: manual` with `auto: comment`, which the same file calls a config error — the copy-paste template was the one invalid combination; and `docs/roadmap.md:88` still carried "MCP is read-only for writes by policy" as the adapter's live rationale after line 23 was corrected, so the file argued with itself.
- Shipped task files left as history, not edited: `jira-adapter.md` (Goal, IV1, Conclusion IV1) states "nothing reaches Jira without approval" unscoped, which now reads as a live contract to anyone arriving via `### Prior art`. A dated `### Follow-up` in that file's Conclusion is the blessed fix if it bites. `ujira-polish.md` IV2 is scoped to targeted description updates, which stay gated — still true.
- Installed plugin updated to 0.3.32 and checked by fact, not assumption: `installed_plugins.json` reports the version and the installed `SKILL.md` carries the `## auto: comment` section.

### Open gate — one live dogfood run

Status stops at `testing` until the next `/up:make` in cccc that crosses a drafting transition, where all four must hold:

1. Exactly one comment lands on the ticket — not zero, not a duplicate of a prior run's line.
2. It is rendered in the draft block as `Comment (posted):`, a receipt, not a proposal awaiting approval.
3. The ticket transition is still presented as a proposal and does not move until the owner approves it.
4. The `**Jira:**` header annotation advanced the moment the comment landed — the duplicate-on-next-run bug is the one this feature can actually introduce.

Not gating, but worth watching: the auto-post must not raise a permission prompt. It clears today only because user-scope `~/.claude/settings.json` grants `mcp__claude_ai_Atlassian_Rovo__*`; cccc's project-level `permissions.allow` lists Atlassian read tools only. Narrowing that wildcard makes every auto comment prompt until the project list names the write tool explicitly.

Consumer side is not in this task: cccc's `## Jira adapter` section moved to `apply: mcp` + `auto: comment` and sits uncommitted on `feat/conversation-rate-limit` there. It commits in that repo, with that feature.

## Conclusion

<!-- filled after the dogfood run -->
