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
        ledger = json.loads((run / 'ledger.json').read_text(encoding='utf-8'))
        reports = [run / 'reading.md', *sorted(run.glob('reading.*.md'))]
        for report in reports:
            result = pdr.audit(manifest, ledger, report.read_text(encoding='utf-8'))
            audit_name = report.name.replace('reading', 'audit', 1).replace('.md', '.json')
            saved = json.loads((run / audit_name).read_text(encoding='utf-8'))
            assert result == saved, f'{report}: committed audit is stale'
            print(run.parent.name, report.name, result['status'], result['metrics'])
            failed |= result['status'] != 'pass'
    return int(failed)


if __name__ == '__main__':
    sys.exit(main())
