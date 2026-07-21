# T0+T1 — Fork governance + reliability quick-wins

**Status:** validating
**Branch:** t0-t1-batch
**Worktree:** none
**Goal:** Fork owns its marketplace identity and installs cleanly as the daily driver (`/up:make` loads from this fork's marketplace); agents follow the quota-aware model policy with no inlined model names left in prose; no dangling skill refs or repo-relative cross-refs remain; job-guardian is de-ML'd with a truthful cadence rationale; README is a self-sufficient onboarding doc a colleague can install and use the pack from without asking the owner. Confirming install requires a real reinstall in the owner's environment.
**Mode:** interactive

## Design

T0+T1 batch per `docs/roadmap.md` (SoT). Six work areas, all doc edits, no runtime code:

1. **Marketplace identity** — `.claude-plugin/marketplace.json`: keep name `ultrapack` (owner decision — install handle `up@ultrapack` unchanged; upstream marketplace must be removed before adding the fork, same-name collision is inherent). Owner → Dzmitry Sviryn; add fork repo reference. `plugins/up/.claude-plugin/plugin.json`: keywords drop `ml`, `data-engineering`; author stays upstream (credit); version patch-bump on land.
2. **Fork policy** — new short section in repo `CLAUDE.md`: generic fixes are PR'd upstream, opinionated features stay in the fork, periodic cherry-pick from `upstream/main`.
3. **Model policy** — frontmatter is the single home for model choice: `implementer` drops its `model:` pin (inherits session model — one `/model` knob controls daily burn), `reviewer` pins `opus` (obsoletes the owner's dispatch-time override in global CLAUDE.md — flag for the owner to remove it after install), `implementer-sonnet`/`explorer`/`researcher`/`summarizer` unchanged. Kill model names from prose: `uexecute` ("dispatcher, on Opus"; "(Opus)"/"(Sonnet)" labels), `commands/summary.md` ("pinned to Sonnet"), `implementer-sonnet.md` ("re-routes to Opus" → "re-routes to `up:implementer`"), README agent list. The quoted anti-example in `_brevity.md` keeps its model string — it illustrates this very rule. Never pin Fable/Mythos-tier anywhere.
4. **Cross-refs** — all sibling references inside `plugins/up/` switch from repo-relative (`plugins/up/skills/_brevity.md`) to `${CLAUDE_PLUGIN_ROOT}/skills/_brevity.md`: 7 refs in `agents/reviewer.md`, `udesign`, `uplan` (×2), `uexecute`, `uverify`, `ureview`. Uniform choice because agent files get no base-directory preamble, so skill-relative paths can't work there. `uplan`'s illustrative example-plan lines (`@ plugins/up/skills/foo/SKILL.md`) are example content, not refs — untouched.
5. **job-guardian** — remove dangling `remote-ssh`/`ml-experiments` refs (inline the needed minimum: nohup launch, log redirection, connection reuse — one line); de-ML examples toward the owner's profile (deploy, migration, backfill, batch pipeline; training stays as one example among several, not the frame); replace the fixed-270s-cache-TTL cadence law with "pick the cadence from the job's dynamics" (the 5-min cache TTL rationale is stale — current harness TTL is 1h) with a sane default and no fixed-number iron rule.
6. **README for colleagues** — full rewrite as a standalone onboarding doc: what the pack is and why, install from the fork (`/plugin marketplace add dzmitry-dns/ultrapack-dzm`, removing upstream first), quickstart, the task-file lifecycle with the ID system explained, per-skill and per-command reference, agents table (roles, no model versions in prose; one line stating the model policy), fork note pointing upstream. Written for someone who has never seen ultrapack or the roadmap.

Rejected alternative for (4): skill-relative paths (`../_brevity.md`) — works only for skills (they get a base-directory preamble), breaks for agents; a mixed scheme is worse than one variable.

TDD: no (doc-only pack; no runtime code, no test harness — verification is install-and-invoke).

### Invariants
- IV1 — Agent frontmatter is the only place a model name appears normatively; no prose in `plugins/up/` or README names a model (the quoted anti-example in `_brevity.md` is exempt).
- IV2 — No file under `plugins/up/` references a sibling file by repo-relative path; all cross-file refs use `${CLAUDE_PLUGIN_ROOT}` (uplan's example-plan `@` lines exempt as illustrative content).
- IV3 — Plugin name `up`, marketplace name `ultrapack`, and all `up:*` invocation names are unchanged.
- IV4 — No reference to a skill or file that does not exist in the pack (kills `remote-ssh`, `ml-experiments`).
- IV5 — No Fable/Mythos-tier model is pinned anywhere in the pack.

### Principles
- PC1 — README is written for a colleague with zero fork context: no roadmap references, no fork-internal jargon, every workflow concept introduced before use.

### Assumptions
- AS1 — `${CLAUDE_PLUGIN_ROOT}` expands inside installed skill and agent markdown (observed expanding in command args this session; agent files unverified).
- AS2 — The fork repo `dzmitry-dns/ultrapack-dzm` is (or will be made) accessible to colleagues, so the README install path works for them.

### Unknowns
- UK1 — Whether `/plugin marketplace add` of the fork requires removing the upstream `ultrapack` marketplace first (expected yes; confirmed at reinstall).
- UK2 — Whether `${CLAUDE_PLUGIN_ROOT}` expands in agent files specifically; if not, the reviewer agent's `_brevity.md` ref needs the dispatcher to pass the path instead (fallback noted for execute).

## Plan

Approach: four doc-edit phases with disjoint file sets — manifests+policy, pack-wide reference/model hygiene, job-guardian rewrite, README rewrite — dispatched as one parallel wave, one commit each. Verification is grep sweeps + reinstall smoke (no runtime code).

### PH1 — Identity, manifests, fork policy

- **1.1** `.claude-plugin/marketplace.json` (modify)
  - `owner.name` → `Dzmitry Sviryn`; add `metadata` with fork repo URL `https://github.com/dzmitry-dns/ultrapack-dzm`. `name` stays `ultrapack` (IV3).
- **1.2** `plugins/up/.claude-plugin/plugin.json` (modify)
  - `keywords`: drop `ml`, `data-engineering`; `version` → `0.3.23`; `author` unchanged.
- **1.3** `CLAUDE.md` (modify)
  - New `## Fork policy` section: generic fixes PR'd to `btseytlin/ultrapack`; opinionated features stay in fork; periodic cherry-pick from `upstream/main`. 3-4 lines.
- Respects: IV3, IV5.
- Commit: `feat(t0): own marketplace identity, fork policy, keywords cleanup`

### PH2 — Model policy + cross-ref hygiene

- **2.1** `plugins/up/agents/implementer.md:5` (modify) — delete `model: opus` line (inherits session model).
- **2.2** `plugins/up/agents/reviewer.md:6` (modify) — `model: sonnet` → `model: opus`; line 55 `plugins/up/skills/_brevity.md` → `${CLAUDE_PLUGIN_ROOT}/skills/_brevity.md`.
- **2.3** `plugins/up/agents/implementer-sonnet.md:26,111` (modify) — "re-routes to the Opus implementer" / "re-routes to Opus" → "re-routes to `up:implementer`"; description line 3 "but on Sonnet for cost" → "on a cheaper pinned model" (frontmatter `model: sonnet` stays — IV1 lives in frontmatter).
- **2.4** `plugins/up/skills/uexecute/SKILL.md:80,87,88` (modify) — drop "(the dispatcher, on Opus)" model mention and "(Opus)"/"(Sonnet)" labels; line 22 ref → `${CLAUDE_PLUGIN_ROOT}/skills/_brevity.md`.
- **2.5** `plugins/up/skills/udesign/SKILL.md:136`, `uplan/SKILL.md:38,172`, `uverify/SKILL.md:17`, `ureview/SKILL.md:32` (modify) — repo-relative `_brevity.md`/`_principles.md` refs → `${CLAUDE_PLUGIN_ROOT}/skills/...` (IV2; uplan's example-plan `@` lines untouched).
- **2.6** `plugins/up/commands/summary.md:7` (modify) — drop "(pinned to Sonnet)"; keep the "cheaper than the main-session model" rationale without naming a model.
- Respects: IV1, IV2, IV5. `_brevity.md:20` anti-example untouched (IV1 exemption).
- Commit: `feat(t1): model policy in frontmatter only; ${CLAUDE_PLUGIN_ROOT} cross-refs`

### PH3 — job-guardian cleanup

- **3.1** `plugins/up/skills/job-guardian/SKILL.md` (modify)
  - Line 28: delete the `remote-ssh`/`ml-experiments` paragraph; inline the minimum: launch detached (`nohup`/container), redirect output to a log file, reuse SSH connections for remote (IV4).
  - Line 57: drop `(remote-ssh)` ref; keep "confirm the pod/host is reachable".
  - De-ML examples throughout (description line 3, lines 24-26, 39, 119): frame as long-running jobs generally — deploy, DB migration, backfill, batch pipeline, training run as one example among several; recovery playbook examples get generic entries (transient network → retry; disk full → clean + resume; OOM → lower concurrency/batch; hung worker → restart from last good state).
  - Lines 65, 90-92, 134-135: replace fixed-270s + 5-min cache-TTL rationale with: pick the cadence from the job's dynamics (how fast it can go wrong × cost of a late catch), default ~5 min, state the chosen cadence in the contract file; drop the "never stretch or shrink" rule. Keep: timer-wake over Monitor-grep gating, crash-gate first wake shortly after launch.
- Respects: IV4; UK2 n/a here.
- Commit: `feat(t1): job-guardian — de-ML, drop dangling refs, cadence from job dynamics`

### PH4 — README rewrite for colleagues

- **4.1** `README.md` (rewrite)
  - Audience: a colleague who has never seen ultrapack (PC1). Sections: what/why (one paragraph); Install from the fork (`/plugin marketplace remove ultrapack` if upstream present → `/plugin marketplace add dzmitry-dns/ultrapack-dzm` → `/plugin install up@ultrapack` → `/reload-plugins`, verify with `/up:make`); Quickstart (`/up:make ...`, what happens stage by stage); The task file (lifecycle Design→Plan→Verify→Conclusion, Status enum, Goal-gated done, ID system IV/PC/AS/UK/PH/RK/CK with one-line meanings); Skills reference (process + discipline, one line each); Commands reference; Agents (role table, no model names in prose (IV1) + one line: models are pinned in agent frontmatter — review-grade judgment on the top pinned tier, mechanics on cheaper tiers, the default implementer inherits the session model); Hands-off mode; Fork note (upstream credit, fork policy pointer to CLAUDE.md); License.
  - Source of truth for content: the skill/command/agent files themselves, not the old README prose.
- Respects: IV1, PC1, AS2.
- Commit: `docs(t0): README — onboarding-grade rewrite, fork install path`

### Test strategy
Doc-only (TDD: no). Verify stage: `jq .` both manifests; grep sweeps — no `plugins/up/` sibling refs (IV2), no model names in prose outside frontmatter/exemptions (IV1, IV5), no `remote-ssh`/`ml-experiments` (IV4); reinstall + `/up:make` load smoke covers AS1/UK1/UK2 (user-side).

### Order & dependencies
No `[blocks]` edges — all four phases are one parallel wave (disjoint paths). PH4 relies on PH2/PH3 *decisions* (already fixed in Design), not their diffs.

### Risks / rollback
- RK1 — `${CLAUDE_PLUGIN_ROOT}` may not expand in agent markdown (UK2): verify at reinstall; fallback — `ureview` passes the brevity-file path in the reviewer dispatch prompt.
- RK2 — README rewrite drifts from actual skill behavior: implementer derives content from the skill files; reviewer checks claims against them.
- Rollback: single branch `t0-t1-batch`, one commit per phase — revert per-commit or drop the branch.

### Interface graph
- PH1  ->   @ .claude-plugin/marketplace.json, plugins/up/.claude-plugin/plugin.json, CLAUDE.md
- PH2  ->   @ plugins/up/agents/implementer.md, plugins/up/agents/reviewer.md, plugins/up/agents/implementer-sonnet.md, plugins/up/skills/uexecute/SKILL.md, plugins/up/skills/udesign/SKILL.md, plugins/up/skills/uplan/SKILL.md, plugins/up/skills/uverify/SKILL.md, plugins/up/skills/ureview/SKILL.md, plugins/up/commands/summary.md
- PH3  ->   @ plugins/up/skills/job-guardian/SKILL.md
- PH4  ->   @ README.md

Backwards-compat: no consumer-breaking changes — install handle `up@ultrapack` and all `up:*` names unchanged (IV3); model pin changes affect cost only; the owner's global-CLAUDE.md reviewer override becomes redundant (flagged in Conclusion, not edited here).

## Verify

**Result:** passed

Happy-path:
- CK1 — manifests broken by PH1 edits (missing key, invalid JSON) — held: `jq` parses both; loader keys (`name`, `owner`, `plugins[0].source`) intact, version 0.3.23
- CK2 — README names a skill/command/agent that doesn't exist — held: all 23 `up:*` names map to real files; install commands correct incl. remove-upstream step

Negative:
- CK3 — orphaned leftovers survive rewrites (270s/cache-TTL/ML framing in job-guardian; model versions/stale install path in README) — held: only sanctioned mentions remain (RunPod as one-example-among-many, `runpodctl` ×1, `btseytlin` in fork note only)
- CK4 — frontmatter corrupted by pin edits — held: implementer.md valid with no `model:` line; reviewer.md exactly one `model:` line

Invariants / assumptions:
- CK5 (IV1, IV5) — model-name grep outside frontmatter/exemptions — held: zero hits
- CK6 (IV2) — repo-relative sibling refs — held: zero outside uplan's exempt example lines
- CK7 (IV3) — names/handle drift — held: `up@ultrapack`, plugin `up`, marketplace `ultrapack` unchanged
- CK8 (IV4) — `remote-ssh`/`ml-experiments` refs — held: zero hits
- CK10 (AS1) — `${CLAUDE_PLUGIN_ROOT}` precedent hunt — deferred: **no precedent on `main`** (PH2's "existing usage confirms precedent" claim was false — the only 6 usages are ours); expansion in agent files unverified until reinstall (UK2)
- CK11 — README pointers promise content the target file lacks — broke → fixed: README:129 claimed CLAUDE.md documents model overrides + cache-edit rule (both live in the owner's global CLAUDE.md); repointed to Fork policy + Versioning only (`c2e916a`), re-ran — held

Smoke: local proxy only — `jq` both manifests + plugin dir structure resolves; real smoke (marketplace reinstall + `/up:make` loads) is user-side, Goal-gated (UK1, UK2)

Goal: proxy only — manifests/refs/content verified at rest; install-and-invoke from the fork remains for the owner

## Conclusion

Outcome: all T0+T1 edits landed and reviewed merge-ready at `c2e916a`; Goal completes when the owner reinstalls from the fork and `/up:make` loads (UK1/UK2 close there).

Invariants:
- IV1 — grep sweep: model names only in frontmatter + `_brevity.md:20` anti-example (CK5, confirmed by reviewer at HEAD)
- IV2 — grep sweep: no repo-relative sibling refs outside uplan's exempt examples (CK6)
- IV3 — manifests + README: `up`, `ultrapack`, `up@ultrapack`, all `up:*` names unchanged (CK7)
- IV4 — zero `remote-ssh`/`ml-experiments` hits (CK8)
- IV5 — zero Fable/Mythos hits (CK5)

### Assumptions check
- AS1 — unverifiable until reinstall — no `${CLAUDE_PLUGIN_ROOT}` precedent existed on `main` (PH2's "existing usage" claim was false); syntax follows Claude Code plugin docs, confirmed only by install smoke
- AS2 — held — `gh repo view`: PUBLIC, https://github.com/dzmitry-dns/ultrapack-dzm

### Unknowns outcome
- UK1 — still-open — remove-upstream-first documented in README; confirmed at owner's reinstall
- UK2 — still-open — `${CLAUDE_PLUGIN_ROOT}` expansion in agent files; fallback ready (ureview passes the brevity path in the reviewer dispatch prompt) if it doesn't expand

Plan adherence: two consistency-sweep extras beyond listed line numbers, both in-scope — `implementer-sonnet.md:24` header rename (IV1) and PH3 de-ML of lines 33/38/39/80/93 (covered by "throughout"); post-verify fix `c2e916a` (README pointer over-claimed CLAUDE.md contents — CK11).

Review findings: none at confidence ≥80 (reviewer on the new opus pin; sub-80 observations recorded: nonstandard `metadata.repository` manifest key — covered by install smoke; implementer/implementer-sonnet model-equivalence when the session runs a cheap tier — deliberate "one `/model` knob" tradeoff).

Future work:
- Remove the dispatch-time `model: "opus"` override for `up:reviewer` from the owner's global `~/.claude/CLAUDE.md` after reinstall — Justification: Design item 3 (frontmatter pin obsoletes it).
