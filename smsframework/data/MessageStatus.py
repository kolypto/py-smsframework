from datetime import datetime

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

    #: Has an error occurred? See status then
    #: True | False
    error = False

    #: Status code from the provider, if any
    status_code = None

    #: Status text from the provider, if any
    status = None

    #: Provider-dependent info dict, if any
    meta = None

    def __init__(self, msgid, rtime=None, meta=None):
        """ Create the message status struct.

            Most fields are defined with direct property access, or by using subclasses

            :type msgid: str
            :param msgid: Unique message id
            :type rtime: datetime | None
            :param rtime: Status timestamp, naive, UTC
            :type meta: dict | None
            :param meta: Provider-dependent info
        """
        self.msgid = msgid
        self.rtime = rtime or datetime.utcnow()
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
    delivered = False
    expired = False


class MessageDelivered(MessageAccepted):
    """ Delivered successfully

        The message was accepted and finally delivered
    """
    accepted = True
    delivered = True
    expired = False


class MessageExpired(MessageAccepted):
    """ Message has expired

        The message was accepted, has stayed idle for some time, and finally expired
    """
    accepted = True
    delivered = False
    expired = True


class MessageError(MessageStatus):
    """ Late Error

        The message was accepted (as no exception was raised by the Gateway.send() method), but later failed
    """
    accepted = True
    delivered = False
    expired = False
    error = True
