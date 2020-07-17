import logging
import sys
import os

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from widgets.main_window import MainWindow

levelName = os.getenv('LOG_LEVEL', 'INFO')
level = logging.getLevelName(levelName)

logging.basicConfig(
    format='%(asctime)s - %(module)s - [%(levelname)s] %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level = level)

log = logging.getLogger(__name__)


if __name__ == '__main__':
    log.info('Bootstrapping gtk resources.')

    css_provider = Gtk.CssProvider()
    css_provider.load_from_path('ui/style.css')

    Gtk.StyleContext().add_provider_for_screen(
        Gdk.Screen().get_default(),
        css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    win = MainWindow()

    def close(*args):
        log.info('Exiting...')
        sys.exit(0)

    win.connect('delete-event', close)

    win.show()

    log.info('Starting application.')
    Gtk.main()
