# Compatibility and native invocation

Checked 2026-10-16. Product behavior changes; these are the sources read for this
release, not a permanent entitlement statement.

| Question | Evidence | What this release can claim |
|---|---|---|
| Does ChatGPT have native skill invocation? | [Build skills](https://learn.chatgpt.com/docs/build-skills) and [Skills & Plugins](https://learn.chatgpt.com/docs/skills-and-plugins) describe `@` in ChatGPT and `$` in Codex | Yes, an official mechanism exists |
| Is Plus excluded from all skills? | [Learn pricing](https://learn.chatgpt.com/docs/pricing) marks Skills and Plugins available for Plus in its feature comparison | A blanket “Plus cannot use skills” claim is unsupported |
| Does this prove Plus can upload this skill into ordinary Chat on every surface? | No. [Help Center: Skills in ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt) currently lists eligible Business, Enterprise, Healthcare and Edu users, subject to availability | Official eligibility wording differs; this account-specific flow remains unverified |
| Is a folder enough for web/mobile Chat? | Build skills distinguishes standalone local discovery from plugin-bundled skills across Chat/Work surfaces | No automatic web installation follows from copying a local folder |
| Does a GitHub release put a plugin in the public directory? | [Package your plugin](https://developers.openai.com/plugins/build/plugins) separates local/repo marketplaces, workspace sharing and public directory submission | No; public-directory submission/review is separate |
| Is OpenAI API support included in a ChatGPT subscription? | [API Skills](https://developers.openai.com/api/docs/guides/tools-skills) documents a separate API execution integration | This package has the compatible folder shape; it does not create/upload an API skill or provide API credits |

The Learn pricing comparison is a broad Work/Codex feature matrix, not a specific
promise about custom upload in ordinary Chat. The Help Center eligibility text
must not be ignored when evaluating that narrower question. We therefore do
not promise native custom-skill `@` for a Plus account without an actual install
and invocation on the target surface.

## Local Codex / Work path

Run `python3 scripts/install.py --agent codex`. The destination is the current
documented user discovery path `~/.agents/skills/podcast-xmind`. This does
not edit configuration or overwrite an installed skill. Start a new chat if
the picker is stale. Use `$podcast-xmind <link or transcript>` in Codex;
the ChatGPT desktop surface may expose `@` selection according to its mode.

This release executed the skill's instructions and scripts inside the supplied
Codex/Work environment. It did not establish that a new picker entry appeared
in every local UI surface. A successful file copy is an installation artifact,
not a UI acceptance result.

## Plugin packaging path

Root `plugin.json` follows the portable manifest in OpenAI's package guide and
discovers `skills/`. `.agents/plugins/marketplace.json` points to the repo root
using `./`, relative to the marketplace root (not the JSON file's directory).
This is an authored distribution source, not a public directory listing.

With a functioning Codex CLI, the documented registration command is:

```sh
codex plugin marketplace add zachsaws/podcast-xmind --ref main
```

Then use the desktop Plugins Directory to select the marketplace, inspect and
install the package, and test in a new chat. Availability can vary by surface.
The PATH-installed CLI launcher failed to find its native executable during the
initial release. On 2026-10-16, diagnosis found the desktop application's working
bundled CLI. The new `python3 scripts/install_plugin.py` uses that executable
when available, or accepts `--cli /absolute/path/to/codex`. It registers this
repo as a local marketplace and installs `podcast-xmind@podcast-xmind`.

## Observed desktop diagnosis and repair, v0.1.2

The user reported the standalone skill was selectable in Work but absent in
Chat. Comparison with the locally installed Writing Craft package showed that
Writing Craft was a registered, installed and enabled plugin, while Podcast
XMind only had a standalone skill plus an unregistered repo marketplace. This
is a concrete installation difference and a likely cause of the observed
visibility gap; it does not prove all product surfaces use identical discovery.

The repair added Chinese plugin presentation metadata, registered the marketplace
and installed the plugin through the official CLI. The installation readback
reported version 0.1.2 with `installed: true` and `enabled: true`. Other parsed
configuration values were checked and preserved. The unchanged former standalone
installation was preserved outside the discovery path to avoid duplicate entries.
No Writing Craft files or settings were changed.

The computer-use tool refused access to the desktop application, so the Chat
picker could not be inspected. Restart the desktop app, open a new Chat draft,
type `@播客导图` and look under **Plugins**, not only Skills. This UI acceptance
step remains pending. The local installation is not proof of account-level
web/mobile synchronization or a public-directory listing.

ZIP releases provide both a single-folder skill and a portable-plugin bundle.
If an eligible UI offers a skill upload action, use the **skill ZIP**; do not
assume a skill uploader accepts a plugin ZIP. A portable-plugin ZIP needs a
host that accepts that format. We have checked archive structure, not every
product's upload UI. Workspace publishing and public directory publishing have
their own roles, confirmation flows and review requirements.

## Target-account acceptance (still to run)

1. On the intended Plus account and Chat surface, confirm a custom skill/plugin
   installation entry actually exists. Record the surface and app version.
2. Install through that supported entry. Do not interpret Projects instructions
   or a pasted GitHub URL as installation.
3. Start a fresh **Chat** conversation. Type `@` and select the actual skill or
   plugin entry, then provide the NASA example link.
4. Confirm full source retrieval or an honest access limitation, Chinese layered
   reading, evidence locations and a clear statement if scripts did not execute.
5. Repeat with a transcript excerpt. Confirm it remains partial. Repeat with
   an inaccessible episode link. Confirm no invented episode contents.

Until these are observed, desktop plugin installation is verified but Chat
invocation is not account-accepted. Use the local path now or the explicitly manual
[Chat fallback](chat-fallback.md).

## Claude Code and other hosts

`python3 scripts/install.py --agent claude` copies into `~/.claude/skills/`.
[Claude Code's official documentation](https://code.claude.com/docs/en/skills)
documents this directory and `/skill-name` invocation. No Claude-specific hooks
or required MCP servers are bundled. Live Claude Code execution has not been
verified. Hosts implementing [Agent Skills](https://agentskills.io/specification)
can use the folder, but network, filesystem, model and shell capabilities must
be checked independently. A standard manifest is not proof of equivalent quality
across models or a working transcription backend.
