import logging

from gi.repository import Gtk

from widgets.models import Note

log = logging.getLogger(__name__)


@Gtk.Template.from_file('ui/MoveNoteDialog.ui')
class MoveNoteDialog(Gtk.Dialog):
    __gtype_name__ = 'MoveNoteDialog'

    headerbar: Gtk.HeaderBar = Gtk.Template.Child()

    def __init__(self, note: Note):
        super(MoveNoteDialog, self).__init__(use_header_bar=True)

        self.note = note

        self.close_button = Gtk.Button(label='Close')
        self.headerbar.pack_start(self.close_button)
        self.close_button.connect('clicked', self._on_close_clicked)
        self.close_button.show()

        self.move_button = Gtk.Button(label='Move')
        self.move_button.set_sensitive(False)  # Will become sensitive once row is selected
        self.headerbar.pack_end(self.move_button)
        self.move_button.show()

    def _on_close_clicked(self, btn):
        self.close()

    def _on_move_clicked(self, btn):
        log.info('Moving to x.')
        self.close()
