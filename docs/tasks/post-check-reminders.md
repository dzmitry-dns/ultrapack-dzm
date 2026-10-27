# Post-check reminders

**Status:** design
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
2. **Trigger lives in the pack.** `/up:make` step 11, the `validating` branch: when a remaining step is tied to a date or a period (after a release, after N days, daily for a week) and the loaded instructions have a `## Reminders` section, propose a reminder list: date, time, title, what to check. No section → no proposal, no tool call.
3. **Owner approves the list itself.** Events are created only after a yes to the reminder list; a yes to the merge, the plan, or a longer list does not count. The owner may edit dates in the reply.
4. **Record in the task file.** After creation, one `Reminders:` line per event goes into `## Conclusion` (date, time, title, event id). A resumed `validating` task reads it and does not propose again; when the Goal is confirmed early, the agent offers to cancel the remaining events.
5. **Event text.** Title `<ticket or slug>: <what to check>`; description says what to look at and where, and ends with the resume prompt `/up:make docs/tasks/<slug>.md` and the repo name, so the event alone is enough to start the check.
6. **Periodic checks.** Same check repeated → one event with an RRULE (`recurrenceRules`, e.g. `FREQ=DAILY;COUNT=7`); different checks per day → separate events.
7. **cccc memory note** `feedback_calendar-via-api.md` is rewritten to point at the global section, so a cccc session stops going straight to Chrome.

Rejected: a new pack skill for reminders (one paragraph in step 11 plus the global section is enough; YAGNI); owner's calendar ids in the pack (other users of the fork would write into nothing, and ids are personal).

Backwards compatibility: no break. Additive text; a user or project without `## Reminders` gets a byte-identical flow (same rule as `up:ujira` → no config, silent no-op).
TDD: no (reason: doc-only pack, no runtime code; verification is a live tool call and an install-and-invoke run)

### Prior art
- `plugins/up/skills/ujira/SKILL.md:15`, `:137`: opt-in config section in `CLAUDE.md`, silent no-op without it; the same shape is reused here.
- `plugins/up/commands/make.md:163`: step 11 already hands remaining checks to the owner; the trigger attaches there.
- `~/.claude/projects/-Users-svirins-dev-current-cccc-monorepo/memory/feedback_calendar-via-api.md`: owner defaults (Work, 11:00, 15 min, no notification, no guests) and the Chrome prefilled-link fast path.
- No task in `docs/tasks/` covers reminders.

### Invariants
- IV1: Without a `## Reminders` section in the loaded instructions, `/up:make` makes no reminder proposal and no calendar tool call.
- IV2: No calendar event is created before the owner's yes to the reminder list itself.
- IV3: Every created event is recorded in the task file with date, title and event id before the turn ends.
- IV4: Owner-specific values (account id, calendar id, time zone, defaults) appear only in `~/.claude/CLAUDE.md`, never under `plugins/up/`.
- IV5: Existing `/up:make` steps and resume of older task files keep working unchanged.

### Assumptions
- AS1: `notion-calendar-create-events` with the Work `accountId` + `calendarId` writes the event into "Work" in Google Calendar.
- AS2: The Notion calendar connection stays connected between sessions.

### Unknowns
- UK1: The create tool has no notification field; whether an event created through it carries the Work calendar's default notification, against the owner's "no notification" default. Resolve in verify with one test event.
- UK2: Whether `list-events` returns the event id needed for a later cancel, or only `create-events` does.
