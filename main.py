import logging
import os

import gi

from widgets.models import ApplicationState, Note, NoteBook

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from widgets.main_window import MainWindow


levelName = os.getenv('LOG_LEVEL', 'INFO')
level = logging.getLevelName(levelName)

logging.basicConfig(
    format='%(asctime)s - %(module)s - [%(levelname)s] %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=level)

log = logging.getLogger(__name__)


if __name__ == '__main__':
    log.info('Bootstrapping gtk resources.')

    css_provider = Gtk.CssProvider()
    css_provider.load_from_path('ui/style.css')

    Gtk.StyleContext().add_provider_for_screen(
        Gdk.Screen().get_default(),
        css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    state = ApplicationState()

    notebook = NoteBook('Astronomy')
    state.notebooks.append(notebook)
    state.notebooks.append(NoteBook('Fun stuff'))

    notes = [
        Note('Jobs to do', 'The most effective way to destroy people is to deny an obliterate their psyche.', notebook, pinned=True),
        Note('Gift Ideas', 'The most effective way to destroy people is to deny an obliterate their psyche.', notebook, pinned=True),
        Note('Pluto', 'The most effective way to destroy people is to deny an obliterate their psyche.', notebook, pinned=False),
        Note('Something else', 'The most effective way to destroy people is to deny an obliterate their psyche.', notebook, pinned=False),
    ]

    for note in notes:
        state.notes.append(note)

    win = MainWindow(state)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    log.info('Starting application.')
    Gtk.main()
