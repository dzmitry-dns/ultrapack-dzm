# ultrapack-dzm fork roadmap

Why this fork: the upstream pack (btseytlin/ultrapack, forked at v0.3.22, `main == upstream/main`) is used daily on cccc-monorepo, but (1) predates current Claude Code harness primitives, (2) is tuned to the upstream author's ML profile rather than a web+Jira profile, and (3) its template drifts from how 157 real task files are actually written. This file is the working plan.

**How to continue:** a fresh session reads this file, resolves the Open questions with the owner if still open, then drives tracks in the stated order via `/up:make` (one task file per track item or coherent batch).

## Audit findings — pack side (2026-07-20, full-pack read)

- **Stale model pins.** Agents pin `opus`/`sonnet`/`haiku` in frontmatter; README names "Opus 4.7"/"Sonnet 4.6". Owner already overrides `up:reviewer` to opus at dispatch time via global CLAUDE.md.
- **Dangling references.** `job-guardian` requires `remote-ssh` and `ml-experiments` skills that don't exist in the pack; `plugin.json` keywords still list `ml`, `data-engineering`.
- **Fragile cross-refs.** Skills reference siblings repo-relative (`plugins/up/skills/_brevity.md`) — unresolvable from cwd when installed via marketplace into another project. Needs `${CLAUDE_PLUGIN_ROOT}` or skill-relative paths.
- **SSOT violations** (pack's own GPC4): reviewer stance duplicated in `ureview/SKILL.md` + `agents/reviewer.md`; dispatch contract in `uexecute` + `implementer.md`; hands-off deltas in `handsoff` + every stage skill. Every change touches 4-7 files.
- **Harness drift.** `uexecute` (~345 lines) hand-describes topo-sort/wave dispatch in prose; TodoWrite instead of TaskCreate/TaskUpdate; manual `git worktree add` instead of EnterWorktree; udesign wants multiple-choice questions but doesn't name AskUserQuestion.
- **No bug entry.** `/up:make` is always feature-shaped; `udebug` standalone.
- **ML slant.** GPC4 examples, pod-shaped job-guardian (270s cadence justified by a 5-min cache TTL that no longer holds), vague UI smoke.
- **No pack QA.** Doc-only with no lint; version bumps on the honor system.

## Audit findings — cccc-monorepo reality (2026-07-20, two subagent sweeps)

Config layer (`.claude/rules/workflow.md` + settings):

- Owner hand-built what the pack lacks: mandatory `docs/tasks/archive/` consultation before Design + required `### Prior art` subsection; SessionStart hook printing branch/commits/active tasks/archive index; `**Jira:**` header convention; hard plan-approval gate (3+ files, DB migration, or new API surface); Context7-first mandate.
- Jira MCP is effectively **read-only** (allow: getJiraIssue/searchJiraIssuesUsingJql/getTransitions; no addComment/editIssue) — any Jira automation must be draft-then-approve.
- `dippy` PreToolUse hook (global) auto-approves safe Bash; mutating git (`push`/`reset`/`rebase`) stays ask-tier — agents can stage/commit/branch autonomously but not rewrite history or push.
- Local `workflow.md` template omits `## Verify` and fixes a 5-status enum — both already contradicted by real files (Verify appears in 99 files; statuses overflow the enum). The plugin should own the template; the rule doc should shrink.
- Verify recipe for this stack: `bun type-check` + `bun test:unit` + `bun run build` + local dev smoke; integration needs the `ats2025_test` DB; E2E is Playwright. Turborepo + bun, Next.js 16 / React 19 / tRPC 11 / Clerk, Fastify 5 APIs, Prisma 7.

Task-file census (157 files, ~124 archived):

| Signal | Data | Implication |
|---|---|---|
| `### Prior art` | **107 files** — biggest non-template section | promote to template + udesign step |
| `### Rollback` / `### Rollout` | 91 / 73 | promote to Plan template slots |
| `**Jira:**` header | 49 (+10 URL variants) | bless header + slug conventions (`cats-<num>-*`) |
| `**Depends on:**` | 28 | bless header |
| `**Mode:** hands-off` | **0 of 82** (and `### Hands-off decisions` used once) | hands-off mode has zero adoption — candidate cut |
| `**Worktree:**` | ~always `none` | isolation happens via branches — field/flow candidate cut |
| `### Interfaces` / `### Interface graph` | **4-6 of 157** | wave machinery barely used — demote, shrink uexecute |
| Real CK attack lists in `## Verify` | 23 of 99 | verify protocol too heavy → perfunctory `Result: passed` elsewhere; needs a light tier |
| Status header | enum + freeform ship-log ("merged PR #294 + 5-DB rollout complete…"; `testing`, `shipped`, `reopened`, `reference`) | bless `<enum> — <annotation>`; model merge/deploy-gated terminal reality |
| `### Deferred (needs user input)` | 0 exact uses; ~20 freeform `### Deferred → CATS-xxxx` | the real need is scope-parking to other tickets, not a user-input gate |
| Post-done creep | `### Follow-up (post-merge)`, `### Scope change — <date>`, review tables | Conclusion needs a blessed dated post-merge log |
| Epics | `messaging/` (25 files + overview), `PHASE-1..4` dirs, plan/summary splits | one-file-per-task breaks for epics — bless a folder convention |

## Guiding principles

1. **Core untouched:** task file as SoT, ID system (IV/PC/AS/UK/PH/RK/CK), independent no-rationale reviewer, adversarial verify stance, `_brevity`.
2. **Prose must not imitate runtime.** Where the harness has a deterministic primitive, use it; prose keeps judgment.
3. **Data over doctrine.** The template follows observed usage (157-file census), not aspiration. Features with ~0 adoption get cut or demoted, not documented harder.
4. **The owner's profile is first-class** — web stack, Jira, bun/Playwright smoke — not tape in global CLAUDE.md.

## Open questions (owner decisions, resolve before T2)

1. **Cut hands-off mode from the main flow?** Zero adoption in 82 files. Cutting removes the `handsoff` skill + per-stage deltas (large simplification). `job-guardian` would inline its own autonomy contract. Recommendation: cut.
2. **Worktrees:** default off in `/up:make` step 6 (census: always `none`)? Keep the skill for on-demand use? Recommendation: default off, keep skill.
3. **Interface graph:** cut entirely vs. move to an optional reference file? Recommendation: move out of `uexecute` mainline into a reference; revisit cutting after 2-3 months of fork usage.
4. **job-guardian:** keep (pod/training-shaped; owner's work is web)? Could re-shape toward "babysit a deploy/migration". Recommendation: keep but de-ML the examples in T1.

## Tracks

### T0 — Fork governance
- [ ] Own marketplace identity in `.claude-plugin/marketplace.json` (owner, repo URL). Installing from the fork requires uninstalling the upstream marketplace first (plugin name `up` collides).
- [ ] Policy: generic fixes PR'd upstream; opinionated features stay in fork; periodic cherry-pick from upstream.
- [ ] Reinstall daily driver from this fork; verify `/up:make` loads.

### T1 — Reliability quick-wins (one batch, mostly upstreamable)
- [ ] Model policy (owner is on a **Max 5x** subscription — quota-aware): spend where independent judgment pays, mechanics cheap, main-line follows the session model so one `/model` knob controls daily burn.
  - `implementer` — no pin, inherits session model.
  - `reviewer` — pin `opus` (highest-leverage tokens; obsoletes the owner's dispatch-time override).
  - `implementer-sonnet` — `sonnet`, `explorer` — `haiku`, `researcher`/`summarizer` — `sonnet` (unchanged).
  - Never pin Fable/Mythos-tier in the pack — per-session user choice only.
  - Kill inlined model names in README/prose; frontmatter is the only home for model choice.
- [ ] Fix cross-file refs (`${CLAUDE_PLUGIN_ROOT}` or skill-relative).
- [ ] Remove dangling `remote-ssh`/`ml-experiments` refs from job-guardian (inline the needed minimum); de-ML its examples; fix the stale 270s cache-TTL rationale (cadence matches what's being watched).
- [ ] README refresh (models, fork install path), `plugin.json` keywords cleanup.

### T2 — Template & flow realignment (data-driven; biggest value)
- [ ] Template additions: `### Prior art` (+ udesign step: consult `docs/tasks/archive/`, cite file:line or "none found"), `### Rollback` + `### Rollout` in Plan, `**Jira:**` + `**Depends on:**` headers.
- [ ] Status realism: bless `**Status:** <enum> — <freeform annotation>`; extend terminal lifecycle to model merge/deploy-gated reality (e.g. `validating` → `shipped`), align resume-check in `/up:make`.
- [ ] Conclusion: blessed dated post-merge log (`### Follow-up — <date>`, `### Scope change — <date>`); task files are living changelogs in practice.
- [ ] Repurpose `### Deferred` as scope-parking (`→ <ticket>`); drop the user-input-gate framing (dies with hands-off).
- [ ] Verify tiering: Small tasks get CK-lite (e.g. ≥3 attacks + smoke, one screen) so adversarial verify happens at all; full protocol for Medium+. Census shows heavy protocol → perfunctory skips.
- [ ] Epic convention: bless feature folders (`docs/tasks/<epic>/` with `overview.md`, `Status: reference`) for multi-task workstreams.
- [ ] Execute per Open questions 1-3: cut hands-off, worktree default off, interface graph out of `uexecute` mainline. Shrink `uexecute` accordingly.
- [ ] Fold the SSOT dedup here (single home for reviewer stance, dispatch contract) — it's the same files being rewritten anyway.

### T3 — Daily-driver features
- [ ] **Jira adapter:** on Status transitions, *draft* the thin-layer Jira update (description = what+why + acceptance + task-file pointer; comment = one plain line per phase) and hand to the owner for approval — MCP is read-only for writes by policy. Config in project CLAUDE.md.
- [ ] **Requirements-review:** optional second dispatch in `ureview` — verbatim original requirement + BASE_SHA/HEAD_SHA only; auto-suggested for Medium+. Fold `~/.claude/agents/requirements-reviewer.md` into the pack.
- [ ] **Project verify recipe:** `uverify`/`/up:make` read a per-project smoke recipe (cccc: `bun type-check`, `bun test:unit`, `bun run build`, dev smoke; integration gated on test DB; UI via Playwright/chrome MCP click-through) instead of guessing.
- [ ] **Plan-approval gates as config:** fold cccc's "3+ files / DB migration / new API surface ⇒ plan approval" into `/up:make` as a project-configurable gate; shrink `workflow.md` accordingly.
- [ ] **Bug entry:** bug-shaped ask → `udebug` takes the Design slot in `/up:make`.
- [ ] **Archive & index:** bless `docs/tasks/archive/`; resume-check reads an index (cccc's SessionStart hook already prints one — reuse the shape).

### T4 — Harness modernization (piecemeal)
- [ ] TodoWrite → TaskCreate/TaskUpdate across skills.
- [ ] udesign clarifying questions via AskUserQuestion.
- [ ] `git-worktrees` on top of EnterWorktree/ExitWorktree (only if worktrees survive Open question 2 as on-demand).
- [ ] Revisit `/up:summary` JSONL-grep hack (keep the command — cross-machine handoff still valuable).
- [ ] uexecute parallel waves → Workflow script **only if** interface-graph usage grows after T2; census says don't build it now.

### T5 — Pack QA (background)
- [ ] Repo-level lint script (not in plugin — "doc-only" stays intact): dangling skill refs, ID conventions, anchors, version-bump check; wire as CI.
- [ ] Dogfood discipline: pack changes go through `/up:make` in this repo.

## Order

1. T0 + T1 in one batch (small edits, immediate reliability).
2. Resolve Open questions → T2 (template realignment; evidence-backed, touches the same files as the SSOT dedup).
3. T3, starting with Jira adapter + requirements-review + verify recipe.
4. T4 piecemeal; T5 in the background alongside.
