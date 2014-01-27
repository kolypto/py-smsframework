class MessageStatus(object):
    """ Sent Message Status

        Represent network's response to a sent message.
    """

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

    def __init__(self, provider, msgid, status=None, meta=None, error=None):
        """ Create the message status struct

            :type provider: str | None
            :param provider: Provider name that has reported the status
            :type msgid: str
            :param msgid: Unique message id
            :type status: str | None
            :param status: Status text
            :type meta: dict | None
            :param meta: Provider-dependent info
            :type error: str | None
            :param error: Error string, if any
        """
        self.provider = provider
        self.msgid = msgid
        self.status = status
        self.meta = meta


class MessageAccepted(MessageStatus):
    """ Accepted for processing """
    accepted = True


class MessageDelivered(MessageAccepted):
    """ Delivered successfully """
    delivered = True


class MessageExpired(MessageAccepted):
    """ Message has expired """
    delivered = False
    expired = True

class MessageError(MessageStatus):
    """ Error """
    accepted = True
    delivered = False
    error = ''
