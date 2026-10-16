# Executable contract (v1)

Python 3.10+, standard library only. Commands run from any working directory
when the script path is absolute. Paths below are examples, not mandatory names.

```sh
python3 skills/podcast-xmind/scripts/pdr.py prepare episode.vtt \
  --out work/episode --scope partial --scope-note 'User-provided excerpt' \
  --source-url 'https://example.org/episode'
python3 skills/podcast-xmind/scripts/pdr.py audit \
  work/episode/transcript.json work/episode/ledger.json work/episode/reading.md \
  --out work/episode/audit.json
```

`prepare` creates a new directory and refuses to overwrite one. It preserves
`source.original`, records its SHA-256, creates normalized `transcript.json`,
bounded `chunks.json` and an unfinished `ledger.json`. It never calls an LLM.
The original file is UTF-8, optionally with BOM. Invalid bytes are an error.
File extension selects TXT/MD, SRT, VTT or JSON; binary/audio is rejected.
Source text is never executed. No de-duplication occurs during normalization.

Each normalized segment has `id`, `text`, `speaker` (string or null), `start`
and `end` (seconds or null), `line_start`, `line_end`. Long plain-text paragraphs
are split into bounded segments without interpolating timestamps. A source cue
with several explicit VTT voice labels becomes multiple segments sharing its
actual cue range. Repeated ASR cues remain separate; merge their meaning later.

Chunks have `core_ids` to extract and `context_ids` for neighboring context.
Every segment belongs to exactly one core chunk. Overlap is not additional source
coverage. Read the actual segment text from `transcript.json` for every ID.

An example unit (quotes must exactly match the normalized source, apart from
Unicode normalization and whitespace):

```json
{
  "id": "U001",
  "topic": "Unit economics",
  "kind": "fact",
  "importance": "critical",
  "claim": "Guest reports $2 per completed job, not per request.",
  "speaker": "Guest",
  "evidence": [{"segment_id": "S0001", "quote": "$2 per completed job"}],
  "disposition": "included",
  "reason": "",
  "duplicate_of": null
}
```

Ledger root: `schema_version: 1`, `reviewed_segments: ["S0001", ...]`,
`review_notes: {"S0002": "Music only"}`, `units: [...]`.
All segment IDs must be reviewed exactly once in the final ledger. `kind` is
`fact|opinion|speculation|question`; `importance` is `critical|important|optional`.
All units need evidence and attribution, including excluded units. Known
segment speakers must match `speaker`; if evidence combines speakers, split
the unit. A missing source label requires null, not a guessed name. If the source
explicitly labels an anonymous turn `Speaker 1` or `Unknown speaker`, preserve
that string in both transcript and ledger; explain that identity is unverified.

`disposition` is `included|excluded|duplicate`. Critical and important units
must appear in the deep-read prose; only optional units can be excluded with
a concrete `reason`. True duplicate units need `duplicate_of` referencing an
included unit, a reason and the same topic. Equivalence is a semantic judgment
the checker cannot establish. Do not call corrections or counterarguments duplicates.
Each topic that has non-duplicate units must be represented by an included unit.

Place visible `Source coverage: full`, `partial` or `unknown` in the report;
it must agree with the manifest. Use exactly one ordered pair of report markers:

```md
<!-- deep-read:start -->
The guest's number refers to completed jobs. [U001](#u001)
<!-- deep-read:end -->

<a id="u001"></a>
U001 — Guest, S0001, exact excerpt; original source link.
```

The audit checks manifest digest, original-file digest, segment IDs and ordering,
review accounting, unit fields, speaker consistency, exact excerpt matching,
valid duplicate targets, important-unit inclusion, topic inclusion, report scope
and evidence-ID presence **inside** the deep-read region. Appendix-only IDs do
not count. Unknown report IDs are errors. Exit 0 = structural pass, 1 = audit
failure, 2 = invalid input/usage; JSON diagnostics include errors and warnings.

Metrics count **agent-selected units**, not all information in the episode.
`retained_unique_units / eligible_unique_units` and reviewed segments are
accounting metrics only. Semantic completeness, excerpt entailment, surrounding
prose accuracy, transcription quality and importance assignment require review
against raw material. Never advertise these metrics as an accuracy score.
