---
name: outbox
description: Run a text drafted in this session for other people (an email, a doc, a message, an announcement) through the `outbox` CLI for a plain-English rewrite by a second model. Use when the user asks to "make this plain", "say it like a person", "de-claude this", "run it through outbox", asks for a version for the team, a manager, a funder, hackathon participants, or a reader they name ("for Sam", "for the post's author"), or wants the Claude habits removed without changing anything else ("just de-claudish it", "polish, don't shorten"), or is about to send something drafted here and wants it to read as their own writing. Not for every reply: only text meant for someone else.
---

# outbox: a second model edits the draft

You cannot see your own writing habits, because they look normal to you. The `outbox` CLI has a Gemini model, whose habits differ, rewrite the draft instead. So pass the draft exactly as written, without tidying or trimming it first, and pass the rewrite on without restyling it. The only edit you make afterwards is putting back a fact the rewrite changed (step 5).

## Invocation

`/outbox:outbox [audience] [text]`, both optional.

- **audience**: an audience name as the first word, or a quoted description of the reader. When empty, choose from who the text is for.
- **text**: when empty, the most recent text you wrote for someone else in this conversation, word for word.

## Choosing the audience

The names are `engineer` (the default: another engineer, everything kept), `polish` (the draft's own readers: wording only, no summarizing), `team` (a teammate running programs or operations: operational detail, no code), `manager` (a manager or director: three to five sentences with the outcome, the impact and the request), `funder` (a program officer: a measured report), and `participant` (a hackathon participant: warm, simple, tells them what to do).

Use a name whenever one is close, even when the user names a particular reader ("for Sam", "for the post's author and the other programme leads"). Pass the closest name with `--for`, and put what the user said about the reader in `--instruction "The reader is ..."`: who they are, what they know, and anything they said about tone or length, in their words where they gave them. An operations lead who has not seen the code is `team` plus such an instruction; a manager who wants a short reply is `manager` plus one.

Only when no name is close, pass the reader's description to `--for` as a quoted phrase. It takes the place of a name's paragraph; `rules.md` and any instructions still apply. What the description leaves out defaults to keeping the draft's content and structure, so a description that wants the text shorter must say so.

## Steps

1. Make a scratch directory with `mktemp -d`, and write the draft to `outbox-draft.md` in it with the Write tool, never through shell quoting.
2. In that directory run `outbox --for <audience> [--instruction "The reader is ..."] outbox-draft.md > outbox-rewrite.md 2> outbox-changes.txt` with a 600-second timeout, since outbox retries failed requests itself; quote a described reader. Stdout is the rewrite; stderr holds the change list, warnings and any error.
3. Read both files whole with the Read tool, with no offset or limit, and never through `head`, `tail`, `grep`, `sed` or `wc`: a filter shows the lines you expected and hides the ones the model changed.
4. Check the rewrite against the draft, sentence by sentence: every number, date, name, link, identifier, command, code block, condition and commitment is unchanged, and the rewrite says nothing the draft did not. Compare with the draft itself, because the change list sometimes misses changes.
5. Fix each discrepancy in `outbox-rewrite.md` with the smallest edit that restores what the draft said: put back the draft's number, name, date, link, identifier or word, delete a clause the draft never said, or restore a dropped sentence in the draft's own words. Leave everything around it alone, including every sentence step 4 found accurate. If a small edit cannot fix it (a paragraph whose meaning changed), rerun outbox instead of rewriting the passage yourself.
6. Reply with the rewrite as it now stands, after at most one lead line ("Rewritten for the team:"). Leave the change list and your check out of the reply. The user can ask for them.
7. After the rewrite, add at most one line, and only if there is something to say: how many facts step 5 put back, and whether stderr warned that the rewrite was cut short. Leave out a surviving em dash, which is a matter of style and not a changed fact.

## When the tool fails

Show the actual error (no key at `~/.config/gemini/api-key`, an HTTP error from Gemini, a network error, no response within the timeout). Offer your own rewrite only if the user asks, clearly labeled as a fallback.
