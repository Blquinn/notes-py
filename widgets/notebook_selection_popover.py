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

from gi.repository import Gtk, Pango

from widgets.edit_notebooks_dialog import EditNotebooksDialog
from widgets.models import ApplicationState
from models.models import NoteBook

log = logging.getLogger(__name__)


@Gtk.Template.from_file('ui/NotebookSelectionPopover.ui')
class NotebookSelectionPopover(Gtk.PopoverMenu):
    __gtype_name__ = 'NotebookSelectionPopover'

    notebooks_list: Gtk.ListBox = Gtk.Template.Child()
    all_notebooks_button: Gtk.Button = Gtk.Template.Child()

    def __init__(self, state: ApplicationState):
        super(NotebookSelectionPopover, self).__init__()
        self.application_state = state
        self.notebooks_list.bind_model(state.notebooks, self._create_notebook_widget)
        self.notebooks_list.set_header_func(self._create_header, None)
        self.application_state.connect('notify::active-notebook', self._on_active_notebook_changed)

    def _create_header(self, row: Gtk.ListBoxRow, before, user_data):
        # Only set header on first row
        if before:
            return

        lbl = Gtk.Label(label='Notebooks')
        lbl.set_halign(Gtk.Align.START)
        lbl.get_style_context().add_class('list-header')
        row.set_header(lbl)

    def _create_notebook_widget(self, notebook: NoteBook):
        return NoteBookWidget(notebook)

    def _on_active_notebook_changed(self, *args):
        """ Ensure the correct row is selected when active notebook changes. """
        for row in self.notebooks_list:
            nbw: NoteBookWidget = row.get_child()
            if nbw.notebook == self.application_state.active_notebook:
                self.notebooks_list.select_row(row)
                break

    @Gtk.Template.Callback('on_edit_notebooks_button_clicked')
    def _on_edit_notebooks_button_clicked(self, btn):
        diag = EditNotebooksDialog(self.application_state, transient_for=self.get_toplevel())
        diag.show()

    @Gtk.Template.Callback('on_notebooks_list_row_activated')
    def _on_notebooks_list_row_activated(self, list_box, row: Gtk.ListBoxRow):
        self.application_state.show_trash = False
        nb = self.application_state.notebooks[row.get_index()]
        self.application_state.active_notebook = nb
    
    @Gtk.Template.Callback('on_all_notebooks_button_clicked') 
    def _on_all_notebooks_button_clicked(self, btn):
        self.application_state.show_trash = False
        self.application_state.active_notebook = None
        self.notebooks_list.unselect_all()

    @Gtk.Template.Callback('on_show_trash_button_clicked')
    def _on_show_trash_button_clicked(self, btn, *args):
        log.debug('Show trash pressed.')

        self.application_state.active_notebook = None
        self.application_state.show_trash = True
        self.notebooks_list.unselect_all()


class NoteBookWidget(Gtk.Label):
    def __init__(self, notebook: NoteBook):
        super().__init__()

        self.notebook = notebook

        self.set_label(notebook.name)
        notebook.bind_property('name', self, 'label', 0)
        self.set_ellipsize(Pango.EllipsizeMode.END)
        self.set_halign(Gtk.Align.START)
        self.set_max_width_chars(25)
