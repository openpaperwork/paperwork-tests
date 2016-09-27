import os
os.environ['LANG'] = 'C'
os.environ['XDG_DATA_HOME'] = 'tmp'
os.environ['GTK_THEME'] = 'HighContrast'
os.environ['XDG_DTA_DIRS'] = '/usr/local/share:/usr/share'

import shutil
import threading
import time
import unittest

import pytestshot

from paperwork.frontend import mainwindow
from paperwork.frontend.util.config import load_config

import gi
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
gi.require_version('Poppler', '0.18')
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')

from gi.repository import GLib
from gi.repository import Gtk


class PaperworkInstance(object):
    def start(self):
        if os.path.exists("tmp"):
            shutil.rmtree("tmp")
        if os.path.exists("data"):
            shutil.rmtree("data")
        if os.path.exists("paperwork.conf"):
            os.unlink("paperwork.conf")
        os.mkdir("tmp")
        shutil.copy("orig_paperwork.conf", "paperwork.conf")
        shutil.copytree("orig_data", "data")

        config = load_config()
        config.read()
        mainwindow.__version__ = "TEST"
        mainwindow.g_must_init_app = False
        self.main_window = mainwindow.MainWindow(config)
        mainwindow.ActionRefreshIndex(self.main_window, config).do()
        self.thread = threading.Thread(target=self._gtk_thread)
        self.thread.start()
        self.wait()

    def _gtk_thread(self):
        Gtk.main()

    def _get_gdk_win(self):
        return self.main_window.window.get_window()

    gdk_window = property(_get_gdk_win)

    def _get_docsearch(self):
        return self.main_window.docsearch

    docsearch = property(_get_docsearch)

    def wait(self):
        time.sleep(0.1)  # force thread yielding
        pytestshot.wait()
        for i in range(0, 5):
            loop_again = True
            while loop_again:
                time.sleep(0.1)  # force thread yielding
                for scheduler in self.main_window.schedulers.values():
                    scheduler.wait_for_all()
                loop_again = Gtk.events_pending()
                if loop_again:
                    pytestshot.wait()
        time.sleep(0.5)  # force thread yielding

    def stop(self):
        pytestshot.wait()
        for scheduler in self.main_window.schedulers.values():
            scheduler.stop()
        pytestshot.wait()
        time.sleep(0.1)  # force thread yielding
        self.main_window.window.hide()
        time.sleep(0.1)  # force thread yielding
        pytestshot.wait()
        pytestshot.exit()
        self.thread.join()
        if threading.active_count() > 1:
            print (
                "WARNING: Some threads are still active at the end of the test"
            )
            for thread in threading.enumerate():
                print (thread)


class TestBasicMainWin(unittest.TestCase):
    def setUp(self):
        self.pw = PaperworkInstance()

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
