# Jira Adapter — draft-then-approve Status sync

**Status:** planning
**Branch:** jira-adapter
**Goal:** In a Jira-configured consumer project, an /up:make run whose task crosses a drafting transition produces a correct thin-layer Jira draft (description = 1-2 sentence what+why + acceptance checklist + task-file pointer; comment = one plain-language line per phase) handed to the owner for approval, and nothing reaches Jira without that approval; in unconfigured projects the flow is byte-identical to today. Full confirmation needs a dogfood run in the owner's Jira-configured project (cccc, real CATS ticket) — install-and-invoke in this repo is only the local proxy.

## Design

Purpose: keep Jira human-readable and current with near-zero owner effort — the workflow drafts thin Jira updates at meaningful Status transitions, the owner approves, nothing is ever auto-written.

Chosen approach: a new process skill `up:ujira` (`plugins/up/skills/ujira/SKILL.md`) owns the whole draft contract — thin-layer format, transition coalescing, config discovery, output format, approval protocol. `make.md` gets two one-line trigger hooks. Rationale: single home per the T2 SSOT principle, `make.md` stays lean after T2 just shrank it, and the skill stays manually invocable (`/up:ujira`) for transitions that happened outside make.

Alternatives rejected:
- Inline steps in `make.md` — no new surface, but duplicates the draft contract across trigger points, bloats make.md, not invocable standalone.
- Hook automation (PostToolUse on task-file writes) — catches transitions outside make, but violates the repo's doc-only principle (hooks are runtime code) and risks noise.

Trigger set — two drafting moments per session, each coalescing all undrafted transitions since the last draft:
1. Status → `executing` (rides the existing plan-approval pause): ticket transition proposal to In Progress + one start comment + description (re)draft if the ticket description doesn't yet match the thin contract.
2. Terminal pause (make step 12 finish menu / session end): one plain line per phase crossed since the last draft (validating, done, shipped) + ticket transition proposal when done/shipped.
Mid-flow enum churn (design → planning → executing within one sitting) never drafts on its own — Jira readers care about started / awaiting validation / shipped, not internal stages.

Draft output: one chat block per ticket, copy-paste-ready (plain text that Jira renders as-is), itemizing each action — transition, comment(s), description replacement. Owner responds approve / edit / skip per block. Apply mode comes from consumer config: `manual` (default — owner pastes into Jira; the agent never writes) or `mcp` (agent applies via the Atlassian MCP only after explicit approval of that specific draft).

Config contract: a `## Jira adapter` section in the consumer project's CLAUDE.md (project key, site URL, apply mode). Task-to-ticket linkage stays per-task in the `**Jira:**` header. Discovery: the skill reads consumer CLAUDE.md; missing config section or missing header ⇒ silent no-op.

V1 scope cut: linked tickets only. If config exists but the task lacks a `**Jira:**` header, one-line prompt at task creation to paste a ticket id or skip. Ticket-creation drafting is parked as follow-up.

TDD: no (reason: doc-only pack, no runtime code; verification is install-and-invoke smoke).

### Prior art
- `docs/tasks/t2-template-realignment.md:15` — census made `**Jira:**` an official optional header (49+10 files); the linkage slot this adapter reads.
- `docs/tasks/t2-template-realignment.md:63` — the template block in `make.md:48` carrying the `**Jira:**` slot.
- `docs/roadmap.md:88` — the T3 roadmap item defining the thin-layer contract and the draft-then-approve constraint.

### Invariants
- IV1 — Nothing reaches Jira without explicit per-draft owner approval; in `manual` apply mode the agent never writes to Jira at all.
- IV2 — Drafts obey the thin-layer contract: description = 1-2 sentence what+why + acceptance checklist + task-file pointer; comment = one plain-language line per phase; no Design/Plan IDs, no file:line, no technical internals.
- IV3 — All adapter config lives in the consumer project's CLAUDE.md; the pack ships no project keys, site URLs, or ticket ids.
- IV4 — Without config or without a `**Jira:**` header the flow is byte-identical to today: zero added prompts, zero output.
- IV5 — Doc-only: the adapter is a markdown skill plus make.md hook lines; no `hooks/` entries, no scripts.

### Principles
- PC1 — Drafts surface only at existing user-decision points (plan approval, finish menu); never a new mid-autonomous-flow interrupt.
- PC2 — Coalesce: one draft covers all undrafted transitions; never more than two Jira pauses per session.

### Assumptions
- AS1 — Consumer projects reach Jira through the Atlassian MCP for reads (fetching current ticket state before drafting); write availability varies and is never required.
- AS2 — One ticket per task file via the `**Jira:**` header is enough linkage; epics map through their children (`overview.md` at `reference` never drafts).
- AS3 — Owner-approval latency is acceptable — no requirement for real-time Jira mirroring.

### Unknowns
- UK1 — Exact config key names and section title for consumer CLAUDE.md (settled in plan).
- UK2 — Whether description drafts should merge with human-written ticket text or replace wholesale (settled by dogfood on a real ticket; V1 default: present a replacement, owner edits before applying).
- UK3 — Standalone skill invocations (e.g. `/up:uplan` run directly) cross transitions without drafting; acceptable while dogfood is make-driven — revisit if it bites.

## Plan
<empty — filled by up:uplan; gains ### Rollout / ### Rollback when the change ships to a live system>

## Verify
<empty — filled by up:uverify>

## Code smells
<empty — file:line + one-line smell passed while exploring and left unfixed (out of scope, non-trivial); deleted if none>

## Conclusion
<empty — filled by up:ureview; after done/shipped grows dated ### Follow-up — <date> / ### Scope change — <date> entries and ### Deferred scope-parking>
