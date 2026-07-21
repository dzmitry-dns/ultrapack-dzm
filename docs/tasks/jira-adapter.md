# Jira Adapter — draft-then-approve Status sync

**Status:** validating
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

Approach: one new skill file owns the entire draft contract; `make.md` gets three one-line, config-gated touch points that reference it by name; docs and version bump close the branch. Serial, three phases.

UK1 settled — consumer CLAUDE.md config contract (documented in the skill, shipped nowhere):

```markdown
## Jira adapter
- project: CATS
- site: https://<org>.atlassian.net   (optional — link rendering / MCP site lookup)
- apply: manual                        (optional — manual | mcp; absent = manual)
```

Coalescing state (settles "undrafted transitions since last draft" mechanics): the `**Jira:**` header annotation records sync progress — `**Jira:** CATS-123 — synced executing 2026-07-21` — updated after the owner approves or skips a draft; free-text annotation per the T2 status format, no new header.

### PH1 — up:ujira skill

- **1.1** `plugins/up/skills/ujira/SKILL.md` (create)
  - Frontmatter description: invoked from `/up:make` at its trigger points or manually via `/up:ujira`; never self-triggers in unconfigured projects (RK1).
  - Sections: Config discovery (the `## Jira adapter` contract above; no config section or no `**Jira:**` header ⇒ silent no-op — respects IV3, IV4); Draft contract (thin-layer rules + banned content list — IV2); Triggers & coalescing (start draft at Status → `executing`, terminal draft at finish; annotation mechanism above — PC1, PC2); Draft block format (per-ticket copy-paste-ready block: transition, comment(s), description replacement; approve / edit / skip protocol); Apply modes (`manual` — paste-ready output, agent never writes; `mcp` — apply via Atlassian MCP only after per-draft approval — IV1, AS1); Terminal state.
  - Epic rule one-liner: `overview.md` at `reference` never drafts (AS2).
- Commit: `feat(ujira): draft-then-approve Jira adapter skill`

### PH2 — make.md trigger hooks

- **2.1** `plugins/up/commands/make.md:39-50` (modify) — step 3: one line — if consumer CLAUDE.md has a `## Jira adapter` section and the new task has no `**Jira:**` header, prompt once for a ticket id or skip.
- **2.2** `plugins/up/commands/make.md:110-112` (modify) — step 7: one line — on Status → `executing`, if Jira is configured invoke `up:ujira` (start draft rides the plan-approval pause).
- **2.3** `plugins/up/commands/make.md:141-147` (modify) — step 12: one line in the options list — if Jira is configured, present the `up:ujira` terminal draft alongside the finish options.
- Hooks name `up:ujira` and carry zero contract detail (RK2; single home per Design).
- Commit: `feat(make): up:ujira trigger hooks — ticket link, start draft, terminal draft`

### PH3 — docs + version

- **3.1** `README.md:86` (modify) — one bullet after `up:udocument`: draft-then-approve Jira sync, config in consumer CLAUDE.md.
- **3.2** `docs/roadmap.md:88` (modify) — tick the T3 Jira-adapter item.
- **3.3** `plugins/up/.claude-plugin/plugin.json:3` (modify) — version `0.3.26` → `0.3.27` (repo policy: patch bump on landing).
- Commit: `docs(ujira): README + roadmap; bump 0.3.27`

### Risks
- RK1 — Frontmatter description could make Claude invoke `up:ujira` spontaneously in non-Jira projects; mitigation: description names its two entry paths explicitly and the skill opens with the silent no-op gate.
- RK2 — make.md hooks could accrete contract detail over time, recreating the rejected inline option; mitigation: hooks are name-only references, contract lives solely in SKILL.md.
- RK3 — Sync annotation on the `**Jira:**` header could collide with human annotations; mitigation: annotation is free text by T2 convention, `synced <enum> <date>` is short and appended, owner edits freely.

Backwards-compat: greenfield — new skill plus config-gated additive lines in make.md (IV4); no existing consumer behavior changes.

## Verify

**Result:** passed

Happy-path:
- CK1 — Gate's "no output, no prompts" vs make step-3 ticket prompt contradiction — held (explicit exception carve-out in Gate)
- CK2 — terminal draft misread as requiring all three block actions — held (Triggers defines per-draft contents)

Negative:
- CK3 — an unconfigured project sees Jira prompts (IV4) — held (all three make.md hooks config-gated: lines 39, 112, 147)
- CK4 — dangling cross-references (`up:ujira` ↔ make step numbers) — held

Invariants / assumptions:
- CK5 (IV1) — hunt for a write path that skips approval — held (manual: no write tool ever; mcp: per-draft approval gates each write)
- CK6 (IV2) — contract detail leaked into make.md hooks — held (name-only references)
- CK7 (IV3) — real project key shipped in pack — broke: `CATS` in ujira SKILL.md:27,62,71; fixed 06122c9 (neutralized to `PROJ`, swept pre-existing `CATS-1204` in make.md:23); re-run held (grep clean)
- CK8 (IV5) — non-doc artifacts in diff — held (diff = 5 .md + plugin.json version)
- CK9 (AS2/template drift) — sync annotation breaks `**Jira:**` header consumers — held (annotation is free text by T2 convention; resume-check tolerates)

Interfaces:
- CK10 — SKILL.md frontmatter invalid — held (name + description, single-line, parseable)
- CK11 — plugin.json / marketplace.json broken by bump — held (`jq` parses both; marketplace pins no version)

Smoke: structural proxy — manifests parse, frontmatter valid, all refs resolve; real install-and-invoke not run (installed cache is v0.3.26 from GitHub; swap is remove-then-add, disruptive mid-session)

Goal: proxy only — full confirmation needs reinstall of v0.3.27 + a dogfood /up:make run in the owner's Jira-configured project (cccc, real ticket)

## Conclusion

Outcome: adapter landed in pack v0.3.27 (branch head 9b050ec); Goal pending real-world validation — reinstall + a dogfood /up:make run in a Jira-configured project.

Invariants:
- IV1 — CK5: only write path is `mcp` mode after per-draft approval; `manual` never writes.
- IV2 — CK6: contract + banned list single-homed in SKILL.md; make.md hooks are name-only.
- IV3 — CK7: broke (real project key in examples), fixed 06122c9, re-run clean.
- IV4 — CK3: all three make.md hooks config-gated; no config ⇒ zero output.
- IV5 — CK8: diff is 5 .md files + plugin.json version only.

### Assumptions check
- AS1 — unverifiable until dogfood — no Jira MCP exercised in this repo; design never requires writes, reads degrade explicitly.
- AS2 — held for V1 — single-ticket linkage; reviewer's scope flag covers the multi-ticket gap.
- AS3 — held — owner chose draft-then-approve pacing at design.

### Unknowns outcome
- UK1 — resolved — config contract (`## Jira adapter`: project/site/apply) documented in SKILL.md.
- UK2 — still-open — merge-vs-replace for descriptions settles at first dogfood on a real ticket; V1 presents a replacement the owner edits.
- UK3 — still-open, accepted — standalone skill invocations don't draft; revisit if it bites.

Scope flag:
- Sync state persisted as free text inside the identity-bearing `**Jira:**` header couples mutable workflow state to a stable identity slot: a human-edited or absent annotation makes everything recompute as unsynced (re-proposed drafts, backstopped only by owner review), and a multi-ticket task has no room for per-ticket progress. A dedicated structured sync line would be cheaper to add now than to retrofit once consumers depend on the header shape.

Future work:
- Ticket-creation drafting (config present, no ticket yet) — Justification: Design's V1 scope cut, "parked as follow-up".
