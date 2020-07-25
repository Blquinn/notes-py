from typing import Union
import logging

from gi.repository import Gtk, Pango, Gdk

from models.models import Note, NoteBook
from widgets.models import ApplicationState
from widgets.note_actions_popover import NoteActionsPopover

log = logging.getLogger(__name__)


@Gtk.Template.from_file('ui/NoteList.ui')
class NoteList(Gtk.Box):
    __gtype_name__ = 'NoteList'

    note_search_entry: Gtk.SearchEntry = Gtk.Template.Child()
    loading_stack: Gtk.Stack = Gtk.Template.Child()
    notes_loading_spinner: Gtk.Spinner = Gtk.Template.Child()
    notes_listbox: Gtk.ListBox = Gtk.Template.Child()

    def __init__(self, main_window: 'MainWindow', state: ApplicationState):
        super().__init__()

        self.main_window = main_window
        self.application_state = state
        self.search_filter = ''

        self.notes_listbox.bind_model(self.application_state.notes, self._create_sidebar_note_widget)
        self.notes_listbox.set_filter_func(self._filter_notes, None)

        # self.application_state.initializing_state
        self.application_state.connect('notify::initializing-state', self._on_notes_loaded)

        self.notes_listbox.set_header_func(self._header_func, None)
        self.application_state.connect('notify::active-note', self._on_active_note_changed)
        self.application_state.connect('notify::active-notebook', self._on_active_notebook_changed)

    def _on_active_note_changed(self, state, *args):
        note: Note = self.application_state.active_note
        if not note:
            return

        # Activate row in listbox any time the active note is changed
        for row in self.notes_listbox.get_children():
            row: Gtk.ListBoxRow = row
            item: NoteListItem = row.get_child()
            if item.note == note:
                self.notes_listbox.select_row(row)
                break

    @Gtk.Template.Callback('on_note_search_entry_changed')
    def _on_note_search_entry_changed(self, entry: Gtk.SearchEntry):
        self.search_filter = entry.get_text()
        self.notes_listbox.invalidate_filter()

    @Gtk.Template.Callback('on_notes_listbox_row_activated')
    def _on_notes_listbox_row_activated(self, lb: Gtk.ListBox, row: Gtk.ListBoxRow):
        nli: NoteListItem = row.get_child()
        self.application_state.active_note = nli.note

    def _create_sidebar_note_widget(self, note: Note):
        ni = NoteListItem(self.main_window, self.application_state, note)
        ni.show_all()
        return ni

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

    def _on_notes_loaded(self, *args):
        log.debug('Notes loaded')
        if self.application_state.notes:
            self.notes_listbox.get_row_at_index(0).activate()

    # TODO: Select first note in notebook
    def _on_active_notebook_changed(self, state, *args):
        """Re-filter notes list when active notebook is changed."""
        self.notes_listbox.invalidate_filter()

    def _header_func(self, row: Gtk.ListBoxRow, before: Union[Gtk.ListBoxRow, None], user_data):
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


class NoteListItem(Gtk.EventBox):

    def __init__(self, main_window, state: ApplicationState, note: Note):
        super(NoteListItem, self).__init__()

        self.main_window = main_window
        self.application_state = state
        self.note = note

        inner_box = Gtk.VBox()
        self.add(inner_box)

        top = Gtk.HBox()
        title_lbl = Gtk.Label(label=note.title)
        note.bind_property('title', title_lbl, 'label', 0)
        title_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        top.add(title_lbl)
        top.set_child_packing(title_lbl, False, False, 10, Gtk.PackType.START)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        top.add(spacer)

        time_lbl = Gtk.Label(label=note.format_last_updated())
        note.bind_property('last_updated_fmt', time_lbl, 'label', 0)
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

        popover = NoteActionsPopover(self.main_window, self.application_state, item.note)
        popover.set_relative_to(self)
        popover.show()
        popover.popup()
