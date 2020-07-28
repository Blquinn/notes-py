import logging

from gi.repository import Gtk

from models.db import NoteDao
from models.models import Note, NoteBook
from widgets.application_preferences_popover import ApplicationPreferencesPopover
from widgets.editor import Editor
from widgets.models import ApplicationState
from widgets.note_actions_popover import NoteActionsPopover
from widgets.note_list import NoteList
from widgets.notebook_selection_popover import NotebookSelectionPopover

log = logging.getLogger(__name__)

# TODO: Split into multiple widgets
# Note: We can keep state by keeping the text buffers in memory and swapping the active buffer
# https://python-gtk-3-tutorial.readthedocs.io/en/latest/textview.html


@Gtk.Template.from_file('ui/MainWindow.ui')
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'MainWindow'

    header_main: Gtk.HeaderBar = Gtk.Template.Child()
    header_side: Gtk.HeaderBar = Gtk.Template.Child()
    main_pane: Gtk.Paned = Gtk.Template.Child()
    note_selection_box: Gtk.Box = Gtk.Template.Child()
    note_selection_button: Gtk.MenuButton = Gtk.Template.Child()
    note_selection_button_label: Gtk.Label = Gtk.Template.Child()

    def __init__(self, note_dao: NoteDao):
        super(MainWindow, self).__init__()

        self.note_dao = note_dao
        self.application_state = ApplicationState()

        self.side_panel = NoteList(self, self.application_state)
        self.main_pane.pack1(self.side_panel, False, False)

        self.editor = Editor(self, self.application_state)
        self.main_pane.pack2(self.editor, False, False)

        self.editor_actions_button = Gtk.MenuButton()
        self.editor_actions_button.add(
            Gtk.Image().new_from_icon_name('view-more-symbolic', Gtk.IconSize.LARGE_TOOLBAR)
        )
        self.editor_options_popover = NoteActionsPopover(self, self.application_state)
        self.editor_actions_button.set_popover(self.editor_options_popover)
        self.header_main.pack_end(self.editor_actions_button)

        self.add_note_button = Gtk.Button()
        self.add_note_button.add(Gtk.Image().new_from_icon_name('value-increase-symbolic', Gtk.IconSize.BUTTON))
        self.header_side.pack_start(self.add_note_button)
        self.add_note_button.connect('clicked', self._on_add_notebook_button_pressed)

        self.preferences_button = Gtk.MenuButton()
        self.preferences_button.add(Gtk.Image().new_from_icon_name('format-justify-fill-symbolic', Gtk.IconSize.BUTTON))
        self.header_side.pack_end(self.preferences_button)
        
        self.application_preferences_popover = ApplicationPreferencesPopover()
        self.preferences_button.set_popover(self.application_preferences_popover)
       
        self.notebook_selection_popover = NotebookSelectionPopover(self.application_state)
        self.note_selection_button.set_popover(self.notebook_selection_popover)

        self.application_state.connect('notify::active-notebook', self._on_active_notebook_changed)

        self.application_state.initialize_state()

    def _on_active_notebook_changed(self, *args):
        nb: NoteBook = self.application_state.active_notebook
        notebook_name = nb.name if nb else 'All Notebooks'
        self.note_selection_button_label.set_text(notebook_name)
        if nb:
            nb.connect('notify::name', self._on_active_notebook_name_changed)

    def _on_active_notebook_name_changed(self, nb: NoteBook, *args):
        self.note_selection_button_label.set_text(nb.name)

    def invalidate_note_list_filter(self):
        self.notes_listbox.invalidate_filter()
        self.notebook_button_label.set_text(self.application_state.active_note.notebook.name)

    def _on_add_notebook_button_pressed(self, btn):
        """Add a new blank note to the current notebook."""
        self.application_state.add_new_note()
