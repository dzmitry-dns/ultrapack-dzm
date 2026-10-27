# Post-check reminders

**Status:** reviewing
**Branch:** main
**Goal:** When a `/up:make` task ends with a check that needs a later date, the agent proposes the calendar reminders itself and, after the owner's yes to that list, creates them in the owner's Google Calendar "Work" through the Notion calendar tools and records them in the task file; a project or user with no reminders config sees no change. Confirming it needs one live run in a real project (cccc) where a task reaches `validating` with a dated check.

## Owner summary
- Done: <empty: rewritten by /up:summary step 3 in plain English, no IDs>
- Left: <empty>
- Owner decides: <empty>

## Design

Today the owner asks by hand, at the end of a session, for a Google Calendar reminder to re-check a result after a release (one-off or a series, e.g. CATS-1837 got 8 daily events). The pack already has the right moment: `/up:make` step 11 hands the owner the steps it cannot finish and keeps Status `validating` (`plugins/up/commands/make.md:163`). Nothing there proposes a reminder, and the "how" lives only in a cccc memory note that still says the Notion calendar path fails.

Owner decisions, 2026-10-27: the trigger goes into the pack (step 11) plus one global rule; events are created through the Notion calendar tools (the owner connected Google Calendar in Notion the same day; `notion-calendar-list-calendars` now lists "Work" with `writeEvents: true`).

Chosen shape, mirroring `up:ujira`'s opt-in config:

1. **Config lives with the owner, not the pack.** A `## Reminders` section in `~/.claude/CLAUDE.md` holds: the tool (`notion-calendar-create-events`), the target calendar (account id + calendar id of "Work"), the time zone, defaults (11:00, 15 minutes, no guests), the event text shape, and the Chrome fallback (prefilled `calendar.google.com/calendar/r/eventedit` link) for when the Notion tool errors. The section also states the rule outside `/up:make`: whenever I hand the owner a check that needs a later date, I offer reminders the same way.
2. **Trigger lives in the pack.** `/up:make` step 11, the `validating` branch, notes that a remaining step is tied to a date or a period (after a release, after N days, daily for a week). When the loaded instructions have a `## Reminders` section, step 12 asks for the reminder list (date, time, title, what to check) as its own question after the merge answer, with dates counted from the release that answer names (or from today when nothing merges). The merge question stays merge-only (`make.md:181`). The reminder question, event creation and the `Reminders:` record all run before step 12's "Leaving a plain branch / Leaving a worktree" sequence, so the record is committed with the task file where it lives (the branch inside a worktree) before exit step 2 copies it (`make.md:192`). No section → no proposal, no tool call.
3. **Owner approves the list itself.** Events are created only after a yes that answers the reminder question; a yes to the merge, the plan, or a longer list does not count. The owner may edit dates in the reply.
4. **Record in the task file.** After creation, one `Reminders:` line per event goes into `## Conclusion` (date, time, title, event id). A resumed `validating` task reads it and does not propose again; when the Goal is confirmed early, the agent offers to cancel the remaining events.
5. **Event text.** Title `<ticket or slug>: <what to check>`; description says what to look at and where, and ends with the resume prompt `/up:make docs/tasks/<slug>.md` and the repo name, so the event alone is enough to start the check.
6. **Periodic checks.** Same check repeated → one event with an RRULE (`recurrenceRules`, e.g. `FREQ=DAILY;COUNT=7`); different checks per day → separate events.
7. **cccc memory note** `feedback_calendar-via-api.md` is rewritten to point at the global section, so a cccc session stops going straight to Chrome.

Rejected: a new pack skill for reminders (one paragraph in step 11 plus the global section is enough; YAGNI); owner's calendar ids in the pack (other users of the fork would write into nothing, and ids are personal).

Backwards compatibility: no break. Additive text; a user or project without `## Reminders` gets a byte-identical flow (same rule as `up:ujira` → no config, silent no-op).
TDD: no (reason: doc-only pack, no runtime code; verification is a live tool call and an install-and-invoke run)
Reviewed before code: 2 rounds, 2 Critical/Important fixed, 0 rejected, 2026-10-27

