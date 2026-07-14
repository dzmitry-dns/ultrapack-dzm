---
description: Explain something like a colleague explaining to another engineer. Picks a realistic depth, explains it in one message, offers follow-up threads.
---

# /up:e

Explain the target the way one engineer explains something to another over a desk — not a doc dump.

## Arguments

Optional. If arguments follow the command, they name the target (a file, an error, a concept, "why did X happen"). If empty, infer the target from the most recent open question or topic in the conversation, and say which one was picked in the first line.

## Process

### 1. Ground it

If the target is something you can inspect — a file, a diff, an error, a conversation turn — look at it now instead of explaining from memory. Pure concept questions (no inspectable target) skip this.

### 2. Assume vague recall

Treat the reader as only vaguely remembering prior context, not tracking every detail of this conversation. Don't lean on "as discussed above.", use as few context-dependent terms as possible, speak plainly.

### 3. Pick the depth

Decide the structure: what's the shortest chain of inferential steps that gets to real understanding? Pick the level of detail actually achievable in one message. Don't overreach into exhaustive detail. Don't underreach into a vague summary.

### 4. Write it

One message. Plain language, like explaining out loud to a smart colleague. No wall of text, no invented terminology. When a term is unavoidable, unpack it in plain words. Terse and plain aren't opposites — cut words, not the explanation.

### 5. Offer next threads

If necessary, end with 1-3 follow-up threads worth going deeper on, named but not answered. Skip this if the explanation is already complete and nothing meaningfully deeper remains.

## Rules

- Test: could a sharp person outside this codebase follow it with no glossary? If not, rewrite.
- If the target is genuinely ambiguous — no argument, no clear recent topic — ask once instead of guessing.
