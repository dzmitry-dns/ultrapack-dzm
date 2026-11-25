# UltraPack

This repository distributes the `up` development workflow plugin for Codex and Claude Code.

## Repository layout

- `.agents/plugins/marketplace.json` lists the Codex plugin under `plugins/up/`.
- `plugins/up/.codex-plugin/plugin.json` declares the skills and hooks loaded by Codex.
- `.claude-plugin/marketplace.json` and `plugins/up/.claude-plugin/plugin.json` describe the Claude Code distribution.
- `plugins/up/{skills,commands,agents,hooks}/` contains the shared workflow and client-specific integrations.
- `codex/agents/` contains Codex role definitions. See README.md for installation.
- `docs/tasks/` holds task designs, plans, and conclusions.

## Naming

Keep the `up` namespace and the existing `u` prefix for process skills. Codex enters the shared workflow through `codex-make` and `codex-summary`.

## Design and verification

Keep only skills the project uses. Most changes edit Markdown instructions. Install the plugin and exercise the affected entry point. For changes to the Python handler in `plugins/up/hooks/context-handoff-codex.py`, verify the affected events declared in `plugins/up/hooks/codex.json`.

## Fork policy

This is a fork of `btseytlin/ultrapack`. Send generic fixes upstream and keep owner-specific workflow preferences in this fork. Cherry-pick relevant upstream changes from `upstream/main`.

## Versioning

When landing changes on main, bump the patch version in both plugin manifests. Ask the owner before a minor or major bump.
