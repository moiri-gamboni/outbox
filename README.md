# outbox

outbox rewrites a text that an AI assistant drafted for other people (an email, a doc, an announcement) in plain English, and lists what it changed. The editor is a Gemini model, because a model edits out its own habits badly: it reads them as normal. outbox is a command, and a Claude Code plugin whose skill runs it on a draft and passes the result on without restyling it; the skill's one edit afterwards puts back a fact the rewrite moved, span for span (step 5 of `skills/outbox/SKILL.md`). It is meant for occasional outward-facing text, not every reply.

## Install

1. Clone the repository and put `outbox` on your `PATH`: add the clone directory, or symlink `outbox` into a directory already on it. It needs only Python 3's standard library.
2. Get a Gemini API key at https://aistudio.google.com/apikey and save it to `~/.config/gemini/api-key` with mode 0600, or set `GEMINI_API_KEY`. Use a key of your own: the free tier's daily quota is shared by everything that uses the key.
3. Optional: put two or three short samples of your own writing in `~/.config/outbox/voice.md`, and the model matches that register. `--voice FILE` reads samples from elsewhere, `--no-voice` skips them.
4. For the Claude Code skill, install the plugin, then ask for a plain version of a draft or run `/outbox:outbox [audience] [text]`:

   ```
   /plugin marketplace add /path/to/your/outbox/clone
   /plugin install outbox@outbox
   ```

## Rewrite a draft

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
```

Stdout is the rewrite and nothing else, so it can be pasted as is. Stderr carries the model's list of changes, a warning when an em dash survived or the rewrite was cut short, and a usage line with the token counts and the model that served the call.

`--instruction "..."` (repeatable) adds a rule for one call. It is for a caller that knows something about where the text lands that the rules cannot: a value the text will sit beside, a term this reader will not have. A task tracker, for example, can tell it not to restate the status or due date that its row already shows beside the body. The model gets it as a rule to obey, where `--voice` samples are prose to imitate. Without `--instruction`, the prompt has no such block at all.

The other options (`--model`, `--thinking`, `--temperature`, `--timeout`) and every default are in `outbox --help`.

## Check the rewrite before sending

Read the whole rewrite against the draft, with the change list beside it. The failure that matters with any rewriter is a fact that moved: a number that changed or appeared, a condition that went missing, a promise the draft never made. Do not skim it through `head`, `tail` or `grep`; a filter shows the lines you expected and hides the ones that changed.

- Compare with the draft, not only the change list, which can miss a change: a funder rewrite has given a draft's shorthand model name an official-looking full name without listing the rename. `rules.md` forbids renaming identifiers, but check them.
- Do not run outbox on its own output. A second pass is close to idempotent but not exact: it can trade a precise word for a plainer, vaguer one while reporting that no claims changed. To shorten or retarget a rewrite, run outbox on the original draft again.

## Audiences

Each name adds one paragraph ahead of the rules, which wins where the two conflict.

- `engineer` (default): another engineer. Style changes only; every fact, number, file path, command and code block stays, and the text shortens only by the filler removed.
- `polish`: whoever the draft was written for. Wording only: structure, headings, lists and every sentence's content stay, so the result runs about the draft's length.
- `team`: a teammate who runs programs and operations. Leads with what happened, why it matters and what is needed; keeps every fact, date, name and link; drops code, paths and implementation detail unless one is the point; aims for about a third of the draft's length.
- `manager`: a manager or director with thirty seconds. Three to five sentences: the outcome, the impact or risk, any decision or ask, with the numbers and link needed to act. No code, paths, lists or headings.
- `funder`: a program officer who will quote the text. A research-impact report's register: every number says what it counts and over which population, uncertainty and the as-of date are stated once, associations stay associations and detection counts are floors, nulls and caveats stay in, no promotional language, invented jargon or process notes.
- `participant`: a hackathon participant, often early in their career, reading English as a second language, on a phone. Warm, second person: what this is and what they get, then what to do, with any deadline and link. Short paragraphs, no internal names, greeting and sign-off kept.
- A described reader (`--for "Sam, who runs operations and has not seen the code"`): the phrase replaces the named note, so whatever it says about the reader, the register or the length outranks the rules. What it leaves unsaid defaults to `polish`: the register this reader expects, shorthand said in ordinary words, every paragraph's content and the draft's structure kept, so a description that wants the text shorter must say so. To keep a name's rules for a narrower reader, pass the name and add `--instruction "The reader is ..."`. A single word that is not a name is refused as a misspelling; a description takes at least two.

## Model

The default is `gemini-flash-latest`, Google's alias for the newest Flash release, previews included. The usage line names the model that actually served the call (`gemini-flash-latest served by ...`), so a change of model shows on its first run; for a reproducible run, pass a fixed model id with `--model` or `$OUTBOX_MODEL`. `gemini-3.1-pro-preview` is the most capable option, `gemini-3.5-flash-lite` the cheap one.

Thinking defaults to `high`, the most faithful level in testing (`low` dropped facts and invented asks). Temperature stays at 1.0, since Google's Gemini 3 guide warns that lowering it can degrade output. A 429 or 5xx response is retried, honouring `Retry-After`, up to four attempts in all; then outbox exits with the response body.

## How the prompt is built

The system instruction is, in order: the audience paragraph, marked as taking precedence on conflict (which settles, for example, the engineer note's "do not shorten" against the rules' preference for deleting); any voice samples; the whole of `rules.md`; any `--instruction` rules. The spec's last line ("Output only the rewritten text.") is replaced by the output format: the rewrite, a `--- changes ---` line, then the changed claims and the wording notes.

`rules.md` began as an outside spec and keeps that spec's structure as its backbone, with rules from several other sources folded into the sections they belong to, alongside a few rules and audience notes written for outbox itself; none of it is reproduced verbatim. Every source, its license, and exactly what it contributed are in `THIRD-PARTY-NOTICES.md`.

## Development

```
python3 -m unittest discover tests
```

The tests run offline against scripted responses. `rules.md`, the audience notes and the described-reader text must pass the rules they carry: the tests fail on an em dash in any of them or contrast framing in the notes.

## License

AGPL-3.0, in `LICENSE`. `rules.md` and the audience notes carry text from four MIT-licensed projects and one GPL-3.0-licensed project; their notices are in `THIRD-PARTY-NOTICES.md`. The deslop gist has no license, so it is credited there without a notice entry.
