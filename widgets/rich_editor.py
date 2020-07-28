import logging

from gi.repository import Gtk, Gdk

from widgets.editor_buffer import UndoableBuffer
from widgets.models import ApplicationState

log = logging.getLogger(__name__)


class RichEditor(Gtk.TextView):
    buffer: UndoableBuffer = None

    def __init__(self, state: ApplicationState, **kwargs):
        super(RichEditor, self).__init__(**kwargs)
        self.application_state = state
        self.buffer = UndoableBuffer()
        self.set_buffer(self.buffer)
        self.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.connect('key-press-event', self._on_key_pressed)

    def get_buffer(self) -> UndoableBuffer:
        return super().get_buffer()

    def set_buffer(self, buf: UndoableBuffer):
        super().set_buffer(buf)
        self.buffer = buf

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
