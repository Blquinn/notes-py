from gi.repository import Gtk


@Gtk.Template.from_file('ui/NotebookSelectionPopover.ui')
class NotebookSelectionPopover(Gtk.PopoverMenu):
    __gtype_name__ = 'NotebookSelectionPopover'

    def __init__(self):
        super(NotebookSelectionPopover, self).__init__()
