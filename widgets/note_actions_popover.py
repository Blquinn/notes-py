import logging

from gi.repository import Gtk

from models.models import Note
from widgets.models import ApplicationState
from widgets.move_note_dialog import MoveNoteDialog

log = logging.getLogger(__name__)


@Gtk.Template.from_file("ui/NoteActionsPopover.ui")
class NoteActionsPopover(Gtk.PopoverMenu):
    __gtype_name__ = 'NoteActionsPopover'

    open_in_window_button = Gtk.Template.Child()

    def __init__(self, main_window, state: ApplicationState, note: Note = None):
        super(NoteActionsPopover, self).__init__()

        self.main_window = main_window
        self.note = note
        self.application_state = state

    @Gtk.Template.Callback('on_move_to_button_clicked')
    def _on_move_to_button_clicked(self, btn):
        note = self.note if self.note else self.application_state.active_note
        diag = MoveNoteDialog(self.main_window, note, self.application_state)
        diag.set_transient_for(self.main_window)
        diag.show_all()
