# Podcast XMind

**Read the depth. Skip the filler.** Evidence-linked podcast reading with information ledgers and visible coverage boundaries.

[中文](README.md) · [Real output](examples/nasa/run/reading.md) · [Source-to-output demo](examples/synthetic/README.md) · [Downloads](https://github.com/zachsaws/podcast-xmind/releases)

![Source, ledger, layered reading, evidence](assets/cover.svg)

A short summary can lose the very detail you needed: a corrected number, a causal mechanism, a failed pilot, a caveat or a valuable side topic. This skill reads the supplied material in chunks, builds atomic information units, reorganizes by topic and checks the reading against the original.

The output has three layers: a **2–3 minute scan**, a **dynamic deep read** (usually 15–25 minutes for a substantive long episode), and **on-demand source evidence**. Short episodes need less; dense ones may need more. There is no fixed word-count cap or requirement to fit every topic into one thesis.

## Try it

Requires a skill-capable agent. Helper scripts require Python 3.10+, standard library only. No project API key, server, telemetry or model API integration is included; the host agent supplies reasoning and available tools.

```sh
git clone https://github.com/zachsaws/podcast-xmind.git
cd podcast-xmind
python3 scripts/install.py --agent codex
```

```text
$podcast-xmind <episode link or transcript file>
```

The installer copies the self-contained skill into `~/.agents/skills/podcast-xmind` and refuses to replace any existing path. Start a new session if discovery has not refreshed.

For Claude Code: `python3 scripts/install.py --agent claude`, then `/podcast-xmind <input>`. The directory follows [Claude Code's documented skill format](https://code.claude.com/docs/en/skills); a live Claude Code run has not been tested. Other [Agent Skills](https://agentskills.io/specification) hosts can load `skills/podcast-xmind/`. Tool availability varies.

## See the difference in actual artifacts

The [original synthetic excerpt](examples/synthetic/excerpt.txt) contains a host's mistaken premise, a correction, cost denominators, a failed pilot, an independent data-policy topic and an uncertain future statement. The [independently produced reading](examples/synthetic/run/reading.md) preserves those details. Inspect the [ledger](examples/synthetic/run/ledger.json) and [actual audit](examples/synthetic/run/audit.json). This is one inspectable example, not a comparative performance benchmark.

The [real NASA example](examples/nasa/run/reading.md) turns a complete publisher transcript into Chinese reading, retaining model limitations, learning through independent analysis and personal side topics. No timestamps were invented. [Acquisition and attribution](examples/nasa/README.md).

## ChatGPT Chat, Work and Plus

As checked on **2026-10-16**, official [Build skills](https://learn.chatgpt.com/docs/build-skills) documents `@` skill invocation in ChatGPT, `$` in Codex and plugins as the cross-surface distribution route. The [official plan table](https://learn.chatgpt.com/docs/pricing) marks Skills and Plugins available for Plus. Product docs do not prove a particular account has installed this package or exposes the required custom installation flow; some official eligibility wording also differs by page.

This repo ships `plugin.json`, a repo marketplace, a skill ZIP and a portable-plugin ZIP. **It is not listed in the public plugin directory and has not been installed and tested in the target account's native Chat `@` picker.** Local skill installation does not automatically sync a plugin to the web. Read [compatibility and acceptance steps](docs/compatibility.md).

If your Chat surface lacks custom installation, use the [manual Chat/Project fallback](docs/chat-fallback.md). That is an instruction workflow, not a native skill or plugin.

## Links are an entry point, not a guarantee

The agent first looks for a complete publisher transcript, lawful captions or a supplied file. Available host transcription tools can be used when appropriate. The included CLI does not download episodes or transcribe audio. Login, region, access controls and available tools can limit acquisition. Notes-only or excerpts produce explicitly partial reading; missing content is never reconstructed from a title or outside articles.

## Offline helpers

```sh
python3 skills/podcast-xmind/scripts/pdr.py prepare episode.vtt \
  --out runs/episode --scope partial --scope-note 'User-provided excerpt'
# Agent fills ledger.json and writes reading.md, then:
python3 skills/podcast-xmind/scripts/pdr.py audit \
  runs/episode/transcript.json runs/episode/ledger.json runs/episode/reading.md \
  --out runs/episode/audit.json
```

Supports UTF-8 TXT/MD, SRT, VTT and documented segment JSON. Original bytes, hashes, source positions and actual cue times are retained. `prepare` does not generate prose. `audit` checks structural accounting and exact excerpt/speaker matching; it cannot establish completeness, truth, semantic entailment, translation quality or audio fidelity. Coverage metrics use the agent-selected ledger as their denominator. [Contract](skills/podcast-xmind/references/ledger-contract.md) / [Evaluation](docs/evaluation.md).

## Reproduce the checks

```sh
python3 -m unittest discover -s tests -v
python3 scripts/verify_examples.py
python3 scripts/package.py --out dist
```

CI runs these checks on Python 3.10, 3.12 and 3.13. [Live Actions](https://github.com/zachsaws/podcast-xmind/actions). Packages are deterministic ZIPs with SHA-256 checksums; they exclude examples and private runs.

Please contribute specific, reproducible omissions using material you may share. [Contributing](CONTRIBUTING.md). Planned work starts with long-form, multi-speaker and multilingual evaluation, not unmeasured quality claims. Stars are welcome if the workflow is useful; no growth outcomes are promised. [Launch plan](docs/launch.md).

## Credits and license

Inspired by the fact-ledger and quote-verification ideas in [orange2ai/podcast-to-article](https://github.com/orange2ai/podcast-to-article). This project independently implements a different goal: reading retention and omission transparency rather than a single publishable article. [Design notes](docs/design-notes.md).

Original code, instructions and synthetic fixtures: [MIT](LICENSE). NASA source material retains its original status and conditions; see [NOTICE](NOTICE.md). No endorsement by NASA, OpenAI or Anthropic is implied.
