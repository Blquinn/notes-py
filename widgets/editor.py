from gi.repository import Gtk, GLib
import logging

from models.models import Note
from widgets.editor_buffer import UndoableBuffer
from widgets.models import ApplicationState
from widgets.move_note_dialog import MoveNoteDialog
from widgets.rich_editor import RichEditor

log = logging.getLogger(__name__)


@Gtk.Template.from_file('ui/Editor.ui')
class Editor(Gtk.Box):
    __gtype_name__ = 'Editor'

    last_updated_label: Gtk.Label = Gtk.Template.Child()
    note_title_entry: Gtk.Entry = Gtk.Template.Child()
    text_style_bar: Gtk.ButtonBox = Gtk.Template.Child()
    editor_scrolled_window: Gtk.ScrolledWindow = Gtk.Template.Child()
    notebook_button_label: Gtk.Label = Gtk.Template.Child()

    def __init__(self, main_window, state: ApplicationState):
        super().__init__()

        self.main_window = main_window
        self.application_state = state

        self.editor = RichEditor(self.application_state)
        self.editor.set_margin_top(10)
        self.editor.set_margin_start(30)
        self.editor.set_margin_end(30)
        self.editor_scrolled_window.add(self.editor)

        self.application_state.connect('notify::active-note', self._on_active_note_changed)
        self.application_state.connect('notify::active-notebook', self._on_active_notebook_changed)

        # TODO: Remove me
        buf: UndoableBuffer = self.editor.get_buffer()
        it = buf.get_start_iter()
        buf.insert_markup(it, '<b>Bold text</b>\n', -1)
        buf.insert_markup(it, '<i>Italics text</i>\n', -1)
        buf.insert(it, '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nFoobar', -1)

    @Gtk.Template.Callback('on_note_title_entry_changed')
    def _on_note_title_entry_changed(self, entry: Gtk.Entry):
        txt = entry.get_text()
        self.application_state.active_note.title = txt

    @Gtk.Template.Callback('on_note_notebook_button_clicked')
    def _on_note_notebook_button_clicked(self, btn):
        diag = MoveNoteDialog(self, self.application_state.active_note, self.application_state)
        diag.set_transient_for(self.main_window)
        diag.show_all()

    def _on_active_note_changed(self, *args):
        note: Note = self.application_state.active_note
        if not note:
            return
        log.debug('Editor active note changed.')

        notebook_name = note.notebook.name if note.notebook else 'Other Notes'
        self.notebook_button_label.set_text(notebook_name)
        self.note_title_entry.set_text(note.title)
        self.editor.set_buffer(note.body)
        self.last_updated_label.set_text(f'Last Updated {note.format_last_updated()}')

    def _on_active_notebook_changed(self, *args):
        note: Note = self.application_state.active_note
        if not note:
            return

        notebook_name = note.notebook.name if note.notebook else 'Other Notes'
        self.notebook_button_label.set_text(notebook_name)
