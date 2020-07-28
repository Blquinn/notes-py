import logging

from gi.repository import Gtk

from models.models import NoteBook
from utils import debounce
from widgets.models import ApplicationState

log = logging.getLogger(__name__)


@Gtk.Template.from_file('ui/EditNotebooksDialog.ui')
class EditNotebooksDialog(Gtk.Dialog):
    __gtype_name__ = 'EditNotebooksDialog'

    new_notebook_entry: Gtk.Entry = Gtk.Template.Child()
    notebook_list: Gtk.ListBox = Gtk.Template.Child()

    def __init__(self, state: ApplicationState, *args, **kwargs):
        super().__init__(use_header_bar=True, *args, **kwargs)

        self.application_state = state
        self.notebook_list.bind_model(state.notebooks, self._create_notebook_widget)

    def _create_notebook_widget(self, notebook: NoteBook):
        ni = NoteBookListItem(self.application_state, notebook)
        ni.show_all()
        return ni
   
    @Gtk.Template.Callback('on_add_notebook_button_clicked') 
    def _on_add_notebook_button_clicked(self, btn):
        log.debug('Add notebook button clicked')
        self.application_state.add_new_notebook(self.new_notebook_entry.get_text())
        self.new_notebook_entry.set_text('')


class NoteBookListItem(Gtk.EventBox):
    def __init__(self, state: ApplicationState, notebook: NoteBook):
        super().__init__()

        self.application_state = state
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
        delete_button = Gtk.Button(image=Gtk.Image().new_from_icon_name('edit-delete-symbolic', Gtk.IconSize.BUTTON))
        delete_button.get_style_context().add_class('circular')
        delete_button.get_style_context().add_class('flat')
        delete_button.set_margin_start(10)
        delete_button.set_margin_end(10)
        inner_box.add(delete_button)
        inner_box.set_child_packing(delete_button, False, True, 0, Gtk.PackType.START)

        outer_box.add(Gtk.Separator())

        # Bindings

        delete_button.connect('clicked', self._on_delete_pressed)
        self._do_change_entry_debounced = debounce(500)(self.__do_change_entry)
        self.entry.connect('changed', self._on_entry_changed)

    def _on_delete_pressed(self, btn):
        log.debug('Delete notebook %s pressed.', self.notebook)

        confirm_diag = Gtk.MessageDialog(transient_for=self.get_toplevel(),
                                         modal=True,
                                         buttons=Gtk.ButtonsType.OK_CANCEL)
        
        confirm_diag.props.text = f'Are you sure you want to delete {self.notebook.name} and ' \
                                  f'all of its notes?'
        response = confirm_diag.run()
        if response == Gtk.ResponseType.OK:
            log.info('Deleting notebook %s', self.notebook)
            self.application_state.delete_notebook(self.notebook)

        confirm_diag.destroy()

    def __do_change_entry(self, new_name: str):
        """
        Do not call this fxn directly, rather call the debounced fxn.
        """
        self.notebook.name = new_name
        log.debug(f'Updating notebook {self.notebook}')
        self.application_state.update_notebook(self.notebook)

    def _on_entry_changed(self, entry: Gtk.Entry):
        name = entry.get_text()
        log.debug(f'Notebook name changed to {entry.get_text()}')
        self._do_change_entry_debounced(name)
