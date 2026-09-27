# outbox

outbox takes a text that an AI assistant drafted for other people, such as an email, a doc or an announcement, and has a Gemini model rewrite it in plain English. It prints the rewrite and a list of what it changed. A different model does the editing because a model cannot see its own writing habits.

outbox is a command-line tool and a Claude Code plugin. The plugin's skill runs the command on a draft, checks the rewrite against the draft for changed facts, and shows you the rewrite. It is meant for the occasional text that goes to other people, not for every reply.

## Install

1. Clone the repository and put `outbox` on your `PATH`: add the clone directory, or symlink `outbox` into a directory already on it. It needs only Python 3's standard library.
2. Get a Gemini API key at https://aistudio.google.com/apikey and save it to `~/.config/gemini/api-key` with mode 0600, or set `GEMINI_API_KEY`. Use a key of your own: the free tier's daily quota is shared by everything that uses the key.
3. Optional: put two or three short samples of your own writing in `~/.config/outbox/voice.md`, and the rewrite will match their style. `--voice FILE` reads samples from another file, and `--no-voice` skips them.
4. For the Claude Code skill, install the plugin, then ask for a plain version of a draft or run `/outbox:outbox [audience] [text]`:

   ```
   /plugin marketplace add /path/to/your/outbox/clone
   /plugin install outbox@outbox
   ```

## Rewrite a draft

```
outbox draft.md                       for another engineer (default)
outbox --for polish draft.md          remove the AI habits, change nothing else
outbox --for team draft.md            operational detail, no code
outbox --for manager draft.md         three to five sentences: outcome, impact, ask
outbox --for funder draft.md          measured report register
outbox --for participant draft.md     warm, simple, tells them what to do
outbox --for team --instruction "The reader is Sam, who has not seen the code" draft.md
                                      a named audience, narrowed to one reader
outbox --for "a colleague skimming fifty profiles in one afternoon" draft.md
                                      a reader none of the names fits
cat draft.md | outbox                 read the draft from stdin
outbox --show-prompt --for funder     print the prompt without calling Gemini
```

Stdout is the rewrite and nothing else, so you can paste it as is. Stderr has the model's list of changes, a warning if an em dash survived or the rewrite was cut short, and a usage line with the token counts and the model that answered.

`--instruction "..."` adds a rule for one call, and can be given more than once. Use it for what the general rules cannot know: who exactly the reader is, a term they will not recognise, or a detail shown next to the text. For example, a task tracker can tell outbox not to repeat the status and due date that its row already shows. The model follows an instruction as a rule, whereas it only imitates the style of `--voice` samples.

`outbox --help` lists the other options (`--model`, `--thinking`, `--temperature`, `--timeout`) and every default.

## Check the rewrite before sending

The mistake that matters in any rewrite is a changed fact: a number that changed or appeared, a condition that went missing, a promise the draft never made. Read the whole rewrite against the draft, with the change list beside it.

- Compare with the draft itself, because the change list can miss a change, such as a short name expanded to an official-looking full one.
- Read the rewrite in full. Skimming it through `head`, `tail` or `grep` shows the lines you expected and hides the ones that changed.
- Do not run outbox on its own output. A second pass can swap a precise word for a vaguer one while reporting that nothing changed. To shorten a rewrite or aim it at someone else, run outbox on the original draft again.

## Audiences

Each name adds a paragraph about the reader to the prompt, ahead of the general rules. Where the two disagree, the paragraph wins.

- `engineer` (default): another engineer. Only the style changes. Every fact, number, file path, command and code block stays, and the text gets shorter only by the filler removed.
- `polish`: whoever the draft was written for. Only the wording changes. The structure, headings, lists and the content of every sentence stay, so the result is about as long as the draft.
- `team`: a teammate who runs programs and operations. It leads with what happened, why it matters and what is needed from them. It keeps every fact, date, name and link, drops code, paths and implementation detail unless one is the point, and aims for about a third of the draft's length.
- `manager`: a manager or director with thirty seconds to spare. Three to five sentences: the outcome, the impact or risk, and any decision or request, with the numbers and link needed to act. No code, paths, lists or headings.
- `funder`: a program officer who will quote the text. It reads like a research-impact report: every number says what it counts and in which population, the uncertainty and the as-of date are stated once, associations are not presented as causes, detection counts are given as minimums, and null results and caveats stay in. No promotional language, invented jargon or notes about the process.
- `participant`: a hackathon participant, often early in their career, often reading English as a second language, on a phone. Warm and addressed to "you": what this is and what they get, then what to do, with any deadline and link. Short paragraphs, no internal names, and the greeting and sign-off are kept.

To write for one particular reader, pass the closest name and describe the reader with `--instruction "The reader is ..."`. The name's rules still apply, and the instruction adds to them. The Claude Code skill does this whenever one of the names is close.

For a reader none of the names fits, pass a description of at least two words instead: `--for "a colleague skimming fifty profiles in one afternoon"`. The description replaces the named paragraph, so what it says about the reader, the style or the length overrides the general rules. Where it says nothing, outbox keeps the draft's content and structure, as `polish` does, but writes in the style the described reader expects and spells out shorthand. So if you want the text shorter, the description has to say so. A single word that is not a name is refused as a likely typo.

## Model

The default is `gemini-flash-latest`, Google's alias for the newest Flash release, previews included. The usage line names the model that actually answered (`gemini-flash-latest served by ...`), so you see a model change on the first call after it. For reproducible results, pass a fixed model id with `--model` or `$OUTBOX_MODEL`. `gemini-3.1-pro-preview` is the most capable option and `gemini-3.5-flash-lite` the cheapest.

Thinking defaults to `high`, because in testing `low` dropped facts and invented requests. Temperature defaults to 1.0, since Google's Gemini 3 guide warns that lowering it can make output worse.

outbox retries a network error or a 429, 500, 502, 503 or 504 response (waiting as long as `Retry-After` asks), up to four attempts in all. After that it exits with the error, or the start of the response body. A response slower than `--timeout` (120 seconds by default) is not retried: outbox exits and says so.

## How the prompt is built

The prompt Gemini receives has four parts, in this order:

1. The audience paragraph, marked as taking precedence over the rules. This settles conflicts such as the engineer paragraph's "do not shorten" against the rules' preference for cutting.
2. Your voice samples, if any.
3. All of `rules.md`, which ends by asking for the output format: the rewrite, a `--- changes ---` line, then the changed claims and notes on the wording.
4. Any `--instruction` rules.

`rules.md` is built on the "Claudish to English" spec from the claudish project, with rules from other sources added to the sections they fit. `THIRD-PARTY-NOTICES.md` lists every source, its license and what it contributed.

## Development

```
python3 -m unittest discover tests
```

The tests run offline against scripted responses. They also check the prompt's own text: they fail on an em dash in `rules.md`, the audience paragraphs or the text added to a described reader, and on a few fixed contrast phrases ("not just", "rather than") in the paragraphs and that text.

## License

AGPL-3.0, in `LICENSE`. `rules.md` and the audience paragraphs include text from four MIT-licensed projects and one GPL-3.0-licensed project, whose notices are in `THIRD-PARTY-NOTICES.md`. One further source, a gist with no license, is credited there without a notice.
