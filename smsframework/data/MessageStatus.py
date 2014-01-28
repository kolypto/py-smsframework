class MessageStatus(object):
    """ Sent Message Status

        Represent network's response to a sent message.
    """

    #: Provider name
    provider = None

    #: Was the message accepted by the network?
    #: True | False | None (unknown)
    accepted = None

    #: Was the message delivered to the recipient?
    #: True | False | None (unknown)
    delivered = None

    #: Has the mesage expired?
    #: True | False
    expired = False

    #: Status text from the provider, if any
    status = None

    #: Error string, if any
    error = None

    #: Provider-dependent info dict, if any
    meta = None

    def __init__(self, msgid, status=None, meta=None, error=None):
        """ Create the message status struct

            :type msgid: str
            :param msgid: Unique message id
            :type status: str | None
            :param status: Status text
            :type meta: dict | None
            :param meta: Provider-dependent info
            :type error: str | None
            :param error: Error string, if any
        """
        self.msgid = msgid
        self.status = status
        self.meta = meta or {}

    def __repr__(self):
        return '{cls}({provider!r}, {msgid!r}, status={status!r}, error={error!r})'.format(
            cls=self.__class__.__name__,
            provider=self.provider,
            msgid=self.msgid,
            status=self.status,
            error=self.error
        )



class MessageAccepted(MessageStatus):
    """ Accepted for processing

        The message contained no errors and was accepted, but not yet delivered.
        Not all providers report this status.
    """
    accepted = True


class MessageDelivered(MessageAccepted):
    """ Delivered successfully

        The message was accepted and finally delivered
    """
    delivered = True


class MessageExpired(MessageAccepted):
    """ Message has expired

        The message was accepted, has stayed idle for some time, and finally expired
    """
    delivered = False
    expired = True

class MessageError(MessageStatus):
    """ Late Error

        The message was accepted (as no exception was raised by the Gateway.send() method), but later failed
    """
    accepted = True
    delivered = False
    error = ''
