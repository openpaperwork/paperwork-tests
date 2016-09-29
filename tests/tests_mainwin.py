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

from gi.repository import Gdk
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


class TestPage(unittest.TestCase):
    def setUp(self):
        self.pw = paperwork.PaperworkInstance()

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

    def test_box_highlight_on_mouseover(self):
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

            mouse_event = Gdk.Event.new(Gdk.EventType.MOTION_NOTIFY)
            mouse_event.x = 250
            mouse_event.y = 356

            canvas = self.pw.main_window.img['canvas']
            GLib.idle_add(canvas.emit, 'motion-notify-event', mouse_event)
            self.pw.wait()

            sc = pytestshot.screenshot(self.pw.gdk_window)
            pytestshot.assertScreenshot(
                self, "test_main_win_box_highlight_on_mouseover", sc
            )
        finally:
            self.pw.stop()

    def _set_show_all_to_true(self, main_win):
        main_win.show_all_boxes = True

    def test_box_highlight_all(self):
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

            action = self.pw.main_window.actions['open_view_settings'][1]
            GLib.idle_add(action.do)
            self.pw.wait()
            GLib.idle_add(self._set_show_all_to_true, self.pw.main_window)
            self.pw.wait()

            sc = pytestshot.screenshot(self.pw.gdk_window)
            pytestshot.assertScreenshot(
                self, "test_main_win_box_highlight_all", sc
            )

            self.pw.main_window.popovers['view_settings'].hide()
            self.pw.wait()

            # make sure the boxes are still highlighted when we switch to
            # another document
            doc = self.pw.docsearch.get_doc_from_docid("20130126_1833_26")
            self.pw.main_window.show_doc(doc)
            self.pw.wait()

            sc = pytestshot.screenshot(self.pw.gdk_window)
            pytestshot.assertScreenshot(
                self, "test_main_win_box_highlight_all_2", sc
            )
        finally:
            self.pw.stop()


class TestResize(unittest.TestCase):
    def setUp(self):
        self.pw = paperwork.PaperworkInstance()

    def test_increase_with_zoom_auto(self):
        self.pw.start()
        try:
            doc = self.pw.docsearch.get_doc_from_docid("20130126_1833_26")
            self.pw.main_window.show_doc(doc)
            self.pw.wait()

            self.pw.main_window.window.set_size_request(1000, 600)

            self.pw.wait()

            # Note: The scrollbars should stick to (0, 0)

            sc = pytestshot.screenshot(self.pw.gdk_window)
            pytestshot.assertScreenshot(
                self, "test_main_win_resized_zoom_auto", sc
            )
        finally:
            self.pw.stop()

    def test_increase_with_zoom_auto_2(self):
        self.pw.start()
        try:
            doc = self.pw.docsearch.get_doc_from_docid("20121213_1946_26")
            self.pw.main_window.show_doc(doc)
            self.pw.wait()

            GLib.idle_add(
                self.pw.main_window.page_drawers[2].emit,
                'page-selected'
            )
            self.pw.wait()

            self.pw.main_window.window.set_size_request(1000, 600)

            self.pw.wait()

            # Note: The scrollbars will try to stay on target

            sc = pytestshot.screenshot(self.pw.gdk_window)
            pytestshot.assertScreenshot(
                self, "test_main_win_resized_zoom_auto_2", sc
            )
        finally:
            self.pw.stop()

    def test_increase_with_zoom_auto_3(self):
        self.pw.start()
        try:
            doc = self.pw.docsearch.get_doc_from_docid("20121213_1946_26")
            self.pw.main_window.show_doc(doc)
            self.pw.wait()

            GLib.idle_add(
                self.pw.main_window.page_drawers[3].emit,
                'page-selected'
            )
            self.pw.wait()

            # scroll to the bottom right
            canvas = self.pw.main_window.img['canvas']
            canvas.hadjustment.set_value(canvas.hadjustment.get_upper())
            canvas.vadjustment.set_value(canvas.vadjustment.get_upper())

            self.pw.wait()

            self.pw.main_window.window.set_size_request(1000, 600)

            self.pw.wait()

            # Note: The scrollbars will still to the botton right

            sc = pytestshot.screenshot(self.pw.gdk_window)
            pytestshot.assertScreenshot(
                self, "test_main_win_resized_zoom_auto_3", sc
            )
        finally:
            self.pw.stop()

    def test_increase_with_zoom_manual(self):
        self.pw.start()
        try:
            doc = self.pw.docsearch.get_doc_from_docid("20121213_1946_26")
            self.pw.main_window.show_doc(doc)
            self.pw.wait()

            self.pw.main_window.set_zoom_level(0.05, auto=False)
            self.pw.main_window.update_page_sizes()
            canvas = self.pw.main_window.img['canvas']
            canvas.recompute_size(upd_scrollbar_values=True)
            canvas.redraw()
            self.pw.wait()

            sc = pytestshot.screenshot(self.pw.gdk_window)
            pytestshot.assertScreenshot(
                self, "test_main_win_resized_zoom_manual_before", sc
            )

            self.pw.main_window.window.set_size_request(1000, 600)

            self.pw.wait()

            # Note: The scrollbars will still to the top left

            sc = pytestshot.screenshot(self.pw.gdk_window)
            pytestshot.assertScreenshot(
                self, "test_main_win_resized_zoom_manual_after", sc
            )
        finally:
            self.pw.stop()
