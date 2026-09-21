---
name: outbox
description: Run a text drafted in this session for other people (an email, a doc, a message, an announcement) through the `outbox` CLI, which has a Gemini model rewrite it in plain English and list its changes. Use when the user asks to "make this plain", "say it like a person", "de-claude this", "run it through outbox", asks for a version for the team, a manager, a funder, hackathon participants, or a reader they name ("for Sam", "for the post's author"), or wants the Claude habits removed without changing anything else ("just de-claudish it", "polish, don't shorten"), or is about to send something drafted here and wants it to read as their own writing. Not for every reply: only text meant for someone else.
---

# outbox: a second model edits the draft

A text drafted here for other people usually carries habits that its author cannot see, because the author reads them as normal. The `outbox` CLI hands the draft to a Gemini model with a description of those habits and prints what comes back. The second model is there because it has different habits, so the draft has to reach it untouched and the result has to reach the user in the second model's words: do not tidy, trim or paraphrase the draft before the call, and do not restyle the result after it. The one edit allowed after the call puts back a fact the rewrite moved, and it is as small as the fact (step 5).

## Invocation

`/outbox:outbox [audience] [text]`. Both parts optional.

- audience: one of six names as the first word, or a description of the reader. The names: `engineer` (default; another engineer, everything kept), `polish` (same audience as the draft, no summarizing, wording only), `team` (a teammate running programs or operations; operational detail, no code), `manager` (a manager or director; three to five sentences: outcome, impact, ask), `funder` (a program officer; measured report register), `participant` (a hackathon participant; warm, simple, tells them what to do). Anything else the user says about who reads it is a description ("for Sam", "the post's author and the other programme leads", "a partner org's ops lead who has never seen our Notion"): pass it to `--for` as a quoted phrase saying who they are and what they know, in the user's words where they gave them, plus anything they said about register or length. A description replaces the named note; the CLI adds its own defaults after it (keep the content and the structure, change the register and the wording), so a description that wants the text shorter says so. When the user wants a name's rules for a narrower reader, keep the name and add `--instruction "The reader is ..."`. When the user names no one, pick the name from who the text is for.
- text: the rest. When empty, the draft is the most recent text you wrote for someone else in this conversation (the email body, the doc, the message), reproduced word for word.

## Steps

1. Write the draft to a file in the scratchpad with the Write tool, for example `outbox-draft.md`. Never pass it through shell quoting.
2. Run `outbox --for <audience> outbox-draft.md > outbox-rewrite.md 2> outbox-changes.txt` in the scratchpad, with a described reader in quotes (`--for "Sam, who runs operations"`). Give it 150 seconds; a call usually takes a few seconds. The rewrite is stdout, the change list and warnings are stderr, and an error lands in the stderr file too.
3. Read `outbox-rewrite.md` and `outbox-changes.txt` whole, with the Read tool, no offset or limit. Never run `head`, `tail`, `grep`, `sed -n`, `wc` or any other filter on either file, and never read part of one: a filter shows the lines you predicted and hides the lines the model changed, and the changed lines are what this step exists to find.
4. Check the rewrite against the draft, sentence by sentence: every number, date, name, link, identifier, command, code block, condition and commitment in the draft is in the rewrite unchanged, and the rewrite carries nothing the draft did not say. Check against the draft itself, not against the change list. The change list has missed changes before (funder mode renamed model identifiers on 2026-08-25 and listed none of them, see the README's follow-ups), so it does not stand in for the comparison.
5. When step 4 found a discrepancy, fix it in `outbox-rewrite.md` with the smallest edit that restores the draft's claim: put the draft's number, name, date, link, identifier or word in place of the rewrite's; delete a clause the draft never said; put a dropped sentence back in the draft's own words. Change nothing around the fix: not the shape of the sentence, not its neighbours, and never a sentence step 4 found accurate. The rule against editing the result is a rule against restyling it, since the draft's author restyling the rewrite brings back what the tool removed; a fact put back is not a restyle. When no edit of that size restores the claim (a paragraph whose meaning moved as a whole), rerun outbox instead of rewriting the passage yourself.
6. Reply with the rewrite as it now stands, with one lead line at most, such as "Rewritten for the team:". Then show the change list under a "Changes" heading, verbatim. Do not summarize the changes or add a comment on the rewrite. When step 5 made a fix, add a "Check" heading after the change list with one line per fix, quoting the rewrite's words before and after, so the sender sees exactly what moved back.
7. When stderr carries a warning (an em dash survived, or the rewrite was cut short), show it. An em dash is a style residue, not a moved fact, so it is not yours to fix; the user can rerun.

## When the tool fails

Show the actual error. The usual ones: no key at `~/.config/gemini/api-key` (the user adds one), an HTTP error from Gemini (the message names the status and body), a network error. Offer your own rewrite only as a clearly labeled fallback, and only if the user asks. A rewrite by the draft's author brings back what the tool exists to remove.

## What the reader gets

The rewrite keeps every fact, number, date, name, link, condition, and commitment, and the draft's language. The model is told to add nothing, to keep a claim general when the draft gives no number, and to leave a sentence alone and list it when a rewrite would change its claim. The change list and the "Check" lines are the sender's review surface: the first is what the model says it changed, the second is what the session had to put back. Read both against the draft before sending.
