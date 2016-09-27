import unittest

# this import must be done *BEFORE* Gtk/Glib/etc *AND* pytestshot !
from . import paperwork

import pytestshot

import gi
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
gi.require_version('Poppler', '0.18')
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')

from gi.repository import GLib


class TestSettings(unittest.TestCase):
    def setUp(self):
        self.pw = paperwork.PaperworkInstance()

    def test_open(self):
        self.pw.start()
        try:
            action = self.pw.main_window.actions['open_settings'][1]
            GLib.idle_add(action.do)
            try:
                self.pw.wait()
                self.assertNotEqual(action.dialog, None)
                sc = pytestshot.screenshot(action.dialog.window.get_window())
            finally:
                GLib.idle_add(action.dialog.window.destroy)
        finally:
            self.pw.stop()
        pytestshot.assertScreenshot(self, "test_settings_open", sc)
