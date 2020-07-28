import logging

from gi.repository import Gtk

from models.models import Note
from utils import debounce
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

        self.editor = RichEditor(self.application_state,
                                 margin_top=10, margin_start=30, margin_end=30)
        self.editor_scrolled_window.add(self.editor)

        self.application_state.connect('notify::active-note', self._on_active_note_changed)
        self.application_state.connect('notify::active-notebook', self._on_active_notebook_changed)
        self._update_note_debounced = debounce(500)(self.__update_note)

    def __update_note(self, note: Note):
        log.debug('Saving note %s', note)
        self.application_state.update_note(note)

    @Gtk.Template.Callback('on_note_title_entry_changed')
    def _on_note_title_entry_changed(self, entry: Gtk.Entry):
        txt = entry.get_text()
        note = self.application_state.active_note
        # Prevent save from being called when title is initially set
        if txt == note.title:
            return

        note.title = txt
        self._update_note_debounced(note)

    @Gtk.Template.Callback('on_note_notebook_button_clicked')
    def _on_note_notebook_button_clicked(self, btn):
        diag = MoveNoteDialog(self, self.application_state.active_note, self.application_state,
                              transient_for=self.get_toplevel())
        diag.show_all()
        diag.run()

    def _on_active_note_changed(self, *args):
        note: Note = self.application_state.active_note
        if not note:
            return
        log.debug('Editor active note changed.')

        notebook_name = note.notebook.name if note.notebook else 'Other Notes'
        self.notebook_button_label.set_text(notebook_name)
        self.note_title_entry.set_text(note.title)
        self.editor.set_buffer(note.body)
        self.last_updated_label.set_text(f'Last Updated {note.last_updated_formatted}')

    def _on_active_notebook_changed(self, *args):
        note: Note = self.application_state.active_note
        if not note:
            return

        notebook_name = note.notebook.name if note.notebook else 'Other Notes'
        self.notebook_button_label.set_text(notebook_name)
