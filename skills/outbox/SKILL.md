---
name: outbox
description: Run a text drafted in this session for other people (an email, a doc, a message, an announcement) through the `outbox` CLI for a plain-English rewrite by a second model. Use when the user asks to "make this plain", "say it like a person", "de-claude this", "run it through outbox", asks for a version for the team, a manager, a funder, hackathon participants, or a reader they name ("for Sam", "for the post's author"), or wants the Claude habits removed without changing anything else ("just de-claudish it", "polish, don't shorten"), or is about to send something drafted here and wants it to read as their own writing. Not for every reply: only text meant for someone else.
---

# outbox: a second model edits the draft

A draft's author cannot see its own habits, since it reads them as normal; the `outbox` CLI has a Gemini model, which has different habits, rewrite the draft. So the draft reaches it untouched and the result reaches the user in its words: do not tidy, trim or paraphrase the draft before the call, and do not restyle the result after it. The one edit allowed afterwards puts back a fact the rewrite moved (step 5).

## Invocation

`/outbox:outbox [audience] [text]`, both optional.

- **audience**: a name as the first word, or a description of the reader. Names: `engineer` (default; another engineer, everything kept), `polish` (same audience as the draft, wording only, no summarizing), `team` (a teammate running programs or operations; operational detail, no code), `manager` (a manager or director; three to five sentences: outcome, impact, ask), `funder` (a program officer; measured report register), `participant` (a hackathon participant; warm, simple, tells them what to do). With no reader named, pick the name from who the text is for. Anything else the user says about the reader ("for Sam", "the post's author and the other programme leads") goes to `--for` as a quoted phrase: who they are and what they know, in the user's words where given, plus anything said about register or length. A description replaces the named note, and the CLI's defaults for it keep the content and structure, so a description that wants the text shorter must say so. To keep a name's rules for a narrower reader, pass the name and add `--instruction "The reader is ..."`.
- **text**: when empty, the most recent text you wrote for someone else in this conversation, word for word.

## Steps

1. Write the draft to a scratch file with the Write tool (e.g. `outbox-draft.md`), never through shell quoting.
2. In that directory run `outbox --for <audience> outbox-draft.md > outbox-rewrite.md 2> outbox-changes.txt` (a described reader in quotes), with a 150-second timeout. Stdout is the rewrite; stderr holds the change list, warnings and any error.
3. Read both files whole with the Read tool, no offset or limit, and no `head`, `tail`, `grep`, `sed` or `wc` on them: a filter shows the lines you predicted and hides the ones the model changed.
4. Check the rewrite against the draft, sentence by sentence: every number, date, name, link, identifier, command, code block, condition and commitment is unchanged, and nothing is said that the draft did not say. Compare with the draft itself; the change list has missed changes before.
5. Fix each discrepancy in `outbox-rewrite.md` with the smallest edit that restores the draft's claim: swap the draft's number, name, date, link, identifier or word back in; delete a clause the draft never said; restore a dropped sentence in the draft's own words. Touch nothing around it, and never a sentence step 4 found accurate. If no edit that small restores the claim (a paragraph whose meaning moved), rerun outbox rather than rewriting the passage yourself.
6. Reply with the rewrite as it now stands, after one lead line at most ("Rewritten for the team:"), then the change list verbatim under a "Changes" heading, with no summary or comment. If step 5 made fixes, add a "Check" heading with one line per fix quoting the rewrite's words before and after.
7. Show any stderr warning (a surviving em dash, a rewrite cut short). An em dash is a style residue, not a moved fact: leave it; the user can rerun.

## When the tool fails

Show the actual error (no key at `~/.config/gemini/api-key`, an HTTP error from Gemini, a network error). Offer your own rewrite only if the user asks, clearly labeled as a fallback.
