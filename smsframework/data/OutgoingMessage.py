from .OutgoingMessageOptions import OutgoingMessageOptions


class OutgoingMessage(object):
    """ Outgoing Message: Mobile Terminated (MT)

        Represents a message that's being sent or was sent to the provider
    """

    #: Routing values
    routing_values = None

    #: Unique message id, populated by the provider on send
    msgid = None

    #: Provider-dependent message info dict, populated by the provider on send
    meta = None

    def __init__(self, dst, body, src=None, provider=None):
        """ Create a message for sending

            :type dst: str | None
            :param dst: Destination phone number, digits only
            :type body: str | unicode
            :param body: Message

            :type src: str | None
            :param src: Source phone number, digits only
            :type provider: str | None
            :param provider: Provider name to use for sending.
                If not specified explicitly, the message will be routed using the routing values:
                see :meth:`OutgoingMessage.route`
        """
        self.src = src
        self.dst = dst
        self.body = body

        self.provider = provider

        #: Sending options for the Gateway
        self.provider_options = OutgoingMessageOptions()

        #: Provider-dependent sending parameters
        self.provider_params = {}

    def options(self, **kwargs):
        """ Specify sending options for the Gateway.

            See: :class:`OutgoingMessageOptions`

            :param allow_reply: Replies allowed?
            :param status_report: Request a status report from the network?
            :param expires: Message validity period, minutes
            :param senderId: Sender ID to replace the number
            :param escalate: Is a high-pri message? These are delivered faster and costier.

            :rtype: OutgoingMessage
        """
        self.provider_options.__dict__.update(kwargs)
        return self

    def params(self, **params):
        """ Specify provider-specific sending parameters

            :rtype: OutgoingMessage
        """
        self.provider_params = params
        return self

    def route(self, *args):
        """ Specify arbitrary routing values.

            These are used by the Gateway's routing function to decide on which provider to use for the message
            (if no provider was explicitly specified),

            If no routing values are provided at all - the default route is used.

            :rtype: OutgoingMessage
        """
        self.routing_values = args
        return self
