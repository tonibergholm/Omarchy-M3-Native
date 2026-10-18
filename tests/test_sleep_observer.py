"""Offline lifecycle/storage checks; these do not qualify native sleep signals."""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    'sleep_observer', Path(__file__).resolve().parents[1] / 'tools/sleep-observer.py')
observer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(observer)


class RecorderTests(unittest.TestCase):
    def test_pairing_and_clock_delta_across_two_cycles(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'events.jsonl'
            recorder = observer.Recorder(path)
            states = [{'boottime_s': 100, 'monotonic_s': 100},
                      {'boottime_s': 132, 'monotonic_s': 102},
                      {'boottime_s': 140, 'monotonic_s': 110},
                      {'boottime_s': 202, 'monotonic_s': 112}]
            with patch.object(observer, 'snapshot', side_effect=states):
                for sleeping in (True, False, True, False):
                    recorder.transition(sleeping)
            recorder.close()
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual([row['cycle'] for row in rows], [1, 1, 2, 2])
            self.assertEqual(rows[1]['clock_suspended_seconds'], 30)
            self.assertEqual(rows[3]['clock_suspended_seconds'], 60)
            self.assertTrue(rows[1]['matched_pre'])
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_unmatched_resume_has_no_synthetic_sleep_duration(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'events.jsonl'
            recorder = observer.Recorder(path)
            recorder.transition(False)
            recorder.close()
            row = json.loads(path.read_text())
            self.assertFalse(row['matched_pre'])
            self.assertNotIn('clock_suspended_seconds', row)

    def test_existing_output_and_symlink_are_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'existing'
            target.write_text('preserve')
            link = Path(directory) / 'link'
            os.symlink(target, link)
            for path in (target, link):
                with self.assertRaises(FileExistsError):
                    observer.Recorder(path)
            self.assertEqual(target.read_text(), 'preserve')


if __name__ == '__main__':
    unittest.main()
