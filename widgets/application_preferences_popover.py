from gi.repository import Gtk


@Gtk.Template.from_file('ui/ApplicationPreferencesPopover.ui')
class ApplicationPreferencesPopover(Gtk.PopoverMenu):
    __gtype_name__ = 'ApplicationPreferencesPopover'

    def __init__(self):
        super(ApplicationPreferencesPopover, self).__init__()
