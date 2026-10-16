# Source acquisition and scope

Use host capabilities; do not claim a universal podcast downloader. Tool access,
login, region, transcript availability and transcription capacity vary by host.

| Input | First action | Honest fallback |
|---|---|---|
| Publisher / Xiaoyuzhou / Apple / Spotify episode link | Read episode metadata, find publisher site and full transcript | Search the exact title + publisher for a public transcript; notes alone remain notes |
| YouTube episode | Obtain actual captions using available lawful tools, note human/automatic and language | Ask for caption export/audio when the host cannot retrieve them |
| RSS feed | Find the **requested episode**, inspect transcript/episode links and enclosure | For a feed without episode selection, identify candidates and ask which one; never process a random episode |
| Direct audio / uploaded audio | Use available transcription tool with provenance and real segment times | State that audio exists but no transcript can be produced in this environment |
| TXT / MD | Preserve original text and paragraph/line positions | Unknown timestamps and speaker identities stay unknown |
| SRT / VTT | Preserve cue times and explicit voice labels | Missing or malformed cues fail visibly; don't discard them silently |
| ASR JSON | Use `segments: [{text, start?, end?, speaker?}]` | Other vendor formats require an explicit adapter, not silent interpretation |

When browsing a transcript page, follow pagination and expand collapsed text.
Save the actual transcript, not navigation, related episodes or image captions.
Spot-check first and last turns and topic transitions against the page. Record
how the transcript boundaries were selected. A tool's truncated response does
not establish full access. Retrieve remaining ranges or mark partial.

`--scope full` is an operator declaration requiring `--scope-note`, such as
“publisher transcript read from intro through closing; audio not compared”.
`--scope partial` describes an excerpt or missing spans. `--scope unknown` is
the default when completeness is not established. Show notes cannot be full.
For notes alone, use `--source-kind show_notes --scope partial` and say that
coverage applies to notes, not to the episode. Do not use elapsed cue coverage
as a content-retention measure: subtitles can have legitimate silent gaps.

Speaker labels are evidence, not verified identities. Keep `Speaker 1` if that
is all the transcript says. Resolve names only from explicit introductions or
documented publisher labels. Do not guess from style, turn-taking, accent,
voice or what a host “would probably say”. ASR excerpts are transcript-exact,
not audio-verified quotations. If audio was not checked, say so.

Correct important ASR errors only with evidence. Keep original wording, proposed
correction and reason separate; an external correction never changes what the
speaker actually said. Use ranges for approximate cue locations and disclose
that they locate a cue, not the exact word. Unknown time is a segment reference.

Downloaded recordings and private transcripts stay in a user-selected local run
directory. No telemetry, embedded analytics, automatic cloud upload or provider
API calls are included in the bundled code. A host/provider may still process
material under its own terms. Publish examples only with redistribution rights;
use synthetic material for unrestricted regression fixtures.
