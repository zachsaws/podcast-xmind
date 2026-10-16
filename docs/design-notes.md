# Design notes and reference review

Reference read on 2026-10-16:
[orange2ai/podcast-to-article](https://github.com/orange2ai/podcast-to-article),
commit [`efc4391`](https://github.com/orange2ai/podcast-to-article/tree/efc43919962e8356058057c4b5fd32c57876e6b7)
(commit date 2026-10-08). Read README, SKILL.md, references/style-rules.md,
references/example.md, scripts/prep_transcript.py and scripts/check_style.py.

The reference is thoughtful about preserving concrete details, building a fact
ledger before writing and checking quote/speaker attribution. Its example even
discusses misattributing a host's words to the guest. Those are relevant problems.
Its principal product, however, is a publishable article. This project's product
is a reader's recoverable understanding of an episode.

| Observed design in reference | Decision here |
|---|---|
| Fact ledger before prose | Keep the idea; use atomic units with source spans, claim type, importance and disposition |
| One main narrative determines inclusion | Map all substantive topics; an independent aside can remain its own section |
| Target 2500–3000 Chinese characters | Dynamic length and layered reading; preserve a separate short path |
| Tight constraints on prose style | Use readability guidance; do not mistake style-regex results for retention |
| Original quotes and speaker calibration | Preserve attribution on contestable claims, exact evidence and uncertainty |
| User chooses article direction | Default reading scope is all topics, allowing a link-only request without an editorial approval loop |
| Subtitle cleanup and neighboring dedup | Keep immutable original, repeated cues and actual cue ranges; deduplicate meaning later |
| Style checker plus human checks | Structural accounting tool plus explicit two-way semantic review |

The reference's timestamp helper also illustrates a fragile format boundary:
`MM:SS.mmm` and `HH:MM:SS` need distinct treatment. Its three-component branch
interprets decimal components as hours/minutes/seconds; that can misinterpret
short VTT times. Our normalizer parses colon components first and decimal seconds
within the final component. This is a code-reading finding, not an executed
benchmark of that project.

We did not validate the reference's language-style corpus statistics, popularity
claims or quality scores, and do not repeat them as established measurements.
No reference code or long text passages were copied into the implementation.
This is an independent design inspired by a shared evidence-led approach, not
a claim that publishable-article workflows are inferior for their intended task.

## Deliberate limits

The host agent performs acquisition and semantic work. A universal downloader,
ASR engine, model router, vector database, background daemon and custom UI would
add dependencies without proving retention. The first release therefore provides
one focused skill, deterministic preparation/audit, inspectable outputs and a
portable distribution bundle. Evidence of recurring failures should determine
which adapter or evaluation investment comes next.
