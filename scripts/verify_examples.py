#!/usr/bin/env python3
"""Re-normalize committed examples and audit their actual reading artifacts."""
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pdr', ROOT / 'skills/podcast-xmind/scripts/pdr.py')
pdr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pdr)


def main():
    failed = False
    directories = sorted((ROOT / 'examples').glob('*/run'))
    if not directories:
        raise ValueError('No committed examples found')
    for run in directories:
        manifest = json.loads((run / 'transcript.json').read_text(encoding='utf-8'))
        source = manifest['source']
        original = (run / 'source.original').read_bytes()
        rows = pdr.normalize(original.decode('utf-8-sig'), Path(source['input_name']).suffix)
        assert rows == manifest['segments'], f'{run}: source does not reproduce segments'
        assert pdr.digest(original) == source['original_sha256'], f'{run}: original digest mismatch'
        result = pdr.audit(manifest, json.loads((run / 'ledger.json').read_text(encoding='utf-8')),
                           (run / 'reading.md').read_text(encoding='utf-8'))
        saved = json.loads((run / 'audit.json').read_text(encoding='utf-8'))
        assert result == saved, f'{run}: committed audit is stale'
        print(run.parent.name, result['status'], result['metrics'])
        failed |= result['status'] != 'pass'
    return int(failed)


if __name__ == '__main__':
    sys.exit(main())
