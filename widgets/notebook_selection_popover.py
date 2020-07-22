from typing import List

from gi.repository import Gtk

from widgets.edit_notebooks_dialog import EditNotebooksDialog
from widgets.models import ApplicationState
from models.models import NoteBook


@Gtk.Template.from_file('ui/NotebookSelectionPopover.ui')
class NotebookSelectionPopover(Gtk.PopoverMenu):
    __gtype_name__ = 'NotebookSelectionPopover'

    notebooks_list: Gtk.ListBox = Gtk.Template.Child()

    def __init__(self, state: ApplicationState):
        super(NotebookSelectionPopover, self).__init__()
        self.notebooks_list.bind_model(state.notebooks, self._create_notebook_widget)
        self.notebooks_list.set_header_func(self._create_header, None)

    def _create_header(self, row: Gtk.ListBoxRow, before, user_data):
        # Only set header on first row
        if before:
            return

        lbl = Gtk.Label(label='Notebooks')
        lbl.set_halign(Gtk.Align.START)
        lbl.get_style_context().add_class('list-header')
        row.set_header(lbl)

    def _create_notebook_widget(self, notebook: NoteBook):
        lbl = Gtk.Label(label=notebook.name)
        lbl.set_halign(Gtk.Align.START)
        return lbl
    
    @Gtk.Template.Callback('on_edit_notebooks_button_clicked')
    def _on_edit_notebooks_button_clicked(self, btn):
        diag = EditNotebooksDialog()
        diag.set_transient_for(self.get_parent())
        diag.show()

    # TODO: Set filter on row activate
    # TODO: Fix color of listbox
