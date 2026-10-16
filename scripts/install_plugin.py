#!/usr/bin/env python3
"""Register this local marketplace and install its skill-only plugin via Codex."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def find_cli(explicit=None):
    if explicit:
        candidates = [explicit]
    else:
        candidates = [os.environ.get('CODEX_CLI_PATH'),
                      '/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex',
                      '/Applications/Codex.app/Contents/Resources/codex', shutil.which('codex')]
    for candidate in candidates:
        if candidate and Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return str(Path(candidate).resolve())
    raise ValueError('No executable Codex CLI found; provide --cli /absolute/path/to/codex')


def install(cli, root):
    results = []
    commands = [
        ['plugin', 'marketplace', 'add', str(root), '--json'],
        ['plugin', 'add', 'podcast-xmind@podcast-xmind', '--json'],
        ['plugin', 'list', '--marketplace', 'podcast-xmind', '--json']]
    for command in commands:
        result = subprocess.run([cli, *command], capture_output=True, text=True)
        if result.returncode:
            # Do not dump unrelated diagnostic streams or environment settings.
            raise ValueError('Codex command failed: ' + ' '.join(command[:3]) +
                             '\n' + (result.stdout or result.stderr)[-2000:])
        try:
            results.append(json.loads(result.stdout))
        except ValueError:
            results.append(result.stdout.strip())
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli', help='Codex executable; defaults to host CLI discovery')
    args = parser.parse_args()
    try:
        root = Path(__file__).resolve().parents[1]
        results = install(find_cli(args.cli), root)
        print(json.dumps({'commands': results}, ensure_ascii=False, indent=2))
        print('Plugin registration completed. Refresh/restart the desktop app and verify the Chat @ picker.')
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
