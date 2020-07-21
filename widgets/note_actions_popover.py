import logging

from gi.repository import Gtk

from widgets.models import Note
from widgets.move_note_dialog import MoveNoteDialog

log = logging.getLogger(__name__)


@Gtk.Template.from_file("ui/NoteActionsPopover.ui")
class NoteActionsPopover(Gtk.PopoverMenu):
    __gtype_name__ = 'NoteActionsPopover'

    open_in_window_button = Gtk.Template.Child()

    def __init__(self, note: Note = None):
        super(NoteActionsPopover, self).__init__()
        self.note = note

    def set_note(self, note: Note):
        self.note = note

    @Gtk.Template.Callback('on_move_to_button_clicked')
    def _on_move_to_button_clicked(self, btn):
        diag = MoveNoteDialog(self.note)
        diag.set_transient_for(self.get_parent())
        diag.show()
