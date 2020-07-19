import logging

from gi.repository import Gtk

log = logging.getLogger(__name__)


@Gtk.Template.from_file("ui/EditorOptionsPopover.ui")
class EditorOptionsPopover(Gtk.PopoverMenu):
    __gtype_name__ = 'EditorOptionsPopover'

    open_in_window_button = Gtk.Template.Child()

    def __init__(self):
        super(EditorOptionsPopover, self).__init__()
       
    @Gtk.Template.Callback('on_open_in_window_button_clicked')
    def _on_open_in_window_button_clicked(self, btn):
        # TODO: Implement me
        log.warning('on_open_in_window_button_clicked was clicked, but is not implemented.')
