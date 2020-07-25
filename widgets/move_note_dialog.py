import logging

from gi.repository import Gtk, Pango

from models.models import Note, NoteBook
from widgets.models import ApplicationState

log = logging.getLogger(__name__)

# TODO: Actually move the note

@Gtk.Template.from_file('ui/MoveNoteDialog.ui')
class MoveNoteDialog(Gtk.Dialog):
    __gtype_name__ = 'MoveNoteDialog'

    headerbar: Gtk.HeaderBar = Gtk.Template.Child()
    notebooks_list: Gtk.ListBox = Gtk.Template.Child()
    new_notebook_entry: Gtk.Entry = Gtk.Template.Child()

    def __init__(self, main_window: 'MainWindow', note: Note, state: ApplicationState):
        super(MoveNoteDialog, self).__init__(use_header_bar=True)

        self.main_window = main_window
        self.note = note
        self.application_state = state

        self.close_button = Gtk.Button(label='Close')
        self.headerbar.pack_start(self.close_button)
        self.close_button.connect('clicked', self._on_close_clicked)

        self.move_button = Gtk.Button(label='Move')
        self.move_button.set_sensitive(False)  # Will become sensitive once row is selected
        self.headerbar.pack_end(self.move_button)

        self.notebooks_list.bind_model(state.notebooks, self._create_notebook_row)
        self.move_button.connect('clicked', self._on_move_clicked)

    @Gtk.Template.Callback('on_notebooks_list_row_activated') 
    def _on_notebooks_list_row_activated(self, row: Gtk.ListBoxRow, *args):
        self.move_button.set_sensitive(True)

    def _create_notebook_row(self, notebook: NoteBook):
        box = Gtk.VBox()
        box.notebook = notebook
        lbl = Gtk.Label(label=notebook.name)
        lbl.set_padding(10, 0)
        lbl.set_halign(Gtk.Align.START)
        lbl.set_ellipsize(Pango.EllipsizeMode.END)
        lbl.set_margin_top(10)
        lbl.set_margin_bottom(10)
        box.add(lbl)
        box.add(Gtk.Separator())
        box.show_all()
        return box

    def _on_close_clicked(self, btn):
        self.close()

    def _on_move_clicked(self, btn):
        selected_nb_idx = self.notebooks_list.get_selected_row().get_index()
        selected_nb = self.application_state.notebooks[selected_nb_idx]
        log.debug('Moving note %s to notebook %s', self.note, selected_nb)
        # TODO: update db
        self.note.notebook = selected_nb
        self.main_window.invalidate_note_list_filter()
        self.application_state.active_notebook = selected_nb
        self.close()

    # TODO: Store in db
    @Gtk.Template.Callback('on_new_notebook_button_clicked') 
    def _on_new_notebook_button_clicked(self, btn):
        name = self.new_notebook_entry.get_text()
        if not name:
            return

        self.new_notebook_entry.set_text('')

        nb = NoteBook(name)
        self.application_state.notebooks.append(nb)
