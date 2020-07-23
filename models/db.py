import logging
import os
import sqlite3
import threading
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Any

from gi.repository import Gtk

from config import DATA_DIR
from models.models import Note, NoteBook
from widgets.editor_buffer import UndoableBuffer

log = logging.getLogger(__name__)
db_local = threading.local()


def initialize_db_thread(*args, **kwargs):
    """Initialize each thread pool worker with its own db connection"""
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    db_local.db = get_connection()
    log.info('Initialized db in thread %s', threading.get_ident())


# Serialize all access to sqlite connection via this single threaded executor.
# All access to sqlite should happen through the executor.
DB_EXECUTOR = ThreadPoolExecutor(max_workers=1, initializer=initialize_db_thread)


def get_connection() -> sqlite3.Connection:
    # Optionally override db path with env var
    path = os.getenv('DB_PATH') or f'{DATA_DIR}/storage.db'
    db = sqlite3.connect(path, 10.0)
    try:
        with db:
            db.execute("""
            create table notebooks (
                id integer primary key autoincrement,
                name text not null
            );
            """)

            db.execute("""
            create table notes (
                id integer primary key autoincrement,
                last_updated integer not null,
                notebook_id text references notebooks,
                title text not null,
                note_contents blob not null,
                is_in_trash boolean not null default false,
                is_pinned boolean not null default false
            );
            """)
    except sqlite3.OperationalError as e:
        pass

    return db


class DaoBase:
    def __init__(self, db: sqlite3.Connection = None):
        self._db = db

    @property
    def db(self) -> sqlite3.Connection:
        return self._db or db_local.db


class NoteBookDao(DaoBase):
    def save(self, notebook: NoteBook):
        def fn():
            with self.db:
                if notebook.pk:  # update
                    self.db.execute("""
                    update notebooks set name = ? where id = ? 
                    """, (notebook.name, notebook.pk))
                    return notebook

                res = self.db.execute("""
                insert into notebooks (name) values (?)
                """, (notebook.name,))
                notebook.pk = res.lastrowid
                return notebook

        return DB_EXECUTOR.submit(fn)

    def _find_all(self):
        with self.db:
            rows = self.db.execute(""" select id, "name" from notebooks """).fetchall()
            return [NoteBook(pk=r[0], name=r[1]) for r in rows]

    def find_all(self):
        return DB_EXECUTOR.submit(self._find_all)


class NoteDao(DaoBase):
    def __init__(self):
        super().__init__()
        self.notebook_dao = NoteBookDao()

    @staticmethod
    def read_note_row(row: Tuple[Any]) -> Note:
        buf = UndoableBuffer()
        fmt = buf.register_deserialize_tagset()
        notebook = NoteBook(name=row[6], pk=row[5])
        buf.deserialize(buf, fmt, buf.get_start_iter(), row[2])
        return Note(pk=row[0], title=row[1], body=buf, notebook=notebook,
                    pinned=bool(row[4]), trash=bool(row[3]),
                    last_updated=datetime.fromtimestamp(row[7]))

    def _get_all_notes(self) -> List[Note]:
        rows = self.db.execute("""
        select n.id, n.title, n.note_contents, n.is_in_trash, n.is_pinned, nb.id, 
            nb.name, n.last_updated
        from notes n
        inner join notebooks nb on n.notebook_id = nb.id
        order by n.is_pinned desc, n.last_updated desc
        """).fetchall()
        return [self.read_note_row(r) for r in rows]

    def get_all_notes(self):
        """
        Gets all notes from db.
        :return: Future[List[Note]]
        """
        return DB_EXECUTOR.submit(self._get_all_notes)

    def get_all_notes_and_notebooks(self):
        def fn():
            notes = self._get_all_notes()
            notebooks = self.notebook_dao._find_all()
            return notes, notebooks

        return DB_EXECUTOR.submit(fn)

    def save(self, note: Note):
        def fn() -> Note:
            fmt = note.body.register_serialize_tagset()
            start, end = note.body.get_bounds()
            buf_bytes = note.body.serialize(note.body, fmt, start, end)

            notebook_pk = None
            if note.notebook:
                notebook_pk = note.notebook.pk

            with self.db:
                if note.pk:  # Update
                    self.db.execute("""
                    update notes 
                    set notebook_id = ?, title = ?, note_contents = ?, is_in_trash = ?, 
                        is_pinned = ?, last_updated = strftime('%s', 'now')
                    where id = ? 
                    """, (notebook_pk, note.title, buf_bytes, note.trash, note.pinned, note.pk))
                    return note

                self.db.execute("""
                insert into notes (notebook_id, title, note_contents, is_in_trash, is_pinned, last_updated)
                values (?, ?, ?, ?, ?, strftime('%s', 'now'))
                """, (notebook_pk, note.title, buf_bytes, note.trash, note.pinned))

                return note

        return DB_EXECUTOR.submit(fn)
