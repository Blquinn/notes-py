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
from gi.repository import GLib


def debounce(timeout_millis: int):
    """ Debounce decorator that uses GLib's timeout function for timing. """

    def decorator(fn):
        def debounced(*args, **kwargs):
            def call_fn():
                delattr(debounced, 't')
                fn(*args, **kwargs)

            if hasattr(debounced, 't'):
                GLib.source_remove(debounced.t)

            debounced.t = GLib.timeout_add(timeout_millis, call_fn)
        return debounced
    return decorator
