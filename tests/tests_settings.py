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

from paperwork.frontend.util.config import load_config


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

    def test_uncheck_ocr(self):
        self.pw.start()
        try:
            action = self.pw.main_window.actions['open_settings'][1]
            GLib.idle_add(action.do)
            try:
                self.pw.wait()
                self.assertNotEqual(action.dialog, None)
                sc = pytestshot.screenshot(action.dialog.window.get_window())
                pytestshot.assertScreenshot(self, "test_settings_open", sc)

                widget = action.dialog.ocr_settings['enabled']['gui']
                GLib.idle_add(widget.set_active, False)
                self.pw.wait()

                sc = pytestshot.screenshot(action.dialog.window.get_window())
                pytestshot.assertScreenshot(
                    self, "test_settings_uncheck_ocr", sc
                )

                GLib.idle_add(
                    action.dialog.window.emit, 'delete-event', None
                )
                self.pw.wait()
            finally:
                GLib.idle_add(action.dialog.window.destroy)
                self.pw.wait()
        finally:
            self.pw.stop()

        config = load_config()
        config.read()
        self.assertFalse(config['ocr_enabled'].value)
