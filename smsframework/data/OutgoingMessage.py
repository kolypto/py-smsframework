class OutgoingMessage(object):
    """ Outgoing Message: Mobile Terminated (MT)

        Represents a message that's being sent or was sent to the provider
    """

    #: Unique message id, populated by the provider on send
    msgid = None

    #: Provider-dependent message info dict, populated by the provider on send
    meta = None

    def __init__(self, dst, body, src=None, provider=None, route=None):
        """ Create a message for sending

            :type dst: str | None
            :param dst: Destination phone number, digits only
            :type body: str | unicode
            :param body: Message

            :type src: str | None
            :param src: Source phone number, digits only
            :type provider: str | None
            :param provider: Provider name to use for sending.
                If not specified explicitly, the message will be routed by the :class:`smsframework.Gateway`,
                which by default selects the first available provider.
            :type route: list | tuple | None
            :param route: Routing values for the message: are used by the routing method
        """
        self.src = src
        self.dst = dst
        self.body = body

        self.provider = provider
        self.route = route

        #: Sending options for the Gateway
        self.options = OutgoingMessageOptions()

        #: Provider-dependent sending parameters
        self.params = {}

    def options(self, **kwargs):
        """ Specify sending options for the Gateway

            :param allow_reply: Replies allowed?
            :param status_report: Request a status report from the network?
            :param expires: Message validity period, minutes
            :param senderId: Sender ID to replace the number
            :param escalate: Is a high-pri message? These are delivered faster and costier.
        """
        self.options.__dict__.update(kwargs)
        return self


class OutgoingMessageOptions(object):
    """ Sending Options for :class:`OutgoingMessage` """

    #: Replies allowed?
    allow_reply = False

    #: Request a status report from the network?
    status_report = False

    #: Message validity period, minutes
    expires = None

    #: Sender ID to replace the number
    senderId = None

    #: Is a high-pri message? These are delivered faster and costier.
    escalate = False
