import gi

from utils import debounce

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


@debounce(2000)
def handle_click(btn):
    print('clicked')


if __name__ == '__main__':
    win = Gtk.ApplicationWindow()
    btn = Gtk.Button(label='Click me')
    btn.connect('clicked', handle_click)
    win.add(btn)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
