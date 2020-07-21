from gi.repository import GObject, Gio


class Note(GObject.Object):
    __gtype_name__ = "Note"

    def __init__(self, title, body, notebook: 'NoteBook', pinned=False):
        super(Note, self).__init__()

        self.title = title
        self.body = body
        self.pinned = pinned
        self.last_updated = '12:22'
        self.notebook = notebook


class NoteBook(GObject.Object):
    __gtype_name__ = "NoteBook"

    def __init__(self, name: str):
        super(NoteBook, self).__init__()
        self.name = name


class ApplicationState(GObject.Object):
    __gtype_name__ = "ApplicationState"

    def __init__(self):
        super(ApplicationState, self).__init__()

        self.notes: Gio.ListStore[Note] = Gio.ListStore().new(Note)
        self.notebooks: Gio.ListStore[NoteBook] = Gio.ListStore().new(NoteBook)
