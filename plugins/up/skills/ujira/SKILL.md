---
name: ujira
description: Draft thin-layer Jira updates at task Status transitions and hand them to the owner for approval — never writes without it. Entry paths — invoked by /up:make at its trigger points, or manually via /up:ujira. In a project with no Jira adapter config it is a silent no-op.
---

# Jira adapter

Keeps Jira human-readable with near-zero owner effort: at meaningful Status transitions the workflow drafts a thin Jira update, the owner approves, and only then does anything reach Jira. Jira is a thin layer for humans — never a mirror of the task file. The technical record stays in `docs/tasks/<slug>.md`; Jira gets what a teammate skimming the board needs.

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
- apply: manual
```

The section is docs and live config at once: only bare `- key: value` lines are parsed as config. Surrounding prose is welcome, but never wrap a key in backticks or fold it into a sentence — a decorated key is invisible to discovery.

- `project` — required; Jira project key. Sanity-check ticket ids in `**Jira:**` headers against it.
- `site` — optional; base URL for rendering ticket links and MCP site lookup.
- `apply` — optional; `manual` (default) or `mcp`. Absent means `manual`.

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

1. Status → `executing` — rides the plan-approval pause. Ticket transition proposal (e.g. To Do → In Progress), one start comment, and a description item per the match verdict (skip / targeted update / replace).
2. Terminal pause — `/up:make` step 12 finish menu, or session end. One comment line per phase crossed since the last sync (validating / done / shipped), plus a ticket transition proposal when done or shipped.

Sync state lives in the `**Jira:**` header annotation: `**Jira:** PROJ-123 — synced executing 2026-07-21`. Update it after the owner approves or skips a draft; everything after the recorded enum is not yet synced. Internal churn (design → planning) never drafts.

Manual invocation (`/up:ujira`): same rules — read the header annotation, draft whatever is unsynced, hand over.

## Draft block — what the owner sees

One block per ticket, copy-paste-ready (plain text that Jira renders as-is):

```
Jira draft — PROJ-123 (docs/tasks/<slug>.md)

1. Transition: In Progress
2. Comment:
   Started work on <plain-language summary>.
3. Description (replace):
   <1-2 sentences what + why>
   Acceptance:
   * <outcome 1>
   * <outcome 2>
   Details: docs/tasks/<slug>.md in <repo>
```

A stale-field-only verdict renders item 3 as `Description (update: <field>):` carrying only the replacement line(s) — everything else in the live description stays untouched.

Owner responds per block: approve / edit (owner returns corrected text) / skip. After approve or skip, update the sync annotation.

## Apply modes

- `manual` (default): after approval, output the block for the owner to paste into Jira. The agent never calls a Jira write tool — approval does not change that.
- `mcp`: after approval of a specific draft, apply exactly that draft via the Atlassian MCP write tools and report each action's result. No approval, no write; partial approval applies only the approved items.

A targeted update is a fragment, and Jira's description is one field: applying it means splicing the replacement into the live description and writing the field back whole (`mcp`), or editing just that field in the Jira editor (`manual`) — never writing the fragment as the new description.

Reads — fetching the current ticket description and status before drafting — are fine in both modes when an MCP is available. When it isn't, draft from the task file alone and say the ticket state wasn't checked.

## Rules

- Never write to Jira without per-draft approval; in `manual` mode never write at all.
- Never draft outside the contract — when in doubt, it's technical detail: leave it out.
- Config comes only from the consumer project's `CLAUDE.md` — never from the pack, never invented.
- No config or no ticket → silent no-op; the flow must be byte-identical to a Jira-less project.

## Terminal state

Drafts handed over; approved ones applied (`mcp`) or delivered paste-ready (`manual`); sync annotation updated. Control returns to `/up:make`.
