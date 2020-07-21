from gi.repository import Gtk


@Gtk.Template.from_file('ui/EditNotebooksDialog.ui')
class EditNotebooksDialog(Gtk.Dialog):
    __gtype_name__ = 'EditNotebooksDialog'

    new_notebook_entry: Gtk.Entry = Gtk.Template.Child()

    def __init__(self):
        super(EditNotebooksDialog, self).__init__(use_header_bar=True)
