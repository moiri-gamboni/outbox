# outbox

Rewrites a text that an AI assistant drafted for other people (an email, a doc, an announcement) into plain English, using a Gemini model as the editor. The draft's own author, Claude, never restyles the result: a model edits out its own habits badly, since it reads them as normal. Its one edit after the call puts a fact the rewrite moved back in place, span for span (the skill's step 5). The tool is for occasional outward-facing text. It is a command you run, and a Claude Code skill that runs it.

## Usage

```
outbox draft.md                       for another engineer (default)
outbox --for polish draft.md          remove the Claude habits, change nothing else
outbox --for team draft.md            operational detail, no code
outbox --for manager draft.md         three to five sentences: outcome, impact, ask
outbox --for funder draft.md          measured report register
outbox --for participant draft.md     warm, simple, tells them what to do
outbox --for "Sam, who runs operations" draft.md
                                      any phrase describes the reader instead
cat draft.md | outbox                 stdin works too
outbox --show-prompt --for funder     print the system instruction, make no request
outbox --instruction "..." draft.md   one more rule for this call, repeatable
```

Stdout is the rewrite and nothing else, so it can be pasted as is. Stderr carries the model's list of changes, a warning when an em dash survived, and a usage line with the token count and the model that served the call. Read the whole rewrite against the draft before sending, and the change list with it: the failure that matters with any rewriter is a fact that moved, a number that appeared, or a promise the draft never made, and the change list alone has missed such a change (see Follow-ups). Do not skim it through `head`, `tail` or `grep`; a filter shows the lines you expected and hides the ones that changed.

Flags: `--for engineer|polish|team|manager|funder|participant|"a phrase describing the reader"` (default engineer), `--model` (default `gemini-flash-latest`, or `$OUTBOX_MODEL`), `--voice FILE`, `--no-voice`, `--instruction TEXT` (repeatable), `--thinking minimal|low|medium|high` (default high), `--temperature` (default 1.0), `--timeout` (default 120s).

`--instruction` is for a caller that knows something about the context the text lands in and the rules cannot: a value the text will sit beside, a term this reader will not have. It appends the rule to the system prompt, introduced as a rule to obey. It is not `--voice`, which says "match this register" and would turn a directive into prose to imitate. Passing none leaves the system prompt byte-identical to what it was before the flag existed, which a test pins: a shared tool must not shift under a change made for one caller. A task-tracking tool could call it as the first caller this way: telling the model not to restate the priority level, status, due date or assignee that the task row already shows as fields beside the body.

## Install

Clone the repository, `chmod +x outbox`, then put the clone directory on `PATH` or symlink `outbox` into a directory that already is. The Claude Code skill installs through the plugin, as below.

## Setup

- A Gemini API key at `~/.config/gemini/api-key` (0600), or `GEMINI_API_KEY` in the environment. Get one at https://aistudio.google.com/apikey. Use a personal key: the free tier's daily quota is shared by everything that uses the key, a production service included.
- Optional: `~/.config/outbox/voice.md` with two or three short samples of your own writing. When it exists, the prompt asks the model to match that register. `--voice FILE` points elsewhere, `--no-voice` skips it.
- Python 3 standard library only. No package to install.

## Where the prompt comes from

The system instruction (`outbox --show-prompt --for <audience>` prints it) is the audience note (marked as taking precedence on conflict, which settles the engineer note's "do not shorten" against the rules' preference for deleting; for a described reader, the description and the tail that follows it), any voice samples, and then `rules.md`, the whole instruction document, followed by any `--instruction` rules the caller passed.

`rules.md` began as the programasweights "Claudish to English" spec (github.com/programasweights/claudish, MIT, `specs/claudish-to-english.md`), which is still its backbone and the source of everything distinctive in it: the definition of Claudish, the smallest-set-of-ordinary-propositions goal, the metaphor glossary, and "Preserve logical scope exactly", the one section no other source has ("required" does not become "sufficient", "not tested" does not become "wrong"). It is **no longer verbatim**. Rules folded in since, each into the section it belongs to: vomit's agency and em-dash rules and its self-praise line (github.com/zachahn/vomit, GPL-3.0); a fact guard against inventing a number or a cause a source never gave, echoing bmurphy1976's deslop skill (a GitHub gist, unlicensed; the rule is credited but not reproduced from it) and the SimpleEnglish STE prompt's "NEVER TOUCH" clause (github.com/AminBlg/SimpleEnglish, MIT); the same-language line from claudish-to-english; the status ladder, keep-both-branches and linked-item-naming rules that a five-body test produced; and, from the `humanizer` skill (github.com/blader/humanizer, MIT, itself derived from Wikipedia's "Signs of AI writing"), chat artifacts and servility, signposting, copula avoidance, synonym cycling, false ranges, rule-of-three padding, speculative gap-filling, the formatting tells (mechanical boldface, bolded list labels, Title Case headings, emoji, curly quotes), predicate-position hyphenation, "I" never becoming "we", and the section that matters most for not over-editing: what to leave alone, since specific detail, unresolved tension, asides and varied sentence length are the writing working rather than tells. The spec's last line ("Output only the rewritten text.") is replaced by the output format: the rewrite, a `--- changes ---` line, then the claim diff and the wording notes.

