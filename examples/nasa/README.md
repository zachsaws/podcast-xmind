# Real link → Chinese reading

Source: [NASA, Small Steps, Giant Leaps — Episode 181: Passing Down Knowledge](https://www.nasa.gov/podcasts/small-steps-giant-leaps/episode-181-passing-down-knowledge/),
published 2026-09-02; retrieved 2026-10-16. Host Andres Almeida interviews
Heather Koehler about transferring engineering knowledge. [Read the output](run/reading.md).

## What was acquired

The publisher's HTML page was retrieved and paragraph text decoded with Python's
standard-library HTML parser. The selected span begins `[Soft intro music]` and
ends `Three. Two. One. This is an official NASA podcast.` Navigation, imagery
captions outside paragraph text and related content were excluded. First/last
turns and the interior topic sequence were checked against the page.

`source.json` contains all 88 selected paragraphs, in order. Explicit variants
`Host Andres Almeida`/`Host` map to Andres Almeida;
`Heather Koehler`/`Koehler` map to Heather Koehler. Unlabelled continuation
paragraphs inherit the preceding explicitly identified turn, after inspection
of the complete transcript. Intro music has no speaker. This HTML acquisition
step is a documented one-case preparation, not a universal podcast adapter.

No audio was downloaded or listened to; no timecodes were supplied by the page
and none were inferred. “Full” describes the complete publisher transcript,
not independent agreement with the episode's audio. Source facts were not
externally verified. [Material status and credit](../../NOTICE.md).

## Reproduce preparation

From the repository root, use a fresh output directory:

```sh
python3 skills/podcast-xmind/scripts/pdr.py prepare examples/nasa/source.json \
  --out work/nasa-repro --scope full --chunk-chars 6000 \
  --scope-note 'Complete publisher transcript from intro to outro; audio not compared' \
  --source-url 'https://www.nasa.gov/podcasts/small-steps-giant-leaps/episode-181-passing-down-knowledge/'
```

Read the actual segments and generate your own ledger/reading using the skill.
The author-created example has 34 entries: 32 retained, one duplicate and one
excluded greeting. The report retains nine substantive themes plus introductory
metadata. These are editorial counts, not a ground-truth recall denominator.

`python3 scripts/verify_examples.py` compares normalized segments to the
retained original and recomputes the existing ledger/report audit. It does not
regenerate the prose or pretend the model output is deterministic.
