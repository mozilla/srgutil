"""
A Context is a customizable namespace.

It works like a regular dictionary, but allows you to set a delegate
explicitly to do attribute lookups.

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

    def contains(self, key):
        try:
            self.get(key)
            return True
        except KeyError:
            return False

    def get(self, key, default=NoDefault):
        # This is a little tricky, we want to lookup items in our
        # local namespace before we hit the delegate
        return self.__dict__.get(key, default)

    def set(self, key, value):
        self.__dict__[key] = value

    def delete(self, key):
        del self.__dict__[key]

    def impl(self, iface):
        instance = self.__dict__[iface]
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
