# -*- coding: utf-8 -*-
# Copyright (c) 2020, Benjamin Quinn <benlquinn@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, see <http://www.gnu.org/licenses/>.
import time
from datetime import datetime

from gi.repository import GObject, Gtk

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
                 last_updated: float = None):
        super().__init__()

        self.pk = pk
        self._title = title
        self._pinned = pinned
        self._notebook = notebook
        self._trash = trash
        self._last_updated = last_updated or time.time()
        self._last_updated_fmt = self.format_last_updated(self._last_updated)
        self.body = body or UndoableBuffer()
        self.body_preview = self.get_body_preview()

    # Properties

    @GObject.Property(type=str)
    def last_updated_formatted(self) -> str:
        return self._last_updated_fmt

    @last_updated_formatted.setter
    def set_updated_formatted(self, luf: str):
        self._last_updated_fmt = luf

    @GObject.Property(type=float)
    def last_updated(self):
        return self._last_updated

    @last_updated.setter
    def set_last_updated(self, lu: float):
        self._last_updated = lu
        self.last_updated_formatted = self.format_last_updated(lu)

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

    @GObject.Property(type=str)
    def body_preview(self) -> str:
        return self._body_preview

    @body_preview.setter
    def set_body_preview(self, preview: str):
        self._body_preview = preview

    def __str__(self):
        return f'Note(id={self.pk}, title={self._title})'

    def __repr__(self):
        return str(self)

    def get_body_preview(self) -> str:
        start: Gtk.TextIter = self.body.get_start_iter()
        end = start.copy()
        end.forward_chars(200)
        return self.body.get_text(start, end, False)

    @staticmethod
    def format_last_updated(last_updated: float) -> str:
        now = datetime.now()
        midnight = datetime.combine(now, datetime.min.time())

        lud = datetime.fromtimestamp(last_updated)

        if lud > midnight:
            return lud.strftime('%H:%M')

        if lud.year < now.year:
            return str(lud.year)

        return lud.strftime('%h %d')
