# Run Ultrapack in Codex

Use these operations wherever the shared instructions refer to a Claude Code tool or runtime feature.

- Resolve `${CLAUDE_PLUGIN_ROOT}` from the installed package directory containing this file. Read the invoked stage's `skills/<name>/SKILL.md` and its required references. Respect manual-only skills.
- Read project settings from `AGENTS.md`. For a shared section such as `Jira adapter`, use `CLAUDE.md` when the section exists only there. Stop before acting on conflicting definitions.
- Resolve a task checkout against `git worktree list --porcelain` and verify its branch before mutations. Attach it in Codex desktop when available. In the CLI, set the verified checkout as the working directory for every command and edit. Report a missing checkout instead of silently proceeding in the main checkout.
- Create new worktrees according to the project rules. Create or switch to the task branch before committing in a detached Codex worktree. For steps explicitly targeting the main checkout, select it and verify the branch separately. Archive a Codex-managed worktree or remove a clean Git worktree only at the workflow's cleanup step.
- Use Codex chat-list and message tools for peer notices. Record the current chat ID as the session identifier when available. Preserve an existing identifier if its ownership cannot be verified. Use the task-file handoff when a peer cannot be reached.
- Map each helper to its `up-` Codex role when installed, or read its role instructions under `agents/` and pass them to an authorized Codex helper. Keep review roles read-only. Send the requirements reviewer only the original request and diff. Report a required independent check as pending if no suitable helper is available.
- Keep the current Codex model unless an authorized supported model override is available. The shared trivial-phase scope check still applies.
- Use the available user input action or ask directly at approval pauses. Monitor one-off jobs through bounded background checks in the current chat.
- Before Jira writes, read the user's Jira rules and follow the project authorization. Use the configured `atlassian` MCP server. Resolve the correct site and issue. If a required action is unavailable, preserve the pending draft and leave its sync state unchanged.

## Keep the make workflow running

- After plan approval, finish step 6 and enter step 8 in the same turn. When the required preliminary checks pass and any temporary setup is cleaned up, record the transition to `executing` as the shared workflow requires, then start the first approved phase in the verified checkout. Give the check result as a progress update.
- During active work, answer a status question immediately in commentary with the latest confirmed progress. Then resume the pending tool calls in the same turn. If a background check is still running, keep polling it in bounded intervals and start the next authorized check when it finishes.
- Use a final reply when the workflow finishes, requires approval or other user input, hits a blocker that prevents further authorized work, or receives a stop command. An update about a completed check or a question asking only for status does not end the turn.
