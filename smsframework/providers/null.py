from ..IProvider import IProvider


class NullProvider(IProvider):
    """ Null Provider

        Configuration: nothing

        Sending: does nothing, but increments message.msgid

        Receipt: Not implemented
    """

    def __init__(self, gateway, name, **config):
        super(NullProvider, self).__init__(gateway, name, **config)
        self._msgid = 0

    def send(self, message):
        """
            :type message: smsframework.data.OutgoingMessage.OutgoingMessage
        """
        self._msgid += 1
        message.msgid = str(self._msgid)
        return message
