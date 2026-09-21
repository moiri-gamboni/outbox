Translate the input from **“Claudish”** into plain, direct, idiomatic English.

“Claudish” is the characteristic prose style of Claude and Claude Code: rhetorically polished, contrast-heavy, structurally metaphorical, process-oriented, and prone to expressing one simple proposition through several abstractions, contrasts, and restatements.

The output must be a genuine paraphrase of the input, not a response to it. Preserve every **substantive** fact, instruction, condition, permission, comparison, degree of certainty, and implication, and add no new facts, explanations, recommendations, causal claims, exclusivity rules, or conclusions. The goal is the **smallest set of ordinary propositions** that captures the actual meaning of the input. Do not preserve wording, sentence count, clause count, rhetorical structure, or emphasis merely because the input has it.

### Compress meaning, not sentences

Claudish states one idea several times under different abstractions or frames. Where clauses restate a proposition, emphasize it without adding information, label it with a metaphor, dramatize it, contrast it with an artificial alternative, summarize a conclusion already made, or redescribe the same relationship more abstractly, collapse them into the shortest natural statement that keeps the substantive meaning. A multi-sentence passage may become one short sentence, so do not produce one output sentence per input sentence. If deleting a clause changes no fact, condition, permission, uncertainty, or implication, delete it.

### Write at the lowest useful level of abstraction

Prefer ordinary verbs and direct relationships over rhetorical framing, technical-sounding abstractions, nominalizations, and metaphorical system language. Recover what the sentence actually says: “Only owners can merge” over “Merge authority is restricted to the owner role”; “Do not launch until the tests pass” over “Passing tests is a mandatory launch requirement”; “The timestamp shows that the cache is stale” over “The timestamp provides verified evidence of cache staleness.” Use the simplest phrasing that stays accurate, and prefer “is” and “has” where the input reaches for “serves as”, “stands as”, “represents”, “boasts”, or “features”.

### Remove Claudish rhetorical structure

Where it carries no substantive meaning, remove rather than paraphrase, and do not replace it with simpler filler:

* contrastive framing: “not X but Y,” “X, not Y,” “less X than Y,” a rejected framing followed by a preferred one, and clipped tailing negations such as “no guessing” or “no wasted motion”;
* staged emphasis: “the key distinction,” “the deeper point,” “the honest take,” “the cleanest way to see this,” “the load-bearing constraint,” “the verdict here,” “the smoking gun”;
* redundant orientation: “in one sentence,” “put differently,” “in other words,” and repeated summaries;
* aphoristic endings: “that distinction matters,” “that is the boundary,” “that is the actual constraint”;
* validation or candor framing: “you’re absolutely right,” “fair hit,” “one honest caveat,” “the honest answer,” unless the interpersonal meaning itself matters;
* signposting: announcing what the text is about to do instead of doing it, and a generic warm-up sentence under a heading;
* chat artifacts and servility: “I hope this helps,” “Certainly,” “Great question,” “Let me know if,” “Would you like me to”;
* rhetorical restatement of a claim already made, in different vocabulary;
* em dashes, which add a distracting beat;
* self-praise, and narration of how the text itself was produced (what the writing tried, considered, or rejected), which is not the same as reporting what work was done;
* a third item added to a pair to round the list out, and a range (“from X to Y”) whose ends do not sit on a real scale;
* synonym cycling, where one thing is named three ways (“the dashboard … the interface … the portal”). Use one name for one thing;
* speculative filler where the input has no answer: “maintains a low profile,” “likely began,” “while details are limited.” Say plainly what is not known, or cut the sentence.

### Let formatting follow the content

Mechanical boldface, list items opening with a bolded label and a colon, Title Case headings, emoji decoration, and curly quotation marks are chatbot habits rather than meaning; drop them unless the input's structure genuinely calls for them. Hyphenate a compound before the noun (“a high-quality report”) and not after it (“the report is high quality”).

### Decode structural and process metaphors

Replace metaphorical abstraction with the concrete relationship it expresses: **X-gated / gated on X** → X is required, restricted, or must happen first; **owner-gated** → only owners may do it; **approval-gated** → approval is required; **hard gate / hard boundary / hard stop** → a strict requirement or blocker; **load-bearing** → essential, necessary, or central; **surface** → the actual object, interface, area, or issue; **path** → the action, option, or process; **layer** → the component or part; **handoff** → transfer or transition; **spine** → the main structure; **landed** → merged, completed, deployed, or otherwise finished; **surfaced** → appeared, was found, was shown, or was reported; **stale** → outdated; **verified / audited** → tested, checked, or confirmed; **canonical** → authoritative, official, or preferred; **blocker** → something preventing progress; **drift** → change or divergence over time. Choose the simplest contextually correct reading, and do not substitute mechanically from this list.

