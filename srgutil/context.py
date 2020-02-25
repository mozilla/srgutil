"""
A Context is a customizable namespace.

It works like a regular dictionary, but allows you to set a delegate
explicitly to do attribute lookups.

The primary benefit is that the context has a .child() method which
lets you 'lock' a dictionary and clobber the namespace without
affecting parent contexts.

In practice this makes testing easier and allows us to specialize
configuration information as we pass the context through an object
chain.
"""

from srgutil.interfaces import IS3Data, IClock, IMozLogging


class NoDefault:
    pass

class InvalidInterface(Exception):
    """Raise this when impl() fails to export an implementation"""
    pass


class Context:
    def __init__(self, delegate=None):
        if delegate is None:
            delegate = {}

        self._local_dict = {}
        self._delegate = delegate

    def contains(self, key):
        try:
            self.get(key)
            return True
        except KeyError:
            return False

    def get(self, key, default=NoDefault):
        # This is a little tricky, we want to lookup items in our
        # local namespace before we hit the delegate
        try:
            return self._local_dict[key]
        except KeyError:
            try:
                return self._delegate.get(key)
            except KeyError:
                if default is not NoDefault:
                    return default
                raise

    def set(self, key, value):
        self._local_dict[key] = value

    def delete(self, key):
        del self._local_dict[key]

    def wrap(self, ctx):
        ctx_child = ctx.child()
        this_child = self.child()
        this_child._delegate = ctx_child
        return this_child

    def child(self):
        """ In general, you should call this immediately in any
        constructor that receives a context """

        return Context(self)

    def impl(self, iface):
        instance = self._local_dict[iface]
        if not isinstance(instance, iface):
            raise InvalidInterface("Instance [%s] doesn't implement requested interface.")
        return instance


def default_context():
    ctx = Context()
    from .base import Clock, S3Data
    from .log import Logging

    ctx.set(IClock, Clock())
    ctx.set(IS3Data, S3Data(ctx))
    ctx.set(IMozLogging, Logging(ctx))
    return ctx
