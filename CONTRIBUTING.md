# Contributing

Useful contributions begin with a reproducible gap: an important detail omitted,
an unsupported claim, a wrong speaker, a malformed transcript or a misleading
source-coverage statement. Include the source span, actual output, expected
behavior and why the difference changes a reader's understanding.

Share only material you have permission to redistribute. Redact private names,
identifiers and credentials; do not attach private recordings or third-party
full transcripts to a public issue. Use the smallest synthetic reproduction when
rights or privacy are unclear. Do not claim a fix is accurate only because its
ID markers pass the audit.

For code changes, run:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/verify_examples.py
python3 scripts/package.py --out dist
```

For skill changes, test an actual reading with source material the agent has not
seen, inspect the source and output in both directions, and document both failures
and limitations. Keep the skill folder self-contained. New downloader, paid ASR
or cloud-upload integrations require explicit capability, privacy and cost
boundaries; do not make them implicit prerequisites for local text use.
