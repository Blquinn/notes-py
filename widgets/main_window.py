from gi.repository import Gtk

from widgets.editor_buffer import UndoableBuffer
from widgets.rich_editor import RichEditor


@Gtk.Template.from_file('ui/MainWindow.ui')
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'MainWindow'

    editor_scrolled_window: Gtk.ScrolledWindow = Gtk.Template.Child()
    editor: RichEditor = None

    def __init__(self):
        super(MainWindow, self).__init__()
        self.editor = RichEditor()
        self.editor.show()
        self.editor.set_margin_top(10)
        self.editor.set_margin_start(30)
        self.editor.set_margin_end(30)
        self.editor_scrolled_window.add(self.editor)

        buf: UndoableBuffer = self.editor.get_buffer()
        it = buf.get_start_iter()
        buf.insert_markup(it, '<b>Bold text</b>\n', -1)
        buf.insert_markup(it, '<i>Italics text</i>\n', -1)
        buf.insert(it, '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nFoobar', -1)

    # @Gtk.Template.Callback('on_button_pressed')
    # def _on_button_pressed(self, btn):
    #     self.label.set_text('I was pressed')

    @Gtk.Template.Callback('on_undo_button_clicked')
    def _on_undo_button_clicked(self, btn):
        self.editor.buffer.undo()

    @Gtk.Template.Callback('on_redo_button_clicked')
    def _on_redo_button_clicked(self, btn):
        self.editor.buffer.redo()
