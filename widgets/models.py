from gi.repository import GObject


class Note(GObject.Object):
    __gtype_name__ = "Note"

    def __init__(self, title, body, pinned=False):
        super(Note, self).__init__()

        self.title = title
        self.body = body
        self.pinned = pinned
        self.last_updated = '12:22'
        self.notebook = 'Other'
