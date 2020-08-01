# -*- coding: utf-8 -*-
# Copyright (c) 2020, Benjamin Quinn <benlquinn@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, see <http://www.gnu.org/licenses/>.
import logging
from typing import Union

from gi.repository import Gtk, Pango, Gdk

from models.models import Note
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

        self.notes_listbox.set_header_func(self._header_func, None)
        self.notes_listbox.set_sort_func(self._sort_notes)

        self.application_state.connect('notify::initializing-state', self._on_notes_loaded)
        self.application_state.connect('notify::active-note', self._on_active_note_changed)
        self.application_state.connect('notify::active-notebook', self._on_active_notebook_changed)
        self.application_state.connect('notify::show-trash', self._on_show_trash_changed)
        self.application_state.note_changed.connect(self._on_note_changed)

    def _on_show_trash_changed(self, *args):
        self.notes_listbox.invalidate_filter()

    def _sort_notes(self, a_row: Note, b_row: Note):
        """ Sorts the current view of the notes. Sorts on pinned, then last_updated. """
        a: Note = a_row.get_child().note
        b: Note = b_row.get_child().note
        comp = int(b.pinned) - int(a.pinned)
        if comp == 0:
            comp = int(b.last_updated > a.last_updated)
        return comp

    def _on_note_changed(self, state):
        self.notes_listbox.invalidate_filter()
        self.notes_listbox.invalidate_sort()
        self.notes_listbox.invalidate_headers()

    def _on_active_note_changed(self, state, *args):
        note: Note = self.application_state.active_note
        if not note:
            return

        # Select row in listbox any time the active note is changed
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

        # TODO: Search body
        if self.search_filter and self.search_filter.lower() not in note.title.lower():
            return False

        if self.application_state.show_trash:
            return note.trash

        if note.trash:
            return False

        anb = self.application_state.active_notebook
        notebook_pk = note.notebook.pk if note.notebook else -1
        if anb and notebook_pk != anb.pk:
            return False

        return True

    def _on_notes_loaded(self, *args):
        log.debug('Notes loaded')
        if self.application_state.notes:
            self.application_state.active_note = self.notes_listbox.get_row_at_index(0).get_child().note

    def _on_active_notebook_changed(self, state, *args):
        """Re-filter notes list when active notebook is changed."""
        self.notes_listbox.invalidate_filter()

    def _header_func(self, row: Gtk.ListBoxRow, before: Union[Gtk.ListBoxRow, None], user_data):
        """
        Build notes list header. Note that pinned notes, must all come
        first in the list for this impl to work.
        """
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

        note: Note = row.get_child().note
        if not before:
            if note.pinned:
                row.set_header(create_header('Pinned'))
            else:
                row.set_header(create_header('Other Notes'))
            return

        before_note: Note = before.get_child().note
        if before_note.pinned and not note.pinned:
            row.set_header(create_header('Other Notes'))
            return

        row.set_header(None)


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

        time_lbl = Gtk.Label(label=note.last_updated_formatted)
        note.bind_property('last_updated_formatted', time_lbl, 'label', 0)
        time_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        top.add(time_lbl)
        top.set_child_packing(time_lbl, False, False, 10, Gtk.PackType.END)

        inner_box.add(top)
        inner_box.set_child_packing(top, False, False, 0, Gtk.PackType.START)

        bottom = Gtk.Label(label=note.get_body_preview())
        note.bind_property('body_preview', bottom, 'label', 0)
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
