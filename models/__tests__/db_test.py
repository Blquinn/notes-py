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
import unittest

from models.db import NoteDao, NoteBookDao
from models.models import NoteBook, Note


class NoteDaoTest(unittest.TestCase):
    def setUp(self) -> None:
        self.notebook_dao = NoteBookDao()
        self.dao = NoteDao()

    def test_save_note(self):
        notebook = self.notebook_dao.save(NoteBook('Astronomy')).result()
        note = Note('Pluto', notebook)
        note.body.set_text('Lorem Ipsum skjd lfjfkle lk3j2l 3jlkjfljlk f2lekfjle jflk2jldkjflekjl2 jflk2. '
                           '2 el2kefj l2ek.l l32kj 2lk3432lk4j2 lk23lk42lkj3 42lk34lk23lkj4lkj23 4234l2'
                           'l234lkj2 j42lk34lkj2j423k2lkj3 lkj243lkj23lkj42 jlk4 lk43lk23lkj42 34lk24l.')
        note = self.dao.save(note).result()
        self.assertEqual(note.title, 'Pluto')
        self.assertEqual(notebook.name, 'Astronomy')

        notes = self.dao.get_all_notes().result()
        self.assertTrue('Pluto' in (n.title for n in notes))


if __name__ == '__main__':
    unittest.main()
