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
import logging
from typing import Union

from gi.repository import GObject, Gio

from models.db import NoteBookDao, NoteDao
from models.models import Note, NoteBook
from utils import debounce

log = logging.getLogger(__name__)


class ApplicationState(GObject.Object):
    __gtype_name__ = "ApplicationState"

    note_pinned = GObject.Signal()

    def __init__(self):
        super(ApplicationState, self).__init__()

        self._initializing_state = False

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

    # @debounce(500)
    def _on_note_body_changed(self, buf, note: Note):
        log.debug('Updating note %s', note)
        self.update_note(note)

    def initialize_state(self):
        """ Initialize state loads the initial state from the local db. """
        log.info('Initializing application state.')

        self.initializing_state = True

        def _on_done(fut):
            try:
                (notes, notebooks) = fut.result()
                for notebook in notebooks:
                    self.notebooks.append(notebook)

                for note in notes:
                    note.body.connect('changed', debounce(500)(self._on_note_body_changed), note)
                    self.notes.append(note)

                log.info('Initialized app state.')
            finally:
                self.initializing_state = False

        self._note_dao.get_all_notes_and_notebooks().add_done_callback(_on_done)

    # TODO: Fix header section bug
    def add_new_note(self):
        note = Note('', self.active_notebook)

        # Insert as first non-pinned note in notebook
        self.notes.insert_sorted(note, lambda a, b: int(not a.pinned))
        self.active_note = note

        def on_done(saved_note_fut):
            note.pk = saved_note_fut.result().pk

        self._note_dao.save(note).add_done_callback(on_done)

    def add_new_notebook(self, name: str):
        if not name.strip():
            return

        notebook = NoteBook(name)
        self._notebook_dao.save(notebook)
        self.notebooks.append(notebook)
        self.active_notebook = notebook

    def update_note(self, note: Note):
        log.debug('Updating note %s', note)
        self._note_dao.save(note)

    def update_notebook(self, notebook: NoteBook):
        log.debug('Updating notebook %s', notebook)
        self._notebook_dao.save(notebook)

    def move_note_to_trash(self, note: Note):
        note.trash = True
        self._note_dao.save(note)

    def delete_notebook(self, notebook: NoteBook):
        log.info('Deleting notebook %s', notebook)

        self._notebook_dao.delete(notebook)

        for note in self.notes:
            if note.notebook == notebook:
                note.trash = True

        found, nb_idx = self.notebooks.find(notebook)
        if found:
            self.notebooks.remove(nb_idx)

        if self.notebooks.get_n_items():
            self.active_notebook = self.notebooks[0]
        else:
            self.active_notebook = None