### Prior art
- `plugins/up/skills/ujira/SKILL.md:15`, `:137`: opt-in config section in `CLAUDE.md`, silent no-op without it; the same shape is reused here.
- `plugins/up/commands/make.md:163`: step 11 already hands remaining checks to the owner; the trigger attaches there.
- `~/.claude/projects/-Users-svirins-dev-current-cccc-monorepo/memory/feedback_calendar-via-api.md`: owner defaults (Work, 11:00, 15 min, no notification, no guests) and the Chrome prefilled-link fast path.
- No task in `docs/tasks/` covers reminders.

### Invariants
- IV1: Without a `## Reminders` section in the loaded instructions, `/up:make` makes no reminder proposal and no calendar tool call.
- IV2: No calendar event is created before the owner's yes to the reminder list itself.
- IV3: Every created event is recorded in the task file with date, time, title and event id (`event chrome (no id, cancel by hand)` on the fallback path), and the record is committed in the same step.
- IV4: Owner-specific values (account id, calendar id, time zone, defaults) appear only in `~/.claude/CLAUDE.md`, never under `plugins/up/`.
- IV5: Existing `/up:make` steps and resume of older task files keep working unchanged.

### Assumptions
- AS1: `notion-calendar-create-events` with the Work `accountId` + `calendarId` writes the event into "Work" in Google Calendar.
- AS2: The Notion calendar connection stays connected between sessions.

### Unknowns
- UK1: The create tool has no notification field; whether an event created through it carries the Work calendar's default notification, against the owner's "no notification" default. Resolve in verify with one test event.
- UK2: Whether `list-events` returns the event id needed for a later cancel, or only `create-events` does.

## Plan

Approach: one opt-in paragraph in `/up:make` step 11 plus a resume guard, and the owner-specific config as a `## Reminders` section in the global instructions; the two halves meet only by that section name, like `up:ujira` and `## Jira adapter`.
Reviewed before code: 1 rounds, 2 Critical/Important fixed, 0 rejected, 2026-10-27, round 2: not needed

### PH1: Pack trigger

- **1.1** `plugins/up/commands/make.md:167-169` (modify), step 11
  - New paragraph `**Reminders.**` after the "If the Goal is still pending" paragraph (line 167), before "Once `done`" (line 169). Content: when the loaded instructions have a `## Reminders` section and a remaining step of the `validating` bullet (line 163) is tied to a date or a period, step 12 asks for a reminder list (date, time, title, what to check) after the merge answer, as its own question, with dates counted from the release that answer names (from today when nothing merges); events are created per that section only after a yes that answers this question; each created event gets one `Reminders: <date> <time>, <title>, event <id>` line in `## Conclusion` (`event chrome (no id, cancel by hand)` on the fallback path), and a declined list gets `Reminders: declined <date>`; the question, the events and these lines come before "Leaving a plain branch" / "Leaving a worktree" step 2 and are committed with the task file, so the branch copy carries them (`make.md:192`); when the Goal is confirmed while recorded events are still ahead, offer to cancel them. No such section → no list, no calendar tool call.
  - Respects: IV1, IV2, IV3, IV4 (no ids, calendar or tool names beyond the section name), IV5
- **1.2a** `plugins/up/commands/make.md:181` (modify), step 12, after the merge-question paragraph
  - One sentence: the reminder question of step 11 comes after the merge answer, never inside the merge question.
  - Respects: IV2
- **1.2** `plugins/up/commands/make.md:33` (modify), step 2 resume list, `validating` entry
  - Append: `Reminders:` lines already in `## Conclusion` (events or `declined`) mean the question was answered; do not propose again.
  - Respects: IV3, IV5
- **1.3** `README.md:58` (modify)
  - One sentence after "hands you the rest": with a `## Reminders` section in your `CLAUDE.md`, the agent also proposes calendar reminders for those checks and creates them after your yes.
