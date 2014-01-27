class EventHook(object):
    """ Event Pattern

        Create:
            event = EventHook()
        Subscribe:
            event += handler
        Unsubscribe:
            event -= handler
        Fire:
            event(...)

        Based on: http://www.voidspace.org.uk/python/weblog/arch_d7_2007_02_03.shtml#e616
    """

    def __init__(self):
        self.__handlers = []

    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.__handlers.remove(handler)
        return self

    def __call__(self, *args, **kwargs):
        for handler in self.__handlers:
            handler(*args, **kwargs)
