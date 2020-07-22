from gi.repository import GObject, Gio

from models.models import Note, NoteBook


class ApplicationState(GObject.Object):
    __gtype_name__ = "ApplicationState"

    def __init__(self):
        super(ApplicationState, self).__init__()

        self.notes: Gio.ListStore[Note] = Gio.ListStore().new(Note)
        self.notebooks: Gio.ListStore[NoteBook] = Gio.ListStore().new(NoteBook)
