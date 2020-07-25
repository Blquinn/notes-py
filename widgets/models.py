from typing import Union

from gi.repository import GObject, Gio

from models.db import NoteBookDao, NoteDao
from models.models import Note, NoteBook


class ApplicationState(GObject.Object):
    __gtype_name__ = "ApplicationState"

    def __init__(self):
        super(ApplicationState, self).__init__()

        # self._initializing_state = False

        self._notebook_dao = NoteBookDao()
        self._note_dao = NoteDao()

        self.notes: Gio.ListStore[Note] = Gio.ListStore().new(Note)
        self.notebooks: Gio.ListStore[NoteBook] = Gio.ListStore().new(NoteBook)

        self._active_note: Union[Note, None] = None
        self._active_notebook: Union[NoteBook, None] = None

    # Properties

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

    @GObject.Property(type=bool, default=False)
    def initializing_state(self) -> bool:
        return self._initializing_state

    @initializing_state.setter
    def set_initializing_state(self, initializing: bool):
        self._initializing_state = initializing

    # Methods

    def initialize_state(self):
        """ Initialize state loads the initial state from the local db. """

        self.initializing_state = True

        def _on_done(fut):
            try:
                (notes, notebooks) = fut.result()
                for notebook in notebooks:
                    self.notebooks.append(notebook)

                for note in notes:
                    self.notes.append(note)
            finally:
                self.initializing_state = False

        self._note_dao.get_all_notes_and_notebooks().add_done_callback(_on_done)