The file has to pass the rules it carries, and so do the audience notes; `tests/test_outbox.py` checks the notes for em dashes and contrast framing, and `rules.md` now holds no em dashes either.

## Audiences

Each `--for` name appends one paragraph to the rules. Three are internal, two are public, and `polish` keeps whatever audience the draft already has. Anything that is not a name is a description of the reader, and one unknown word is refused as a misspelt name (a reader takes at least two words to describe).

- `polish`: no audience change and no summarizing. Structure, headings, lists, and every sentence's content stay; only the wording moves, so the result runs about the draft's length. The note overrides the spec's preference for compression through the precedence line.

- `engineer`: nobuzz's colleague mode, recast to open with the reader like the other notes and otherwise kept (its one em dash became a colon). Style changes only; every file path, command and code block stays.
- `team`: nobuzz's manager mode, recast the same way for a teammate who runs programs and operations, keeping its one-third length target. Leads with what happened, why it matters and what is needed; keeps every fact, date, name and link; drops code, paths and implementation mechanics unless one is the point.
- `manager`: nobuzz's director mode, the merged manager/director brief: three to five sentences, outcome, impact or risk, any ask, thirty seconds of attention, no code, paths, lists or headings.
- `funder`: no source prompt. The register is a research-impact report's, and the rules are the ones that survived its review rounds: every number says what it counts and over which population, uncertainty and the as-of date once in plain words, associations reported as associations and detection counts as floors, nulls kept with a plain caveat, no promotional language, invented jargon or process notes. An invented sentence in that register is included as a sample.
- `participant`: no source prompt. The register is a programme welcome email's: warm and professional, second person, what this is and what they get first, then what to do with any deadline and link, short paragraphs, ordinary words, no internal names, greeting and sign-off kept. One passage from such an email is included as a sample.
- a described reader (`--for "Sam, who runs operations and has not seen the code"`): the phrase opens the audience block verbatim, under the precedence line, so whatever it says about the reader, the register or the length outranks the rules; a fixed tail follows with the defaults for what it does not say: write in the register this audience expects, say shorthand they would not know in ordinary words, and otherwise keep every paragraph's content and the draft's structure, shortening only by what removing filler removes (polish's behaviour). A description replaces the named note. To keep a name's rules and only narrow the reader, pass the name and add `--instruction "The reader is ..."`.

## Model

`gemini-flash-latest` by default: Google's alias for the newest Flash release, which the model docs say can be a stable, preview or experimental release and is hot-swapped at each new one, with two weeks' email notice for a breaking change. As of 2026-09 it resolves to `gemini-3.8-flash`. The usage line on stderr names the model that served the call (`gemini-flash-latest served by gemini-3.8-flash`), so a swap is visible on the first run after it; a run that has to be reproducible passes a concrete id through `--model` or `$OUTBOX_MODEL`. Calls use `--thinking high` and the default temperature of 1.0 (the Gemini 3 guide warns that lowering it can degrade output), through `models/{model}:generateContent` (REST, `x-goog-api-key` header). `--model gemini-3.1-pro-preview` is the most capable option, `--model gemini-3.5-flash-lite` the cheap one. On the one draft tested so far, high was the most faithful level and low the one that dropped facts and invented asks, which is why high is the default. Retries on 429 and 5xx (Retry-After honored, then exponential backoff, four attempts), then exits with the response body. A rewrite cut short (`finishReason` other than `STOP`) is still printed, with a warning.

## Tests

```
python3 -m unittest discover tests
```

Offline: a fake `urlopen` replays scripted responses.

## Follow-ups

- A funder-register rewrite can invent a canonical name for a draft's shorthand identifier (a model name, a version string) without the change list flagging the rename as a change; rules.md carries an identifier-preservation rule against this, and the review step reads the whole rewrite against the draft rather than trusting the change list alone.
- Running outbox on its own prior output is close to idempotent but not exact: a pass can still trade a precise word for a plainer, less specific one while reporting no claims changed, so re-compressing an already-rewritten text is a hazard best avoided by redrafting from the original source instead.

## Notices

AGPL-3.0, in `LICENSE`. `rules.md` carries text from four MIT-licensed projects and one GPL-3.0-licensed project; their notices are in `THIRD-PARTY-NOTICES.md`. bmurphy1976's deslop skill (a GitHub gist) also shaped a rule in `rules.md`; the gist carries no license, so it is credited above ("Where the prompt comes from") without a notice entry and without reproducing its text.
