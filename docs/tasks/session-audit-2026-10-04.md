# Session audit 2026-10-04

**Status:** reviewing
**Branch:** main
**Goal:** Every permission prompt and every owner complaint of 2026-10-03/04 has a named root cause and a fix in the place that caused it (dippy config, global CLAUDE.md, cccc rules or memory, or this pack), proven by a dippy replay of every Bash call of those two days and by a probe per new rule.

## Design

Owner ask (2026-10-04, verbatim core): "изучи сессии за сегодняшний день ... опять начали спрашивать о permissions ... объяснить, почему git add docs ... требует у меня permission ... поработай так, чтобы мне не потребовалось после этого сделать повторный ревью ... выполни работу над ошибками, исправь все. Работай и с ультрапаком, и с Claude Code." Mid-turn additions: prompts for scripts in the Claude tmp folder in a neighbour session; a ticket split left the source ticket description stale (CATS-1729 → CATS-1759); review and requirements review after the fixes.

Method: all Bash calls of 34 transcripts (2026-10-03/04, subagents included, 838 calls) paired with their results and replayed through `dippy --claude`; the 119 owner messages read; 3 subagents traced 8 complaint episodes in the transcripts.

Findings and fixes (no pack skill was involved in any episode except F8):

| # | What the owner saw | Root cause | Fix |
|---|---|---|---|
| F1 | "`git add docs` asks again" | 25 of 59 asks were `git push origin main` at the end of a `git add && git commit && git push` chain; the dialog shows the start of the chain. Owner allowed push to main on 2026-10-02 in cccc `workflow.md:29`, dippy was never changed. | `~/.dippy/config`: push to main allowed (force push still denied, production-demo still asks). Global CLAUDE.md: policy lives in two places, change both, probe the whole chain. |
| F2 | "Claude tmp folder" prompts in a neighbour session | `bash <scratch>/__probe*.sh` (9), `psql -f` (8), `kill $(lsof ...)` | dippy: `bash`/`sh` in `/private/tmp/claude-*` and `/tmp/claude-*`; `psql -f *.sql` with or without an env prefix; `kill $(lsof -ti*`. Reasoning in the config comments: `allow bun` already runs any file from the same dir. |
| F3 | other false asks | `xargs grep -o` read as `xargs -o`; `claude plugin validate/update`; `/usr/bin/true`; staging `gh workflow run` (owner orders staging in chat) | dippy allows; production `gh workflow run` still asks, now with the reason "PRODUCTION deploy". |
| F4 | main-app production build nobody asked for | cccc memory `feedback_never-auto-swap-prod-slot.md` said a production build into the preview slot is "fine and the end of the agent's part"; "запускай 1, 2, 3, 4" covered an item that bundled main-app and job-api | memory rewritten; cccc `workflow.md` gained a per-app yes rule (commit d6d37c519); global CLAUDE.md check 9: production writes never mid-turn. |
| F5 | "staging blocked on .env" while DB access works | cccc memory note "Key Vault is a dead end, ask the owner", wrong | Not changed by this session: the edit was refused by the auto-mode classifier. Left for the owner. The correct recipe is in `feedback_fetch-db-env-yourself.md` (written by that session). |
| F6 | "you ignore my questions"; "Стой" arrived after a prod write | focus mode hid mid-turn text; the answer was only mid-turn | owner turned focus off; global CLAUDE.md check 8: the final message answers every question of the turn. |
| F7 | final answer in English | rule existed, not followed after English Jira/Notion writes | Stop hook `~/.claude/hooks/russian-final-check.sh` blocks a final answer with 15+ Latin words and no Cyrillic, unless the owner asked for English; registered in `~/.claude/settings.json`. Memory note that said "final answers were Russian" corrected. |
| F8 | ticket split left CATS-1729 description stale | `up:ujira` revisits a description only at Status transitions; a scope move is not one | `plugins/up/skills/ujira/SKILL.md`: scope move drafts a description item for the source ticket in the same step. Global CLAUDE.md Jira paragraph says the same for sessions outside `/up:make`. |
| F9 | wrong logo reached staging | "works" claimed from a URL in a CSV | global CLAUDE.md Verification Protocol: render and show a visual asset before commit. |

Not fixed, on purpose: `git checkout -- <file>` (discards edits), `docker build/run`, `brew install`, `rsvg-convert`, arbitrary `kill <pid>`, `bash /tmp/<not claude>` still ask. Episode "why is it blocked?" (76493837) and the dense design text (28349add) broke rules that already exist; no new rule.

TDD: no (doc and config change).

## Verify

- Replay of the 838 calls against the new config: 779 allow → allow, 40 ask → allow, 19 ask → ask, no other change (no deny → allow, no allow → ask). After that run three more rules were added (env-prefixed psql, `psql -f *.sql`, `kill $(lsof ...)`), each probed: the two commands from the owner's screenshot now allow; `kill 12345`, `psql -c "drop table x"`, `git push --force`, `claude plugin uninstall`, production `gh workflow run` still ask or deny.
- Stop hook: blocks the real 07:29 English answer cut from transcript 7655d12b; passes a full Russian session (27cbe9c1), a Russian answer, an answer under 15 words, an owner message asking for English, and `stop_hook_active`.
- cccc push d6d37c519 ran without a prompt.

## Conclusion

Pending review.
