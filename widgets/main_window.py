from typing import Union

from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, GObject, Gio, Pango

from widgets.application_preferences_popover import ApplicationPreferencesPopover
from widgets.edit_notebooks_dialog import EditNotebooksDialog
from widgets.editor_buffer import UndoableBuffer
from widgets.note_actions_popover import NoteActionsPopover
from widgets.notebook_selection_popover import NotebookSelectionPopover
from widgets.rich_editor import RichEditor

# TODO: Split into multiple widgets
# Note: We can keep state by keeping the text buffers in memory and swapping the active buffer
# https://python-gtk-3-tutorial.readthedocs.io/en/latest/textview.html


class Note(GObject.Object):
    __gtype_name__ = "Note"

    def __init__(self, title, body, pinned=False):
        super(Note, self).__init__()

        self.title = title
        self.body = body
        self.pinned = pinned
        self.last_updated = '12:22'
        self.notebook = 'Other'


notes = [
    Note('Jobs to do', 'The most effective way to destroy people is to deny an obliterate their psyche.', pinned=True),
    Note('Gift Ideas', 'The most effective way to destroy people is to deny an obliterate their psyche.', pinned=True),
    Note('Pluto', 'The most effective way to destroy people is to deny an obliterate their psyche.', pinned=False),
    Note('Something else', 'The most effective way to destroy people is to deny an obliterate their psyche.', pinned=False),

    # Note('Jobs to do', 'The most effective way to destroy people is to deny an obliterate their psyche.', pinned=True),
    # Note('Gift Ideas', 'The most effective way to destroy people is to deny an obliterate their psyche.', pinned=True),
    # Note('Pluto', 'The most effective way to destroy people is to deny an obliterate their psyche.', pinned=False),
    # Note('Something else', 'The most effective way to destroy people is to deny an obliterate their psyche.', pinned=False),
]
# notes = [
#     Note(),
# ]


@Gtk.Template.from_file('ui/MainWindow.ui')
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'MainWindow'

    editor_scrolled_window: Gtk.ScrolledWindow = Gtk.Template.Child()
    editor: RichEditor = None
    header_main: Gtk.HeaderBar = Gtk.Template.Child()
    header_side: Gtk.HeaderBar = Gtk.Template.Child()
    text_style_bar: Gtk.ButtonBox = Gtk.Template.Child()
    note_selection_box: Gtk.Box = Gtk.Template.Child()
    note_selection_button: Gtk.MenuButton = Gtk.Template.Child()
    note_selection_button_label: Gtk.Label = Gtk.Template.Child()
    pinned_notes_list: Gtk.ListBox = Gtk.Template.Child()
    other_notes_list: Gtk.ListBox = Gtk.Template.Child()
    # note_viewport: Gtk.Viewport = Gtk.Template.Child()

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

        self.editor_options_popover = NoteActionsPopover()
        self.editor_actions_button.set_popover(self.editor_options_popover)

        self.add_note_button = Gtk.Button()
        self.add_note_button.add(Gtk.Image().new_from_icon_name('add', Gtk.IconSize.LARGE_TOOLBAR))
        self.header_side.pack_start(self.add_note_button)
        self.add_note_button.connect('clicked', self._on_add_notebook_button_pressed)

        self.preferences_button = Gtk.MenuButton()
        self.preferences_button.add(Gtk.Image().new_from_icon_name('view-list-text', Gtk.IconSize.LARGE_TOOLBAR))
        self.header_side.pack_end(self.preferences_button)
        
        self.application_preferences_popover = ApplicationPreferencesPopover()
        self.preferences_button.set_popover(self.application_preferences_popover)
       
        self.notebook_selection_popover = NotebookSelectionPopover()
        self.note_selection_button.set_popover(self.notebook_selection_popover)

        self.notes_model: Gio.ListStore = Gio.ListStore().new(Note)
        self.pinned_notes_list.bind_model(self.notes_model, self._create_sidebar_note_widget)
        self.other_notes_list.bind_model(self.notes_model, self._create_sidebar_note_widget)
        
        def header_func(row: Gtk.ListBoxRow, before: Union[Gtk.ListBoxRow, None], user_data):
            print(row)
            pass

        self.other_notes_list.set_header_func(header_func, None)
        self.pinned_notes_list.set_header_func(header_func, None)

        def filter_pinned(row: Gtk.ListBoxRow, user_data) -> bool:
            print(row.get_index(), user_data)
            return True

        def filter_not_pinned(row: Gtk.ListBoxRow, user_data) -> bool:
            print(row.get_index())
            # print(row.path())
            # row.
            # self.notes_model.get
            return False

        self.pinned_notes_list.set_filter_func(filter_pinned, None)
        self.other_notes_list.set_filter_func(filter_not_pinned, None)

        for note in notes:
            self.notes_model.append(note)

        # TODO: Remove me
        buf: UndoableBuffer = self.editor.get_buffer()
        it = buf.get_start_iter()
        buf.insert_markup(it, '<b>Bold text</b>\n', -1)
        buf.insert_markup(it, '<i>Italics text</i>\n', -1)
        buf.insert(it, '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nFoobar', -1)

    def _on_add_notebook_button_pressed(self, btn):
        diag = EditNotebooksDialog()
        diag.show()

    # def _populate_notes_list(self):
    def _create_sidebar_note_widget(self, item: GObject.Object):
        widget = Gtk.VBox()
        widget.set_size_request(-1, 80)
        widget.set_vexpand(True)

        top = Gtk.HBox()
        title_lbl = Gtk.Label(label='Jobs to do')
        title_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        top.add(title_lbl)
        top.set_child_packing(title_lbl, False, True, 10, Gtk.PackType.START)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        top.add(spacer)
        time_lbl = Gtk.Label(label='12:22')
        time_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        top.add(time_lbl)
        top.set_child_packing(time_lbl, False, True, 10, Gtk.PackType.END)

        widget.add(top)
        # widget.set_child_packing(top, True, True, 0, Gtk.PackType.START)

        bottom = Gtk.Label(label='The most effective way to destroy people is to deny an obliterate their psyche.')
        # bottom.set_vexpand(True)
        bottom.set_ellipsize(Pango.EllipsizeMode.END)
        bottom.set_lines(2)
        bottom.set_line_wrap(True)
        # bottom.set_line_wrap_mode(Pango.WrapMode.CHAR)
        bottom.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        bottom.set_alignment(0.0, 0.5)
        bottom.set_margin_start(10)
        bottom.set_margin_end(10)

        widget.add(bottom)
        widget.set_child_packing(bottom, False, True, 10, Gtk.PackType.START)
        return widget
