class OutgoingMessageOptions(object):
    """ Sending Options for :class:`OutgoingMessage` """

    #: Replies allowed?
    allow_reply = True

    #: Request a status report from the network?
    status_report = False

    #: Message validity period, minutes
    expires = None

    #: Sender ID to replace the number
    senderId = None

    #: Is a high-pri message? These are delivered faster and costier.
    escalate = False
