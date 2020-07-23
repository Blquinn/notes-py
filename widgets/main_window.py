import logging
from typing import Union

from gi.repository import Gtk, Gdk, Pango

from models.db import NoteDao
from models.models import Note, NoteBook
from widgets.application_preferences_popover import ApplicationPreferencesPopover
from widgets.edit_notebooks_dialog import EditNotebooksDialog
from widgets.editor_buffer import UndoableBuffer
from widgets.models import ApplicationState
from widgets.move_note_dialog import MoveNoteDialog
from widgets.note_actions_popover import NoteActionsPopover
from widgets.notebook_selection_popover import NotebookSelectionPopover
from widgets.rich_editor import RichEditor

log = logging.getLogger(__name__)

# TODO: Split into multiple widgets
# Note: We can keep state by keeping the text buffers in memory and swapping the active buffer
# https://python-gtk-3-tutorial.readthedocs.io/en/latest/textview.html


@Gtk.Template.from_file('ui/MainWindow.ui')
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'MainWindow'

    editor_scrolled_window: Gtk.ScrolledWindow = Gtk.Template.Child()
    editor: RichEditor = None
    header_main: Gtk.HeaderBar = Gtk.Template.Child()
    header_side: Gtk.HeaderBar = Gtk.Template.Child()
    text_style_bar: Gtk.ButtonBox = Gtk.Template.Child()
    note_selection_box: Gtk.Box = Gtk.Template.Child()
    note_selection_button: Gtk.MenuButton = Gtk.Template.Child()
    note_selection_button_label: Gtk.Label = Gtk.Template.Child()
    notes_listbox: Gtk.ListBox = Gtk.Template.Child()
    notes_loading_spinner: Gtk.Spinner = Gtk.Template.Child()
    loading_stack: Gtk.Stack = Gtk.Template.Child()
    notebook_button_label: Gtk.Label = Gtk.Template.Child()
    note_title_entry: Gtk.Entry = Gtk.Template.Child()
    note_search_entry: Gtk.SearchEntry = Gtk.Template.Child()
    last_updated_label: Gtk.Label = Gtk.Template.Child()

    def __init__(self, note_dao: NoteDao):
        super(MainWindow, self).__init__()

        self.search_filter = ''

        self.note_dao = note_dao
        self.application_state = ApplicationState()

        self.editor = RichEditor(self.application_state)
        self.editor.set_margin_top(10)
        self.editor.set_margin_start(30)
        self.editor.set_margin_end(30)
        self.editor_scrolled_window.add(self.editor)

        self.editor_actions_button = Gtk.MenuButton()
        self.editor_actions_button.add(
            Gtk.Image().new_from_icon_name('view-more-symbolic', Gtk.IconSize.LARGE_TOOLBAR)
        )
        self.header_main.pack_end(self.editor_actions_button)

        self.editor_options_popover = NoteActionsPopover()
        self.editor_actions_button.set_popover(self.editor_options_popover)

        self.add_note_button = Gtk.Button()
        self.add_note_button.add(Gtk.Image().new_from_icon_name('value-increase-symbolic', Gtk.IconSize.BUTTON))
        self.header_side.pack_start(self.add_note_button)
        self.add_note_button.connect('clicked', self._on_add_notebook_button_pressed)

        self.preferences_button = Gtk.MenuButton()
        self.preferences_button.add(Gtk.Image().new_from_icon_name('view-list-text-symbolic', Gtk.IconSize.BUTTON))
        self.header_side.pack_end(self.preferences_button)
        
        self.application_preferences_popover = ApplicationPreferencesPopover()
        self.preferences_button.set_popover(self.application_preferences_popover)
       
        self.notebook_selection_popover = NotebookSelectionPopover(self.application_state)
        self.note_selection_button.set_popover(self.notebook_selection_popover)

        self.notes_listbox.bind_model(self.application_state.notes, self._create_sidebar_note_widget)
        self.notes_listbox.set_filter_func(self._filter_notes, None)

        def header_func(row: Gtk.ListBoxRow, before: Union[Gtk.ListBoxRow, None], user_data):
            """
            Build notes list header. Note that pinned notes, must all come
            first in the list for this impl to work.
            """
            note: Note = row.get_child().note

            def create_header(text: str):
                box = Gtk.VBox()
                box.get_style_context().add_class('list-header')
                box.set_margin_top(10)

                lbl = Gtk.Label(label=text)
                lbl.set_halign(Gtk.Align.START)
                lbl.set_margin_start(10)
                box.add(lbl)

                sep = Gtk.Separator()
                box.add(sep)
                box.show_all()

                return box

            if not before:
                if note.pinned:
                    row.set_header(create_header('Pinned'))
                else:
                    row.set_header(create_header('Other Notes'))
                return

            before_note: Note = before.get_child().note
            if before_note.pinned and not note.pinned:
                row.set_header(create_header('Other Notes'))

        self.notes_listbox.set_header_func(header_func, None)

        # TODO: Remove me
        buf: UndoableBuffer = self.editor.get_buffer()
        it = buf.get_start_iter()
        buf.insert_markup(it, '<b>Bold text</b>\n', -1)
        buf.insert_markup(it, '<i>Italics text</i>\n', -1)
        buf.insert(it, '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nFoobar', -1)

        self.note_dao.get_all_notes_and_notebooks().add_done_callback(self._on_notes_loaded)

        self.application_state.connect('notify::active-note', self._on_active_note_changed)
        self.application_state.connect('notify::active-notebook', self._on_active_notebook_changed)

    # TODO: Select first note in notebook
    def _on_active_notebook_changed(self, state, *args):
        """Re-filter notes list when active notebook is changed."""
        self.notes_listbox.invalidate_filter()
        nb: NoteBook = self.application_state.active_notebook
        notebook_name = nb.name if nb else 'All Notebooks'
        self.note_selection_button_label.set_text(notebook_name)
        if nb:
            nb.connect('notify::name', self._on_active_notebook_name_changed)

    def _on_active_notebook_name_changed(self, nb: NoteBook, *args):
        self.note_selection_button_label.set_text(nb.name)

    def _on_active_note_changed(self, state, *args):
        note: Note = self.application_state.active_note
        if not note:
            return

        notebook_name = note.notebook.name if note.notebook else 'Other Notes'
        self.notebook_button_label.set_text(notebook_name)
        self.note_title_entry.set_text(note.title)
        self.editor.set_buffer(note.body)
        self.last_updated_label.set_text(f'Last Updated {note.format_last_updated()}')

    def _filter_notes(self, row: Gtk.ListBoxRow, data) -> bool:
        """
        Note filtering function, will be re-run when notes_list.invalidate_filter() is called.
        Currently supports filtering by notebook.
        """
        note: Note = row.get_child().note

        # TODO: Search body?
        if self.search_filter and self.search_filter.lower() not in note.title.lower():
            return False

        if note.trash:
            return False

        anb = self.application_state.active_notebook
        if anb and note.notebook.pk != anb.pk:
            return False

        return True 

    def _on_notes_loaded(self, notes_fut):
        """Callback for when the database completes loading the notes + notebooks."""
        try:
            (notes, notebooks) = notes_fut.result()
        except Exception as e:
            log.error(f'Failed to load notes from db {e}')
            return

        log.info(f'Loaded {len(notes)} notes from local db.')
        for note in notes:
            self.application_state.notes.append(note)

        for nb in notebooks:
            self.application_state.notebooks.append(nb)

        if notes:
            self.notes_listbox.get_row_at_index(0).activate()

    def _on_add_notebook_button_pressed(self, btn):
        diag = EditNotebooksDialog(self.application_state)
        diag.set_transient_for(self)
        diag.show()

    @Gtk.Template.Callback('on_note_notebook_button_clicked')
    def _on_note_notebook_button_clicked(self, btn):
        diag = MoveNoteDialog(self.application_state.active_note)
        diag.set_transient_for(self)
        diag.show()

    @Gtk.Template.Callback('on_note_search_entry_changed')
    def _on_note_search_entry_changed(self, entry: Gtk.SearchEntry):
        self.search_filter = entry.get_text()
        self.notes_listbox.invalidate_filter()
        
    @Gtk.Template.Callback('on_notes_listbox_row_activated')
    def _on_notes_listbox_row_activated(self, lb: Gtk.ListBox, row: Gtk.ListBoxRow):
        nli: NoteListItem = row.get_child()
        self.application_state.active_note = nli.note

    def _create_sidebar_note_widget(self, note: Note):
        ni = NoteListItem(note)
        ni.show_all()
        return ni


