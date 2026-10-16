# What was actually evaluated

The release has three distinct evidence levels. None is an episode-recall score.

## Deterministic checks

Run `python3 -m unittest discover -s tests -v`. Tests exercise real transformations
and failure cases: fractional VTT/SRT times, voice tags, UTF-8 BOM/CRLF, unknown
labels, duplicate cues and numeric-only text, malformed input, chunk core
conservation, scope guards, fabricated quotes, speaker swaps, unreviewed segments,
appendix-only citations, omitted important units, cyclic duplicates, transcript
changes, CLI diagnostics, no-overwrite installation and reproducible archives.

Run `python3 scripts/verify_examples.py` to re-normalize committed source bytes,
compare actual segment content and recompute the saved audits. The exact audit
artifact is compared, so a changed report or stale result fails the check.
CI runs these on Python 3.10, 3.12 and 3.13. Check live Actions for completion;
local success alone is not evidence that remote CI passed.

## Independent forward test

A separate agent was given the skill and an original synthetic excerpt, with
external access prohibited. It generated an actual reading and ledger and ran
the bundled audit. Eight supplied paragraphs yielded eleven selected information
units in four topics. The final audit passed; original source and output remain
in `examples/synthetic/`.

Observed behavior retained a numerical correction, reporting date, cost
denominator, conditional mechanism, negative pilot, independent data topic,
deletion exception and uncertain future statement. It did not execute a hostile
instruction embedded in the source. This is one observed behavior, not a security
guarantee or statistically estimated accuracy.

The first audit failed because instructions conflated a missing speaker with a
literal `Unknown speaker` label. The artifact was repaired by preserving the
literal label while leaving identity unverified; the contract was subsequently
clarified. The initial failure is retained as diagnostic history and is not a
failure of the final artifact. [Independent observations](../examples/synthetic/independent-test.md).

## Real source, cross-language reading

The project author retrieved the complete publisher text of NASA's episode 181,
read all 88 paragraphs across three core chunks, built 34 ledger entries and
authored a Chinese reading. Thirty-two entries are retained, one opening excerpt
is a duplicate of the ending, and one greeting is explicitly excluded. Nine
substantive themes plus introductory metadata remain represented.

The author reread the source and report in both directions, including model
scope, the “most of the time” public-course qualifier, supervised responsibility,
personal “probably” wording and the photo aside. Audio, external technical
claims and translation accuracy were not independently evaluated by a second
reviewer. [Source record](../examples/nasa/README.md).

## Known gaps and next useful evaluation

No long-episode holdout, user acceptance study, cross-model comparison, ASR
word-error analysis or controlled comparison with the reference project has
been run. Neither the ledger's unit count nor its retention fraction establishes
the number of important ideas that were never extracted. Importance assignment,
duplicate equivalence and whether evidence supports a claim are semantic tasks
the script cannot certify.

Next evaluation should use rights-cleared long, multilingual and adversarial
multi-speaker transcripts. A human reviewer should create an independent list
of consequential units before seeing the agent ledger. Compare omissions and
unsupported additions against that list; keep full-source and partial-source
cases separate. Report per-case counts and examples, not a single inflated
“coverage” score. Changes should be driven by failures on held-out material.
