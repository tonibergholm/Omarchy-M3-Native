"""Real typed D-Bus signals on a private daemon; never contacts system logind."""
import json
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

try:
    from gi.repository import Gio, GLib
except ImportError:
    Gio = GLib = None

ROOT = Path(__file__).resolve().parents[1]
CHILD = '''
import importlib.util,sys
from pathlib import Path
from gi.repository import Gio
spec=importlib.util.spec_from_file_location('observer',sys.argv[1])
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
connection=Gio.DBusConnection.new_for_address_sync(sys.argv[2],
    Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT | Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,
    None,None)
m.watch(Path(sys.argv[3]),connection=connection,settle_delays=(1,2,3))
'''


@unittest.skipUnless(Gio and shutil.which('dbus-daemon'), 'Gio and dbus-daemon required')
class PrivateBusTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.output = Path(self.directory.name) / 'events.jsonl'
        self.daemon = subprocess.Popen(
            ['dbus-daemon', '--session', '--nofork', '--print-address=1'],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        address = self.daemon.stdout.readline().strip()
        self.connection = Gio.DBusConnection.new_for_address_sync(
            address, Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT |
            Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION, None, None)
        reply = self.connection.call_sync(
            'org.freedesktop.DBus', '/org/freedesktop/DBus', 'org.freedesktop.DBus',
            'RequestName', GLib.Variant('(su)', ('org.freedesktop.login1', 4)),
            GLib.VariantType.new('(u)'), Gio.DBusCallFlags.NONE, 5000, None)
        self.assertEqual(reply.unpack(), (1,))
        self.child = subprocess.Popen(
            [sys.executable, '-c', CHILD, str(ROOT / 'tools/sleep-observer.py'),
             address, str(self.output)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        self.wait_for(lambda rows: any(r['phase'] == 'observer-start' for r in rows))

    def tearDown(self):
        if self.child.poll() is None:
            self.child.terminate()
        self.child.communicate(timeout=5)
        if not self.connection.is_closed():
            self.connection.close_sync(None)
        if self.daemon.poll() is None:
            self.daemon.terminate()
        self.daemon.wait(timeout=5)
        self.daemon.stdout.close()
        self.directory.cleanup()

    def rows(self):
        try:
            return [json.loads(line) for line in self.output.read_text().splitlines()]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def wait_for(self, predicate, timeout=6):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            rows = self.rows()
            if predicate(rows):
                return rows
            if self.child.poll() is not None:
                self.fail('Observer exited before expected signal result')
            time.sleep(.05)
        self.fail('Expected signal result was not recorded')

    def emit(self, sleeping, interface='org.freedesktop.login1.Manager'):
        self.connection.emit_signal(None, '/org/freedesktop/login1', interface,
                                    'PrepareForSleep', GLib.Variant('(b)', (sleeping,)))
        self.connection.flush_sync(None)

    def test_delivery_pairing_and_cancellation(self):
        self.emit(True, interface='org.example.Unrelated')
        time.sleep(.15)
        self.assertEqual(len(self.rows()), 1)
        self.emit(True)
        self.wait_for(lambda rows: any(r['phase'] == 'prepare-for-sleep' for r in rows))
        self.emit(False)
        self.wait_for(lambda rows: any(r['phase'] == 'post-1s' for r in rows))
        self.emit(True)
        self.wait_for(lambda rows: any(r['cycle'] == 2 for r in rows))
        time.sleep(3.5)
        rows = self.rows()
        self.assertFalse(any(r['cycle'] == 1 and r['phase'] in ('post-2s', 'post-3s') for r in rows))
        self.emit(False)
        rows = self.wait_for(lambda rows: any(r['cycle'] == 2 and r['phase'] == 'post-3s' for r in rows))
        resumes = [r for r in rows if r['phase'] == 'resume-signal']
        self.assertEqual(len(resumes), 2)
        self.assertTrue(all(r['matched_pre'] for r in resumes))
        delayed = [r for r in rows if r['cycle'] == 2 and r['phase'].startswith('post-')]
        self.assertEqual([r['phase'] for r in delayed], ['post-1s', 'post-2s', 'post-3s'])
        self.assertTrue(all(r['seconds_since_resume_signal'] >= 0 for r in delayed))
        self.child.terminate()
        self.child.communicate(timeout=5)
        self.assertEqual(self.child.returncode, 0)
        self.assertEqual(self.rows()[-1]['phase'], 'observer-stop')
        self.assertEqual(self.rows()[-1]['failure_types'], [])

    def test_bus_disconnect_is_reported_as_failure(self):
        self.daemon.terminate()
        self.daemon.wait(timeout=5)
        self.assertNotEqual(self.child.wait(timeout=3), 0)
        self.assertIn('SystemBusClosed', self.rows()[-1]['failure_types'])


if __name__ == '__main__':
    unittest.main()
