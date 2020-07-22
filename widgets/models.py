from typing import Union

from gi.repository import GObject, Gio

from models.models import Note, NoteBook


class ApplicationState(GObject.Object):
    __gtype_name__ = "ApplicationState"

    def __init__(self):
        super(ApplicationState, self).__init__()

        self.notes: Gio.ListStore[Note] = Gio.ListStore().new(Note)
        self.notebooks: Gio.ListStore[NoteBook] = Gio.ListStore().new(NoteBook)

        self._active_note: Union[Note, None] = None
        self._active_notebook: Union[NoteBook, None] = None

    @GObject.Property(type=Note)
    def active_note(self) -> Note:
        return self._active_note

    @active_note.setter
    def set_active_note(self, note: Note):
        self._active_note = note

    @GObject.Property(type=NoteBook)
    def active_notebook(self) -> NoteBook:
        return self._active_notebook

    @active_notebook.setter
    def set_active_notebook(self, notebook: NoteBook):
        self._active_notebook = notebook
