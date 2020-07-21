import logging

from gi.repository import Gtk

from widgets.models import Note

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
       
    # @Gtk.Template.Callback('on_open_in_window_button_clicked')
    # def _on_open_in_window_button_clicked(self, btn):
    #     # TODO: Implement me
    #     log.warning('on_open_in_window_button_clicked was clicked, but is not implemented.')
