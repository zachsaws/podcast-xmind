import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/podcast-deep-reader/scripts/pdr.py"
spec = importlib.util.spec_from_file_location("pdr", SCRIPT)
pdr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pdr)


class TranscriptTests(unittest.TestCase):
    def test_fractional_vtt_and_voice(self):
        rows = pdr.normalize('WEBVTT\n\nturn\n00:01.500 --> 00:03.050 align:start\n<v Host>Question?</v>\n<v Guest>A &amp; B.</v>\n', '.vtt')
        self.assertEqual([r['speaker'] for r in rows], ['Host', 'Guest'])
        self.assertEqual(rows[0]['start'], 1.5)
        self.assertEqual(rows[1]['end'], 3.05)
        self.assertEqual(rows[1]['text'], 'A & B.')

    def test_srt_crlf_bom_prepare(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / 'a.srt'
            raw = '\ufeff1\r\n00:00:01,500 --> 00:00:02,750\r\nGuest: 80 accounts.\r\n'.encode()
            src.write_bytes(raw)
            out = Path(d) / 'run'
            pdr.prepare(src, out)
            self.assertEqual((out / 'source.original').read_bytes(), raw)
            obj = json.loads((out / 'transcript.json').read_text())
            self.assertEqual(obj['segments'][0]['end'], 2.75)
            with self.assertRaises(FileExistsError):
                pdr.prepare(src, out)

    def test_no_timestamp_invention(self):
        rows = pdr.normalize('Guest: 你好。\n\nA second unlabelled paragraph.', '.md')
        self.assertEqual(rows[0]['speaker'], 'Guest')
        self.assertIsNone(rows[1]['speaker'])
        self.assertTrue(all(r['start'] is None and r['end'] is None for r in rows))

    def test_plain_timestamp_and_turns(self):
        rows = pdr.normalize('[01:02] **Host:** Ask?\nGuest: Answer.\nContinuation.', '.txt')
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['start'], 62)
        self.assertEqual(rows[1]['text'], 'Answer.\nContinuation.')

    def test_keep_repeated_cues_and_numeric_content(self):
        text = '1\n00:00:00,000 --> 00:00:01,000\n1000\n\n2\n00:00:01,000 --> 00:00:02,000\n1000\n'
        self.assertEqual([r['text'] for r in pdr.normalize(text, '.srt')], ['1000', '1000'])
        self.assertEqual(pdr.normalize('2026', '.txt')[0]['text'], '2026')

    def test_invalid_cues_fail_without_silent_loss(self):
        for text in ['1\n00:00:02,000 --> 00:00:01,000\nA',
                     'bad cue\nNot a transcript',
                     '1\n00:61:00,000 --> 00:62:00,000\nA',
                     '1\n00:00:00,000 --> 00:00:01,000\n']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                pdr.normalize(text, '.srt')

    def test_json_unknown_speaker(self):
        rows = pdr.normalize('{"segments":[{"text":"Maybe","start":0,"end":1}]}', '.json')
        self.assertIsNone(rows[0]['speaker'])

    def test_bad_json_times(self):
        for start in [True, -1, float('nan'), '00:01']:
            with self.subTest(start=start), self.assertRaises(ValueError):
                pdr.normalize(json.dumps({'segments': [{'text': 'A', 'start': start}]}), '.json')

    def test_empty_and_audio_rejected(self):
        for text, ext in [('', '.txt'), ('sound', '.mp3'), ('{}', '.json')]:
            with self.subTest(ext=ext), self.assertRaises(ValueError):
                pdr.normalize(text, ext)

    def test_chunk_core_conserves_all_content(self):
        text = '\n\n'.join('Guest: ' + str(i) + '字' * 3000 for i in range(9))
        rows = pdr.normalize(text, '.txt')
        grouped = pdr.chunks(rows, budget=6000, overlap=1)
        ids = [sid for c in grouped for sid in c['core_ids']]
        self.assertEqual(ids, [r['id'] for r in rows])
        self.assertTrue(grouped[0]['context_ids'])
        long = '文' * 12001
        self.assertEqual(''.join(r['text'] for r in pdr.normalize(long, '.txt')), long)

    def test_scope_guards(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / 'a.txt'; src.write_text('Text')
            with self.assertRaises(ValueError):
                pdr.prepare(src, Path(d) / 'r', scope='full')
            with self.assertRaises(ValueError):
                pdr.prepare(src, Path(d) / 'r', scope='full', scope_note='Notes', source_kind='show_notes')


class AuditTests(unittest.TestCase):
    def setUp(self):
        rows = pdr.normalize('Guest: 80 paying accounts, not 1000.', '.txt')
        self.manifest = dict(schema_version=1, source=dict(kind='transcript', scope='partial', scope_note='Excerpt'),
                             segments=rows, segments_sha256=pdr.segment_digest(rows))
        self.ledger = dict(schema_version=1, reviewed_segments=['S0001'], units=[
            dict(id='U001', topic='Growth', kind='fact', importance='critical',
                 claim='80 paying accounts', speaker='Guest',
                 evidence=[dict(segment_id='S0001', quote='80 paying accounts, not 1000.')],
                 disposition='included', reason='', duplicate_of=None)])
        self.report = 'Source coverage: partial\n<!-- deep-read:start -->\n80 paying accounts. [U001](#u001)\n<!-- deep-read:end -->'

    def run_audit(self):
        return pdr.audit(self.manifest, self.ledger, self.report)

    def assert_error(self, part):
        self.assertTrue(any(part in e for e in self.run_audit()['errors']), self.run_audit())

    def test_valid_partial_is_not_full_coverage(self):
        result = self.run_audit()
        self.assertEqual(result['status'], 'pass')
        self.assertEqual(result['scope'], 'partial')
        self.assertTrue(any('not established' in w for w in result['warnings']))

    def test_fabricated_quote(self):
        self.ledger['units'][0]['evidence'][0]['quote'] = '1000 paying customers'
        self.assert_error('quote does not match')

    def test_speaker_swap(self):
        self.ledger['units'][0]['speaker'] = 'Host'
        self.assert_error('speaker mismatch')

    def test_unknown_speaker_not_inferred(self):
        self.manifest['segments'][0]['speaker'] = None
        self.manifest['segments_sha256'] = pdr.segment_digest(self.manifest['segments'])
        self.assert_error('speaker mismatch')

    def test_appendix_citation_does_not_count(self):
        self.report = self.report.replace('[U001](#u001)', '') + '\nAppendix: [U001](#u001)'
        self.assert_error('absent from deep-read')

    def test_unseen_segment(self):
        self.ledger['reviewed_segments'] = []
        self.assert_error('Unreviewed segments')

    def test_important_cannot_be_excluded(self):
        self.ledger['units'][0].update(disposition='excluded', reason='Too long')
        self.assert_error('cannot be excluded')

    def test_unknown_report_id(self):
        self.report = self.report.replace('80 paying', '[U999] 80 paying')
        self.assert_error('Unknown report citation')

    def test_duplicate_cycle_is_rejected(self):
        self.ledger['units'][0].update(disposition='duplicate', reason='Same', duplicate_of='U001')
        self.assert_error('duplicate target')

    def test_transcript_edit_is_detected(self):
        self.manifest['segments'][0]['text'] = '1000 paying'
        self.assert_error('digest mismatch')

    def test_scope_disclosure(self):
        self.report = self.report.replace('Source coverage: partial', 'Source coverage: full')
        self.assert_error('visibly disclose')

    def test_bad_markers(self):
        self.report += '\n<!-- deep-read:start -->'
        self.assert_error('exactly one pair')

    def test_duplicate_ids(self):
        self.ledger['units'].append(copy.deepcopy(self.ledger['units'][0]))
        self.assert_error('duplicate unit ID')

    def test_unicode_whitespace_equivalence(self):
        self.ledger['units'][0]['evidence'][0]['quote'] = '80  paying\naccounts'
        self.assertEqual(self.run_audit()['status'], 'pass')

    def test_cli_missing_original_and_exit_status(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            pdr.write_json(d / 'transcript.json', self.manifest)
            pdr.write_json(d / 'ledger.json', self.ledger)
            (d / 'reading.md').write_text(self.report)
            run = subprocess.run([sys.executable, str(SCRIPT), 'audit', str(d / 'transcript.json'),
                                  str(d / 'ledger.json'), str(d / 'reading.md')], capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)
            self.assertIn('Original source missing', run.stdout)

    def test_cli_malformed_input_is_actionable(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'bad.json'; path.write_text('[]')
            run = subprocess.run([sys.executable, str(SCRIPT), 'audit', str(path), str(path), str(path)],
                                  capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertNotIn('Traceback', run.stderr)


class DistributionTests(unittest.TestCase):
    def test_install_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            run = subprocess.run([sys.executable, str(ROOT / 'scripts/install.py'), '--dest', d], capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue((Path(d) / 'podcast-deep-reader/SKILL.md').is_file())
            again = subprocess.run([sys.executable, str(ROOT / 'scripts/install.py'), '--dest', d], capture_output=True)
            self.assertNotEqual(again.returncode, 0)

    def test_packages_are_reproducible_and_self_contained(self):
        import zipfile
        with tempfile.TemporaryDirectory() as d:
            command = [sys.executable, str(ROOT / 'scripts/package.py'), '--out', d]
            subprocess.run(command, check=True, capture_output=True)
            first = (Path(d) / 'SHA256SUMS').read_bytes()
            subprocess.run(command, check=True, capture_output=True)
            self.assertEqual(first, (Path(d) / 'SHA256SUMS').read_bytes())
            with zipfile.ZipFile(Path(d) / 'podcast-deep-reader-skill.zip') as z:
                names = z.namelist()
                self.assertEqual(names.count('podcast-deep-reader/SKILL.md'), 1)
                self.assertTrue(any(n.endswith('/scripts/pdr.py') for n in names))
                self.assertFalse(any('__pycache__' in n or '/runs/' in n for n in names))
            with zipfile.ZipFile(Path(d) / 'podcast-deep-reader-plugin.zip') as z:
                self.assertIn('podcast-deep-reader/plugin.json', z.namelist())
                self.assertIn('podcast-deep-reader/skills/podcast-deep-reader/SKILL.md', z.namelist())


if __name__ == '__main__':
    unittest.main()
