from ..IProvider import IProvider


class NullProvider(IProvider):
    """ Null Provider

        Configuration: none

        Sending: does nothing, but increments message.msgid

        Receipt: Not implemented

        Status: Not implemented
    """

    def __init__(self, gateway, name):
        super(NullProvider, self).__init__(gateway, name)
        self._msgid = 0

    def send(self, message):
        self._msgid += 1
        message.msgid = str(self._msgid)
        return message
