import threading
import time
import unittest

import gi
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
gi.require_version('Poppler', '0.18')
gi.require_version('Gdk', '3.0')

from .frontend.mainwindow import ActionRefreshIndex, MainWindow
from paperwork.frontend.util.config import load_config


class PaperworkInstance(object):
    def start(self):
        config = load_config()
        config.read()
        self.main_window = MainWindow(config)
        ActionRefreshIndex(self.main_window, config).do()
        thread = threading.Thread(target=self._gtk_thread)
        thread.start()

    def _gtk_thread(self):
        Gtk.main()

    def stop(self):
        GLib.idle_add(Gtk.main_quit)


class TestBasicMainWin(unittest.TestCase):
    def setUp(self):
        self.paperwork = PaperworkInstance()
        self.paperwork.start()

    def test_main_win(self):
        time.sleep(10)

    def tearDown(self):
        self.paperwork.stop()
