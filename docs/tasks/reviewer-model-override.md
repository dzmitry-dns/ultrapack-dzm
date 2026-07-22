# Reviewer model override on request

**Status:** executing — trivial, Design/Plan skipped
**Branch:** main
**Goal:** `up:ureview` documents that the owner can request a per-dispatch reviewer model override ("review on Fable" / "review on the session model"); the default stays the agent's pinned model, and agent frontmatter pins are never edited for a one-off.

## Verify

**Result:** passed

- CK1 — new paragraph contradicts an existing pin or rule — held: `agents/reviewer.md` frontmatter untouched (`model: opus`); no "always opus" claim anywhere else in the pack
- CK2 — wording licenses silent auto-upgrades — held: override gated on "When the owner asks"; one-run scope explicit
- CK3 — conflicts with the never-pin-Fable policy — held: paragraph forbids editing the frontmatter pin for a one-off; override is dispatch-time only
- CK4 — section structure broken — held: paragraph sits between the dispatch skeleton and 1b; header order 1 → 1b → 2 intact

Smoke: doc-only — install-and-invoke rides the next `/plugin marketplace update` (same deferral as verify-recipe)

## Conclusion
<empty — filled by up:ureview>
