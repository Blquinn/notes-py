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

from gi.repository import Gtk

from models.models import Note
from widgets.models import ApplicationState
from widgets.move_note_dialog import MoveNoteDialog

log = logging.getLogger(__name__)


@Gtk.Template.from_file("ui/NoteActionsPopover.ui")
class NoteActionsPopover(Gtk.PopoverMenu):
    __gtype_name__ = 'NoteActionsPopover'

    open_in_window_button: Gtk.Button = Gtk.Template.Child()
    move_to_trash_button: Gtk.Button = Gtk.Template.Child()

    def __init__(self, main_window, state: ApplicationState, note: Note = None):
        super(NoteActionsPopover, self).__init__()

        self.main_window = main_window
        self.note = note
        self.application_state = state
        self.set_note(note)

    def set_note(self, note: Note):
        self.note = note
        if not note:
            return

        if note.trash:
            self.move_to_trash_button.set_label('Remove From Trash')
        else:
            self.move_to_trash_button.set_label('Move to Trash')
        self.move_to_trash_button.set_halign(Gtk.Align.START)

    @Gtk.Template.Callback('on_move_to_button_clicked')
    def _on_move_to_button_clicked(self, btn):
        note = self.note if self.note else self.application_state.active_note
        diag = MoveNoteDialog(self.main_window, note, self.application_state,
                              transient_for=self.get_toplevel())
        diag.show_all()

    @Gtk.Template.Callback('on_pin_button_clicked')
    def _on_pin_button_clicked(self, btn, *args):
        is_pinned = not self.note.pinned
        self.note.pinned = is_pinned
        log.debug('Setting note %s pinned to %s', self.note, is_pinned)
        self.application_state.update_note(self.note)
        self.application_state.note_changed.emit()
        
    @Gtk.Template.Callback('on_move_to_trash_button_clicked')
    def _on_move_to_trash_button_clicked(self, btn):
        self.note.trash = not self.note.trash
        self.application_state.update_note(self.note)
        self.application_state.note_changed.emit()
