from gi.repository import Gtk

from widgets.application_preferences_popover import ApplicationPreferencesPopover
from widgets.editor_buffer import UndoableBuffer
from widgets.editor_options_popover import EditorOptionsPopover
from widgets.rich_editor import RichEditor

# TODO: Split into multiple widgets
# Note: We can keep state by keeping the text buffers in memory and swapping the active buffer
# https://python-gtk-3-tutorial.readthedocs.io/en/latest/textview.html


@Gtk.Template.from_file('ui/MainWindow.ui')
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'MainWindow'

    editor_scrolled_window: Gtk.ScrolledWindow = Gtk.Template.Child()
    editor: RichEditor = None
    header_main: Gtk.HeaderBar = Gtk.Template.Child()
    header_side: Gtk.HeaderBar = Gtk.Template.Child()
    text_style_bar: Gtk.ButtonBox = Gtk.Template.Child()
    note_selection_box: Gtk.Box = Gtk.Template.Child()
    note_selection_button_label: Gtk.Label = Gtk.Template.Child()

    def __init__(self):
        super(MainWindow, self).__init__()
        self.editor = RichEditor()
        # self.editor.show()
        self.editor.set_margin_top(10)
        self.editor.set_margin_start(30)
        self.editor.set_margin_end(30)
        self.editor_scrolled_window.add(self.editor)

        Gtk.StyleContext.add_class(self.text_style_bar.get_style_context(), "linked")

        sel_label_arrow = Gtk.Image().new_from_icon_name('arrow-down', Gtk.IconSize.SMALL_TOOLBAR)
        sel_label_arrow.set_margin_start(3)
        self.note_selection_box.add(sel_label_arrow)

        self.editor_actions_button = Gtk.MenuButton()
        self.editor_actions_button.add(
            Gtk.Image().new_from_icon_name('view-more', Gtk.IconSize.LARGE_TOOLBAR)
        )
        self.header_main.pack_end(self.editor_actions_button)

        self.editor_options_popover = EditorOptionsPopover()
        self.editor_actions_button.set_popover(self.editor_options_popover)

        self.add_note_button = Gtk.Button()
        self.add_note_button.add(Gtk.Image().new_from_icon_name('add', Gtk.IconSize.LARGE_TOOLBAR))
        self.header_side.pack_start(self.add_note_button)

        self.preferences_button = Gtk.MenuButton()
        self.preferences_button.add(Gtk.Image().new_from_icon_name('view-list-text', Gtk.IconSize.LARGE_TOOLBAR))
        self.header_side.pack_end(self.preferences_button)
        
        self.application_preferences_popover = ApplicationPreferencesPopover()
        self.preferences_button.set_popover(self.application_preferences_popover)

        # TODO: Remove me
        buf: UndoableBuffer = self.editor.get_buffer()
        it = buf.get_start_iter()
        buf.insert_markup(it, '<b>Bold text</b>\n', -1)
        buf.insert_markup(it, '<i>Italics text</i>\n', -1)
        buf.insert(it, '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nFoobar', -1)
