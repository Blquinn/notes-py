from datetime import datetime

from gi.repository import GObject

from widgets.editor_buffer import UndoableBuffer


class NoteBook(GObject.Object):
    __gtype_name__ = "NoteBook"

    def __init__(self, name: str, pk: int = 0):
        super(NoteBook, self).__init__()
        self.pk = pk
        self._name = name

    @GObject.Property(type=str)
    def name(self) -> str:
        return self._name

    @name.setter
    def set_name(self, name: str):
        self._name = name

    def __str__(self):
        return f'NoteBook(id={self.pk}, name={self._name})'

    def __repr__(self):
        return str(self)


class Note(GObject.Object):
    __gtype_name__ = "Note"

    def __init__(self, title: str,
                 notebook: NoteBook,
                 pinned=False,
                 trash=False,
                 pk: int = 0,
                 body: UndoableBuffer = None,
                 last_updated: datetime = None):
        super().__init__()

        self.pk = pk
        self._title = title
        self._pinned = pinned
        self._notebook = notebook
        self._trash = trash
        self._last_updated = last_updated or datetime.now()
        self.body = body or UndoableBuffer()

    def format_last_updated(self) -> str:
        now = datetime.now()
        midnight = datetime.combine(now, datetime.min.time())

        if self._last_updated > midnight:
            return self._last_updated.strftime('%H:%M')

        if self._last_updated.year < now.year:
            return str(self._last_updated.year)

        return self._last_updated.strftime('%h %d')

    @GObject.Property(type=str)
    def title(self):
        return self._title if self._title else 'Untitled'

    @title.setter
    def set_title(self, title: str):
        self._title = title

    @GObject.Property(type=bool, default=False)
    def pinned(self):
        return self._pinned

    @pinned.setter
    def set_pinned(self, pinned: bool):
        self._pinned = pinned

    @GObject.Property(type=str)
    def last_updated(self):
        return self.format_last_updated()

    @GObject.Property(type=str)
    def last_updated_fmt(self):
        return self.format_last_updated()

    # @GObject.Property(type=datetime)
    @property
    def last_updated(self):
        return self._last_updated

    # @last_updated.setter
    @last_updated_fmt.setter
    def last_updated(self, lu: datetime):
        self._last_updated = lu

    @GObject.Property(type=bool, default=False)
    def trash(self):
        return self._trash

    @trash.setter
    def set_trash(self, trash: bool):
        self._trash = trash

    @GObject.Property(type=NoteBook, default=False)
    def notebook(self):
        return self._notebook

    @notebook.setter
    def set_notebook(self, nb: 'NoteBook'):
        self._notebook = nb

    def __str__(self):
        return f'Note(id={self.pk}, title={self._title})'

    def __repr__(self):
        return str(self)
