---
name: ujira
description: Sync thin-layer Jira updates at task Status transitions. Comments post automatically where the project opted in (`auto: comment`); description edits always wait for owner approval; ticket transitions are never drafted unless the project set `transitions: propose`. Entry paths — invoked by /up:make at its trigger points, or manually via /up:ujira. In a project with no Jira adapter config it is a silent no-op.
---

# Jira adapter

Keeps Jira human-readable with near-zero owner effort: at meaningful Status transitions the workflow produces a thin Jira update. What reaches Jira on its own is bounded by config — by default nothing does, and the owner approves every item; a project can opt comments out of that gate with `auto: comment`. Description edits never leave the gate. Ticket state is not the workflow's to move: transitions are not even drafted unless the project set `transitions: propose`, because on most boards a human (QA, the lead) moves the ticket and a proposal from the agent reads as pressure to do it now. Jira is a thin layer for humans — never a mirror of the task file. The technical record stays in `docs/tasks/<slug>.md`; Jira gets what a teammate skimming the board needs.

## Gate — when to run at all

<required>
Run only when BOTH hold; otherwise exit silently — no output, no prompts:

1. The consumer project's `CLAUDE.md` has a `## Jira adapter` section (config below).
2. The task file has a `**Jira:**` header with a ticket id.

One exception: when config exists but the header is missing, the only permitted output is `/up:make` step 3's one-line prompt for a ticket id (or skip). Epic `overview.md` files at Status `reference` never draft.
</required>

## Config — consumer project's CLAUDE.md

The pack ships no Jira config. Consumers declare it in their project `CLAUDE.md`:

```markdown
## Jira adapter
- project: PROJ
- site: https://org.atlassian.net
- apply: mcp
- auto: comment
```

The section is docs and live config at once: only bare `- key: value` lines are parsed as config. Surrounding prose is welcome, but never wrap a key in backticks or fold it into a sentence — a decorated key is invisible to discovery.

- `project` — required; Jira project key. Sanity-check ticket ids in `**Jira:**` headers against it.
- `site` — optional; base URL for rendering ticket links and MCP site lookup.
- `apply` — optional; `manual` (default) or `mcp`. Absent means `manual`.
- `auto` — optional; which draft items are applied without asking the owner. `comment` is the only honored value and it requires `apply: mcp`. Absent means nothing is automatic, which is the historical behavior.
- `transitions` — optional; `propose` is the only honored value and it puts a ticket transition proposal into the draft at the start and terminal triggers. Absent means transitions are never drafted, never applied, never mentioned.

## Draft contract — thin layer, never a mirror

Description (drafted once; on later triggers compare the live description against this contract):
- 1-2 sentences of what + why, plain language.
- Acceptance checklist — observable outcomes, one line each.
- Pointer to the task file: `Details: docs/tasks/<slug>.md in <repo>`.

Match verdict — three outcomes, never binary:
- Matches → skip: no description item in the draft.
- Stale field only — structure matches but one field is out of date (e.g. an outdated `Details:` pointer) → targeted update: the draft replaces just that field, preserving the human-written what+why and acceptance wording.
- Doesn't match → full replace draft.

Comment: one plain-language line per phase crossed.

Banned in any draft: Design/Plan content, task-file ids (IV/PC/AS/UK/PH/RK/CK), file:line references, code, branch names, commit SHAs, agent or skill names, session narrative.

<good-example>
Comment: "Implementation finished and verified; awaiting final confirmation."
</good-example>

<bad-example>
Comment: "PH2 done — make.md:110 hook landed in a1b2c3d, IV4 holds." — task-file ids, file:line, a SHA, and technical detail no board reader needs.
</bad-example>

## Triggers & coalescing

Two drafting moments per `/up:make` session; each draft covers every transition not yet synced:

1. Status → `executing` — rides the plan-approval pause; when `/up:make` skipped that pause (Small under the gate), auto items still post here and gated items move to the terminal draft. One start comment, a description item per the match verdict (skip / targeted update / replace), and, only under `transitions: propose`, a ticket transition proposal (e.g. To Do → In Progress).
2. Terminal pause — `/up:make` step 12 finish menu, or session end. One comment line per phase crossed since the last sync (validating / done / shipped), plus, only under `transitions: propose`, a ticket transition proposal when done or shipped.

Sync state lives in the `**Jira:**` header annotation: `**Jira:** PROJ-123 — synced executing 2026-07-21`. Update it after the owner approves or skips a draft, and immediately after an auto comment lands — an applied comment the annotation does not know about is a duplicate on the next run. Everything after the recorded enum is not yet synced. Internal churn (design → planning) never drafts.

