import logging

from gi.repository import Gtk, Gdk

from models.models import NoteBook
from utils import debounce
from widgets.models import ApplicationState

log = logging.getLogger(__name__)


@Gtk.Template.from_file('ui/EditNotebooksDialog.ui')
class EditNotebooksDialog(Gtk.Dialog):
    __gtype_name__ = 'EditNotebooksDialog'

    new_notebook_entry: Gtk.Entry = Gtk.Template.Child()
    notebook_list: Gtk.ListBox = Gtk.Template.Child()

    def __init__(self, state: ApplicationState):
        super(EditNotebooksDialog, self).__init__(use_header_bar=True)

        self.application_state = state
        self.notebook_list.bind_model(state.notebooks, self._create_notebook_widget)

    def _create_notebook_widget(self, notebook: NoteBook):
        ni = NoteBookListItem(notebook)
        ni.show_all()
        return ni


class NoteBookListItem(Gtk.EventBox):
    def __init__(self, notebook: NoteBook):
        super().__init__()

        self.notebook = notebook

        outer_box = Gtk.VBox()

        inner_box = Gtk.HBox()

        inner_box.set_margin_top(7)
        inner_box.set_margin_bottom(9)
        inner_box.set_margin_start(8)

        outer_box.add(inner_box)

        self.add(outer_box)
        self.entry = Gtk.Entry()
        self.entry.set_text(notebook.name)
        inner_box.add(self.entry)
        inner_box.set_child_packing(self.entry, True, True, 0, Gtk.PackType.START)
        btn = Gtk.Button(image=Gtk.Image().new_from_icon_name('edit-delete-symbolic', Gtk.IconSize.BUTTON))
        btn.get_style_context().add_class('circular')
        btn.get_style_context().add_class('flat')
        btn.set_margin_start(10)
        btn.set_margin_end(10)
        inner_box.add(btn)
        inner_box.set_child_packing(btn, False, True, 0, Gtk.PackType.START)

        outer_box.add(Gtk.Separator())

        self.entry.connect('changed', debounce(500)(self._on_entry_changed))

    def _on_entry_changed(self, entry: Gtk.Entry):
        log.debug(f'Notebook name changed to {entry.get_text()}')
        self.notebook.name = entry.get_text()
