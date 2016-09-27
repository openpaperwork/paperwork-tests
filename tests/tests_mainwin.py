import time
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


class TestBasicMainWin(unittest.TestCase):
    def setUp(self):
        self.pw = paperwork.PaperworkInstance()

    def test_main_win_start(self):
        self.pw.start()
        try:
            sc = pytestshot.screenshot(self.pw.gdk_window)
        finally:
            self.pw.stop()
        pytestshot.assertScreenshot(self, "test_main_win_start", sc)

    def test_main_win_show_doc_one_page(self):
        self.pw.start()
        try:
            doc = self.pw.docsearch.get_doc_from_docid("20130126_1902_26")
            self.pw.main_window.show_doc(doc)
            self.pw.wait()

            sc = pytestshot.screenshot(self.pw.gdk_window)
        finally:
            self.pw.stop()
        pytestshot.assertScreenshot(self, "test_main_win_show_doc_one_page", sc)

    def test_show_doc_multiple_pages(self):
        self.pw.start()
        try:
            doc = self.pw.docsearch.get_doc_from_docid("20121213_1946_26")
            self.pw.main_window.show_doc(doc)
            self.pw.wait()

            sc = pytestshot.screenshot(self.pw.gdk_window)
        finally:
            self.pw.stop()
        pytestshot.assertScreenshot(
            self, "test_main_win_show_doc_multiple_pages", sc
        )

    def test_show_page(self):
        self.pw.start()
        try:
            doc = self.pw.docsearch.get_doc_from_docid("20121213_1946_26")
            self.pw.main_window.show_doc(doc)
            self.pw.wait()

            sc = pytestshot.screenshot(self.pw.gdk_window)
            pytestshot.assertScreenshot(
                self, "test_main_win_show_doc_multiple_pages", sc
            )

            GLib.idle_add(
                self.pw.main_window.page_drawers[2].emit,
                'page-selected'
            )
            self.pw.wait()

            sc = pytestshot.screenshot(self.pw.gdk_window)
            pytestshot.assertScreenshot(
                self, "test_main_win_show_page", sc
            )
        finally:
            self.pw.stop()

    def test_scroll_to_page(self):
        self.pw.start()
        try:
            doc = self.pw.docsearch.get_doc_from_docid("20121213_1946_26")
            self.pw.main_window.show_doc(doc)
            self.pw.wait()

            sc = pytestshot.screenshot(self.pw.gdk_window)
            pytestshot.assertScreenshot(
                self, "test_main_win_show_doc_multiple_pages", sc
            )

            self.pw.main_window.set_layout('paged')
            self.pw.wait()

            canvas = self.pw.main_window.img['canvas']

            adj = canvas.get_hadjustment()
            self.assertEqual(adj.get_value(), 0)
            self.assertEqual(adj.get_lower(), 0)

            adj = canvas.get_vadjustment()
            self.assertEqual(adj.get_value(), 0)
            self.assertEqual(adj.get_lower(), 0)
            self.assertNotEqual(adj.get_upper(), 0)

            target = int(adj.get_upper() / 2)
            step = int(target / (1 / 0.05))
            for pos in range(0, target, step):
                adj.set_value(pos)
                time.sleep(0.05)
            adj.set_value(target)
            self.pw.wait()

            sc = pytestshot.screenshot(self.pw.gdk_window)
            pytestshot.assertScreenshot(
                self, "test_main_win_scroll_to_page", sc
            )
        finally:
            self.pw.stop()