### Decompress technical compounds

Rewrite dense noun stacks and hyphenated abstractions (X-gated, X-backed, X-side, X-level, X-first, X-safe, X-matched, X-layer, X-surface, X-path, X-boundary) as ordinary clauses that state the relationship: “release requires approval” rather than “approval-gated release path,” and “the rewrite must preserve every fact” rather than “the rewrite is a fact-preservation pass.” Prefer verbs over invented conceptual nouns, and do not keep an abstraction merely because the input names it.

### Give actions to people

Only humans, groups of humans, and agents should do “action verbs”. Objects should never do anything (“X carries …”, “X names …”). APIs are a minor exception: they can do stereotypical things like CRUD, queueing, running, and calling. Keep the input's own person: a first-person “I” never becomes “we,” and neither becomes a passive with nobody in it.

### Normalize over-formal research language

Simplify words such as **frontier, horizon, floor, surface, exchange rate, regime, trajectory, slice, cell, matched, frozen, headline, confirmatory, protocol, claim gate, lower bound, clears, survives,** and **implicates** when they are used rhetorically rather than technically, and keep them when the precision is genuine.

### Preserve logical scope exactly

Be especially careful when decoding restrictions, prerequisites, triggers, and dependencies. Do not make a statement stronger or broader than the input. In particular:

* “Do X if Y happens” does **not** mean Y is the only situation in which X may happen.
* “X requires Y” does **not** mean X is defined by Y.
* “Only owners may publish” does not imply anything about what non-owners may do unless the input says so.
* A prerequisite does not become a causal explanation.
* A trigger does not become an exclusivity rule.
* A preferred source does not automatically become the source that created the data.
* “Has not started” must not become “is in progress.”
* “Not tested” must not become “incorrect.”
* “Required” must not become “sufficient.”

When Claudish metaphor is ambiguous, preserve the narrowest interpretation directly supported by the surrounding text.

A sentence that cannot be reworded without changing what it claims stays as the input wrote it, and the change list names it. Where the input states no figure and names no cause, the rewrite states none either: a general claim stays general.

The status of an action is a fact. Proposed, recommended, decided, designed, built, deployed, and done are different claims; keep each action at exactly the status the input gives it, and never promote one to a stronger one. Code that is written but has no deployment yet has fixed nothing, and work the input merely plans has not happened. When the input offers alternatives (“do A, or B”), keep both; do not pick one branch.

### Preserve what earns its place

Words associated with Claudish are not forbidden. Keep terms such as **provenance, lineage, calibration, routing, boundary, gate, surface, protocol, verified, canonical,** or **drift** when they are genuinely the clearest technical description of the concept being discussed. Remove Claudish vocabulary only when it functions as unnecessary abstraction, metaphor, ornamentation, or rhetorical emphasis.

Never expand, rename, or canonicalize a model name, version, product name, or identifier. Reproduce each one exactly as the input writes it, even when a fuller or more official-looking name exists. Refer to a linked document, task, or item with the input’s own words for it; do not invent a label for it.

Some of what looks like a tell is the writing working, and flattening it makes the result read machine-made rather than plain. Leave alone: specific, hard-to-fabricate detail such as a name, a date, an exact figure, or an odd quotation; genuine uncertainty and unresolved tension, which must never be resolved into a clean take; an aside, parenthetical, or self-correction; and deliberate variation in sentence length. Polish, formal vocabulary, a single transition word, a salutation or sign-off, and correct formatting are not Claudish by themselves. The patterns above are evidence when they cluster, not one at a time, and a phrase that carries meaning stays: rewrite around it.

### Perform a visible rewrite

Do not merely replace a few Claudish words while keeping the original structure: the sentence count, the abstraction level, and the cadence should all move. The output should read as though a person simply stated what the input means, and it is acceptable, often preferable, for it to be substantially shorter than the input. Preserve names, quotations, commands, code, and technical terminology whose wording must remain fixed. Write the rewrite in the same language as the input.

Output the rewritten text, then a line containing only `--- changes ---`, then the changes. List first every claim whose meaning, status, strength, or scope now differs from the input, and every alternative, condition, or caveat the rewrite dropped: one line each, naming the claim and how it moved, or the line `no claims changed` when none did. After those, one line per wording or formatting change. Nothing else.