- **1.4** `plugins/up/.claude-plugin/plugin.json:3` (modify): `0.3.55` → `0.3.56`.
- Commit: `feat(up): step 11 proposes post-check calendar reminders` (version bump as its own `chore(up): 0.3.56` commit, per repo history)

### PH2: Owner config and memory (outside the repo, no commit)

- **2.1** `~/.claude/CLAUDE.md`, new `## Reminders` section after `## External Services` (ends line 16) (modify)
  - When: `/up:make` step 11 proposes (inside `/up:make` the pack's order and record rules win), and any other session that hands the owner a check needing a later date offers the same list; created only after the owner's yes to the list.
  - How: `notion-calendar-create-events` (load via ToolSearch), calendar `{accountId: 1c6bea2d-5fa2-4c77-921d-1a8824686056, calendarId: dqmoat8bptqgq731nuhsqft42k@group.calendar.google.com}` ("Work", account svirins@gmail.com), `timeZone: Europe/Minsk`, default 11:00, 15 minutes, no attendees.
  - Text: title `<ticket or slug>: <what to check>`; description = what to look at and where, last line the resume prompt `/up:make docs/tasks/<slug>.md` and the repo folder.
  - Series: same check → one event with `recurrenceRules`; different checks per day → separate events.
  - After create: report each event's date and title in one line; record per `/up:make` step 11.
  - Fallback when the Notion tool errors (`calendar_connection_required`, `calendar_request_rejected`, or any other error): one line naming the error, then the Chrome prefilled link `calendar.google.com/calendar/r/eventedit?text=…&dates=YYYYMMDDTHHMMSS/YYYYMMDDTHHMMSS&details=…` (URL-encoded, no `Z`), remove the default notification, pick "Work", Save; such an event has no id and is recorded as `event chrome (no id, cancel by hand)`.
  - Notification line: written from the UK1 result in verify.
  - Respects: IV4, AS1, AS2
- **2.2** `~/.claude/projects/-Users-svirins-dev-current-cccc-monorepo/memory/feedback_calendar-via-api.md` (modify) and its line in that folder's `MEMORY.md`
  - Rewrite: the global `## Reminders` section is the one home; Notion tool works since 2026-10-27; keep only the dated history lines that explain why Chrome is the fallback.

### Test strategy
none (doc-only change). Verify runs one live check: create one test event in "Work" through the tool with the config's values, read it back with `notion-calendar-list-events` (AS1, UK2), check its notification in Google Calendar (UK1), then cancel it with `notion-calendar-cancel-events`. One event, created once.

### Risks
- RK1: The agent proposes reminders for every `validating` task, including ones with nothing dated; the paragraph limits the trigger to a remaining step tied to a date or a period.
- RK2: The Notion connection drops (AS2); the Chrome fallback in 2.1 covers it.

### Rollout
Push to `main`, then `claude plugin update up@ultrapack`; sessions started before the update keep 0.3.55. The global section takes effect in every new session at once.

## Verify

Passed, 2026-10-27, one live event.
- First try: `notion-calendar-create-events` answered 403 `restricted_resource`; `notion-get-tool-access` exposed only list tools. The owner reconnected the Notion connector in claude.ai; tool access then listed create, update and cancel as available. The 403 and its fix went into the global section's fallback bullet.
- AS1 held: test event `9c5337c5956949d2ace7ba1f19190e68` created in "Work", 2026-10-28 11:00-11:15 +03:00 (Europe/Minsk). Google Calendar's event page showed calendar Work, the time, the two-line description with the `/up:make` line on its own line.
- UK1 resolved: the event page showed no notification (only "Add notification"); the global section now states it.
- UK2 resolved: both `create-events` and `list-events` return the event id.
- Cancel: `notion-calendar-cancel-events` removed it; a re-read of 10:59-11:01 shows only the owner's two real Work events.
- IV1, IV2, IV3, IV5 are text rules in `make.md`; their live check is the Goal's cccc run. IV4: `grep` for the account id and calendar id under `plugins/up/` is part of review.

## Conclusion
<empty: filled by up:ureview>
