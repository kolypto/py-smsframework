from datetime import datetime


class IncomingMessage(object):
    """ Incoming Message: Mobile Originated (MO)

        Represents a message received from the provider
        """

    def __init__(self, provider, src, body, msgid=None, dst=None, rtime=None, meta=None):
        """ Create the received message struct

            :type provider: str
            :param provider: Provider name
            :type src: str
            :param src: Source number (sender)
            :type body: str | unicode
            :param body: Message contents
            :type msgid: str | None
            :param msgid: Message ID from the provider
            :type dst: str | None
            :param dst: Destination number (receiver)
            :type rtime: datetime
            :param rtime: Received time, naive, UTC
            :type meta: dict | None
            :param meta: Provider-dependent message info
        """
        self.provider = provider
        self.msgid = msgid
        self.src = src
        self.body = body
        self.dst = dst
        self.rtime = rtime or datetime.utcnow()
        self.meta = meta or {}

    def __repr__(self):
        return '{cls}({provider!r}, {src!r}, {body!r}, msgid={msgid!r})'.format(
            cls=self.__class__.__name__,
            provider=self.provider,
            src=self.src,
            body=self.body,
            msgid=self.msgid
        )
