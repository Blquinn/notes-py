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