class NoteListItem(Gtk.EventBox):

    def __init__(self, note: Note):
        super(NoteListItem, self).__init__()

        self.note = note

        inner_box = Gtk.VBox()
        self.add(inner_box)

        top = Gtk.HBox()
        title_lbl = Gtk.Label(label=note.title)
        title_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        top.add(title_lbl)
        top.set_child_packing(title_lbl, False, False, 10, Gtk.PackType.START)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        top.add(spacer)

        time_lbl = Gtk.Label(label=note.format_last_updated())
        time_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        top.add(time_lbl)
        top.set_child_packing(time_lbl, False, False, 10, Gtk.PackType.END)

        inner_box.add(top)
        inner_box.set_child_packing(top, False, False, 0, Gtk.PackType.START)

        start: Gtk.TextIter = note.body.get_start_iter()
        end = start.copy()
        end.forward_chars(200)
        preview_text = note.body.get_text(start, end, False)
        bottom = Gtk.Label(label=preview_text)
        bottom.set_ellipsize(Pango.EllipsizeMode.END)
        bottom.set_lines(2)
        bottom.set_line_wrap(True)
        bottom.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        bottom.set_alignment(0.0, 0.5)
        bottom.set_margin_start(10)
        bottom.set_margin_end(10)

        inner_box.add(bottom)
        inner_box.set_child_packing(bottom, False, False, 10, Gtk.PackType.START)

        inner_box.add(Gtk.Separator())

        # Signals

        self.connect('button-press-event', self._on_button_press)

    def _on_button_press(self, item: 'NoteListItem', event: Gdk.EventButton):
        if event.button != Gdk.BUTTON_SECONDARY:  # Right click
            return

        log.debug(f'Note {item.note} right clicked.')

        popover = NoteActionsPopover(item.note)
        popover.set_relative_to(self)
        popover.show()
        popover.popup()
