# CLAUDE.md

`outbox` is one Python script (standard library only) that builds a prompt from an audience paragraph, optional voice samples, `rules.md` and any `--instruction` rules, and sends the draft to Gemini. `skills/outbox/SKILL.md` is how a Claude Code session uses it. README.md is for users; this file is for changing the code.

## Commands

```
python3 -m unittest discover tests      # offline, against scripted Gemini responses
./outbox --show-prompt --for team       # the exact prompt, no request made
```

## Conventions

- **Public repo.** No personal, employer or machine names in the tree or in commit messages; a pre-push hook on the clone refuses them.
- **The prompt follows its own rules.** An edit to `rules.md`, an audience paragraph or the described-reader text must pass the rules it adds to; the tests catch the em dash and "not X but Y" cases.
- **A call without `--instruction` builds the same prompt as before.** Other tools call outbox with fixed arguments, so a change meant for one caller goes behind a flag.
- **One home per fact.** Flags and defaults go in `--help`, user-facing behaviour in the README, and how a session should run the tool in the skill. The skill gets a line only if a session would otherwise use the tool wrongly.
- **Sessions load the installed plugin, not this clone.** After a skill change, push, then `claude plugin update outbox@<marketplace>`; running sessions keep the copy they loaded until restarted.
