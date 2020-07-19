import logging

from gi.repository import Gtk, Gdk
from widgets.editor_buffer import UndoableBuffer

log = logging.getLogger(__name__)


class RichEditor(Gtk.TextView):
    buffer: UndoableBuffer = None

    def __init__(self):
        super(RichEditor, self).__init__()
        self.buffer = UndoableBuffer()
        self.set_buffer(self.buffer)
        # self.set_events(Gdk.EventMask.KEY_PRESS_MASK)
        self.connect('key-press-event', self._on_key_pressed)
        # self.connect('', self._on_range_selected)

    def get_buffer(self) -> UndoableBuffer:
        return self.buffer

    def _on_key_pressed(self, editor, key_event: Gdk.EventKey):
        # Ctrl+y (Redo)
        if key_event.state & Gdk.ModifierType.CONTROL_MASK and key_event.keyval == Gdk.KEY_y:
            log.debug('Redo pressed')
            self.buffer.redo()
            return

        # Ctrl+Shift+z (Undo)
        if (key_event.state & Gdk.ModifierType.CONTROL_MASK) and key_event.keyval == Gdk.KEY_z:
            log.debug('Undo pressed')
            self.buffer.undo()

    def _on_range_selected(self):
        pass
