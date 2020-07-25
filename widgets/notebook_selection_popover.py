from typing import List

from gi.repository import Gtk, Pango, GObject

from widgets.edit_notebooks_dialog import EditNotebooksDialog
from widgets.models import ApplicationState
from models.models import NoteBook


@Gtk.Template.from_file('ui/NotebookSelectionPopover.ui')
class NotebookSelectionPopover(Gtk.PopoverMenu):
    __gtype_name__ = 'NotebookSelectionPopover'

    notebooks_list: Gtk.ListBox = Gtk.Template.Child()

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
        diag = EditNotebooksDialog(self.application_state)
        diag.set_transient_for(self.get_parent())
        diag.show()

    @Gtk.Template.Callback('on_notebooks_list_row_activated')
    def _on_notebooks_list_row_activated(self, list_box, row: Gtk.ListBoxRow):
        nb = self.application_state.notebooks[row.get_index()]
        self.application_state.active_notebook = nb
    
    @Gtk.Template.Callback('on_all_notebooks_button_clicked') 
    def _on_all_notebooks_button_clicked(self, btn):
        self.application_state.active_notebook = None
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
