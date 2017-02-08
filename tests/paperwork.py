import os
# Must be set *BEFORE* import Gtk/GLib/etc and pytestshot !
if os.getenv('KEEP_ENV', '0') != "1":
    os.environ['LANG'] = 'C'
    os.environ['XDG_DATA_HOME'] = 'tmp'
    os.environ['GTK_THEME'] = 'HighContrast'
    os.environ['XDG_DTA_DIRS'] = '/usr/local/share:/usr/share'
    os.environ['GDK_RENDERING'] = 'image'

import logging
logging.disable(logging.DEBUG)
logging.getLogger('pycountry.db').setLevel(logging.WARNING)

import time
import shutil
import threading

import pyinsane2
import pytestshot

import gi
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
gi.require_version('Poppler', '0.18')
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

from paperwork.frontend import mainwindow
from paperwork.frontend.util.config import load_config


pyinsane2.init()


def setup_test_env():
    if os.path.exists("tmp"):
        shutil.rmtree("tmp")
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("paperwork.conf"):
        os.unlink("paperwork.conf")
    os.mkdir("tmp")
    shutil.copy("orig_paperwork.conf", "paperwork.conf")
    shutil.copytree("orig_data", "data")
    if os.getenv('KEEP_ENV', '0') == "1":
        # we are taking screenshots, not testing. drop document 'weird name'
        shutil.rmtree("data/weird name")


class PaperworkInstance(object):
    def start(self):
        setup_test_env()

        config = load_config()
        config.read()

        if os.getenv('KEEP_ENV', '0') != "1":
            mainwindow.__version__ = "TEST"
        else:
            mainwindow.__version__ = ""
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
