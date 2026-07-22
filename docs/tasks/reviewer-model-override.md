# Reviewer model override on request

**Status:** shipped — 2026-07-22; 0.3.31 installed same day (cache verified, SHA 0c42512); pre-close control review clean
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

Outcome: per-dispatch model override documented in ureview section 1 (applies to 1b too); pins untouched. 6ae53bb + review fix.

Review findings:
- Important: "the owner" broke the file's user/dispatcher/reviewer vocabulary — changed to "the user"

Pre-close control review (2026-07-22): `up:reviewer` re-dispatched on 27f383a..0c42512 — merge-ready, zero findings ≥80; CK1–CK4 re-confirmed against files; 0.3.31 cache verified. Sub-threshold notes (no action): README:117 describes only the default pin (level-of-detail choice); "Fable" codename in SKILL.md:73 is an illustrative user utterance.