Manual invocation (`/up:ujira`): same rules — read the header annotation, draft whatever is unsynced, hand over.

## Draft block — what the owner sees

One block per ticket, copy-paste-ready (plain text that Jira renders as-is):

```
Jira draft — PROJ-123 (docs/tasks/<slug>.md)

1. Comment:
   Started work on <plain-language summary>.
2. Description (replace):
   <1-2 sentences what + why>
   Acceptance:
   * <outcome 1>
   * <outcome 2>
   Details: docs/tasks/<slug>.md in <repo>
```

Under `transitions: propose` the block gains a `Transition: In Progress` item (or the terminal state) as its first line; without that key the block never mentions ticket state.

A stale-field-only verdict renders the description item as `Description (update: <field>):` carrying only the replacement line(s) — everything else in the live description stays untouched.

The comment item reads `Comment (posted):` only under `auto: comment`, where it is a receipt rather than a proposal — the text is already on the ticket and the owner is being shown what went out. Without `auto`, it stays `Comment:` and waits like every other item.

Owner responds per block: approve / edit (owner returns corrected text) / skip. After approve or skip, update the sync annotation. An already-posted comment takes no response; an owner who dislikes it edits it in Jira, which is why it was safe to send unattended in the first place.

## Apply modes

- `manual` (default): after approval, output the block for the owner to paste into Jira. The agent never calls a Jira write tool — approval does not change that.
- `mcp`: after approval of a specific draft, apply exactly that draft via the Atlassian MCP write tools and report each action's result. No approval, no write; partial approval applies only the approved items. The one thing that can skip the approval step is a comment under `auto: comment` (below) — `mcp` on its own changes who applies a draft, never whether it was approved.

A targeted update is a fragment, and Jira's description is one field: applying it means splicing the replacement into the live description and writing the field back whole (`mcp`), or editing just that field in the Jira editor (`manual`) — never writing the fragment as the new description.

Reads — fetching the current ticket description and status before drafting — are fine in both modes when an MCP is available. When it isn't, draft from the task file alone and say the ticket state wasn't checked.

## `auto: comment` — comments post unattended

Comments are additive and reversible: a wrong one is edited or deleted in Jira in seconds and nobody acts on it in the meantime. Transitions and descriptions are neither — a transition moves the ticket for the whole team, a description overwrites prose a human wrote. That asymmetry is the entire rationale, so `transition` and `description` are not valid `auto` values: encountering one, ignore it, say so once, and keep that item gated.

With `auto: comment` and `apply: mcp`, per comment:

1. Build it exactly as the Draft contract requires. Automation relaxes nothing — the contract is the only thing between the board and technical noise, and it matters more when no owner reads the text first.
2. Post it via the Atlassian MCP write tool before presenting the block.
3. Render it in the block as a receipt (`Comment (posted):`), never as a proposal.
4. Update the sync annotation the moment the post succeeds, without waiting for the rest of the block to be resolved.

Step 4 is not bookkeeping pedantry: the owner can walk away from the block, and a session that posted a comment but recorded nothing posts it again next run.

The other items still wait for the owner, so a comment can land while its description item (or a proposed transition, where `transitions: propose` is set) is skipped. Accepted by design — the comment reports work that happened, the rest asserts board state the owner owns.

`auto: comment` under `apply: manual` is a config error, not a fallback to silence: `manual` has no write path at all. Name the contradiction once, then hand the comment over as a normal draft item.

A failed MCP write is reported, never swallowed: name the failure, render that comment as a paste-ready proposal, and leave the sync annotation alone — it must not claim a comment that never landed.

## Rules

- Never write to Jira without per-draft approval, with exactly one exception: comments in a project that opted in via `auto: comment`. In `manual` mode never write at all.
- Descriptions always need approval. Transitions are not drafted at all unless `transitions: propose` is set, and even then they need approval. No config value applies either one unattended.
- Never draft outside the contract — when in doubt, it's technical detail: leave it out.
- Config comes only from the consumer project's `CLAUDE.md` — never from the pack, never invented.
- No config or no ticket → silent no-op; the flow must be byte-identical to a Jira-less project.

## Terminal state

Auto comments posted and recorded; remaining drafts handed over; approved ones applied (`mcp`) or delivered paste-ready (`manual`); sync annotation updated. Control returns to `/up:make`.
