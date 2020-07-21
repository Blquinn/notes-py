import logging
from typing import Union

from gi.repository import Gtk, Gdk, Gio, Pango

from widgets.application_preferences_popover import ApplicationPreferencesPopover
from widgets.edit_notebooks_dialog import EditNotebooksDialog
from widgets.editor_buffer import UndoableBuffer
from widgets.models import Note, ApplicationState
from widgets.move_note_dialog import MoveNoteDialog
from widgets.note_actions_popover import NoteActionsPopover
from widgets.notebook_selection_popover import NotebookSelectionPopover
from widgets.rich_editor import RichEditor

log = logging.getLogger(__name__)

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
    note_selection_button: Gtk.MenuButton = Gtk.Template.Child()
    note_selection_button_label: Gtk.Label = Gtk.Template.Child()
    notes_listbox: Gtk.ListBox = Gtk.Template.Child()

    def __init__(self, state: ApplicationState):
        super(MainWindow, self).__init__()

        self.application_state = state

        self.editor = RichEditor()
        self.editor.set_margin_top(10)
        self.editor.set_margin_start(30)
        self.editor.set_margin_end(30)
        self.editor_scrolled_window.add(self.editor)

        self.editor_actions_button = Gtk.MenuButton()
        self.editor_actions_button.add(
            Gtk.Image().new_from_icon_name('view-more-symbolic', Gtk.IconSize.LARGE_TOOLBAR)
        )
        self.header_main.pack_end(self.editor_actions_button)

        self.editor_options_popover = NoteActionsPopover()
        self.editor_actions_button.set_popover(self.editor_options_popover)

        self.add_note_button = Gtk.Button()
        self.add_note_button.add(Gtk.Image().new_from_icon_name('value-increase-symbolic', Gtk.IconSize.BUTTON))
        self.header_side.pack_start(self.add_note_button)
        self.add_note_button.connect('clicked', self._on_add_notebook_button_pressed)

        self.preferences_button = Gtk.MenuButton()
        self.preferences_button.add(Gtk.Image().new_from_icon_name('view-list-text-symbolic', Gtk.IconSize.BUTTON))
        self.header_side.pack_end(self.preferences_button)
        
        self.application_preferences_popover = ApplicationPreferencesPopover()
        self.preferences_button.set_popover(self.application_preferences_popover)
       
        self.notebook_selection_popover = NotebookSelectionPopover(state)
        self.note_selection_button.set_popover(self.notebook_selection_popover)

        self.notes_model: Gio.ListStore = Gio.ListStore().new(Note)
        self.notes_listbox.bind_model(self.notes_model, self._create_sidebar_note_widget)

        def header_func(row: Gtk.ListBoxRow, before: Union[Gtk.ListBoxRow, None], user_data):
            note: Note = self.notes_model[row.get_index()]

            def create_header(text: str):
                box = Gtk.VBox()
                box.set_margin_top(10)

                lbl = Gtk.Label(label=text)
                lbl.set_halign(Gtk.Align.START)
                lbl.set_margin_start(10)
                # lbl.modify_font('')
                box.add(lbl)

                sep = Gtk.Separator()
                box.add(sep)
                box.show_all()

                return box

            if not before:
                if note.pinned:
                    row.set_header(create_header('Pinned'))
                else:
                    row.set_header(create_header('Other Notes'))
                return

            before_note: Note = self.notes_model[before.get_index()]
            if before_note.pinned and not note.pinned:
                row.set_header(create_header('Other Notes'))

        self.notes_listbox.set_header_func(header_func, None)

        for note in state.notes:
            self.notes_model.append(note)

        # TODO: Remove me
        buf: UndoableBuffer = self.editor.get_buffer()
        it = buf.get_start_iter()
        buf.insert_markup(it, '<b>Bold text</b>\n', -1)
        buf.insert_markup(it, '<i>Italics text</i>\n', -1)
        buf.insert(it, '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nFoobar', -1)

    def _on_add_notebook_button_pressed(self, btn):
        diag = EditNotebooksDialog()
        diag.set_transient_for(self)
        diag.show()

    @Gtk.Template.Callback('on_note_notebook_button_clicked')
    def _on_note_notebook_button_clicked(self, btn):
        diag = MoveNoteDialog(self.application_state.notes[0])
        diag.set_transient_for(self)
        diag.show()

    def _create_sidebar_note_widget(self, note: Note):
        return NoteListItem(note)


class NoteListItem(Gtk.EventBox):

    def __init__(self, note: Note):
        super(NoteListItem, self).__init__()

        self.note = note

        inner_box = Gtk.VBox()
        self.add(inner_box)

        top = Gtk.HBox()
        title_lbl = Gtk.Label(label=note.title)
        title_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        top.add(title_lbl)
        top.set_child_packing(title_lbl, False, False, 10, Gtk.PackType.START)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        top.add(spacer)

        time_lbl = Gtk.Label(label=note.last_updated)
        time_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        top.add(time_lbl)
        top.set_child_packing(time_lbl, False, False, 10, Gtk.PackType.END)

        inner_box.add(top)
        inner_box.set_child_packing(top, False, False, 0, Gtk.PackType.START)

        bottom = Gtk.Label(label=note.body)
        bottom.set_ellipsize(Pango.EllipsizeMode.END)
        bottom.set_lines(2)
        bottom.set_line_wrap(True)
        bottom.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        bottom.set_alignment(0.0, 0.5)
        bottom.set_margin_start(10)
        bottom.set_margin_end(10)

        inner_box.add(bottom)
        inner_box.set_child_packing(bottom, False, False, 10, Gtk.PackType.START)

        inner_box.add(Gtk.Separator())

        # Signals

        self.connect('button-press-event', self._on_button_press)

    def _on_button_press(self, item: 'NoteListItem', event: Gdk.EventButton):
        if event.button != Gdk.BUTTON_SECONDARY:  # Right click
            return

        log.debug(f'Note {item.note} right clicked.')

        popover = NoteActionsPopover(item.note)
        popover.set_relative_to(self)
        popover.show()
        popover.popup()
