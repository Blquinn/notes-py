from datetime import datetime, timedelta

from gi.repository import GObject, Gtk


class Note(GObject.Object):
    __gtype_name__ = "Note"

    def __init__(self, title: str,
                 notebook: 'NoteBook',
                 pinned=False,
                 trash=False,
                 pk: int = 0,
                 body: Gtk.TextBuffer = None,
                 last_updated: datetime = None):
        super().__init__()

        self.pk = pk
        self.title = title
        self.body = body or Gtk.TextBuffer()
        self.pinned = pinned
        self.last_updated = '12:22'
        self.notebook = notebook
        self.trash = trash
        self.last_updated = last_updated or datetime.now()

    def format_last_updated(self) -> str:
        now = datetime.now()
        midnight = datetime.combine(now, datetime.min.time())

        if self.last_updated > midnight:
            return self.last_updated.strftime('%H:%M')

        if self.last_updated.year < now.year:
            return str(self.last_updated.year)

        return self.last_updated.strftime('%h %d')


class NoteBook(GObject.Object):
    __gtype_name__ = "NoteBook"

    def __init__(self, name: str, pk: int = 0):
        super(NoteBook, self).__init__()
        self.pk = pk
        self.name = name
