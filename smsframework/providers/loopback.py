from .null import NullProvider
from ..lib import digits_only
from ..data import IncomingMessage, MessageAccepted, MessageDelivered


class LoopbackProvider(NullProvider):
    """ Loopback Provider

        Sends messages to registered subscriber callbacks.

        Configuration: none

        Sending: sends message to a registered subscriber (see: :meth:`LoopbackProvider.subscribe`),
            silently ignores other messages

        Receipt: simulation with a method

        Status: always reports success (if was requested for the message)
    """

    def __init__(self, gateway, name):
        super(LoopbackProvider, self).__init__(gateway, name)

        #: Virtual subscribers
        #: { Phone number : callable(message) }
        self._subscribers = {}

        #: Message traffic
        #: list<IncomingMessage|OutgoingMessage>
        self._traffic = []


    #region Public API

    def get_traffic(self):
        """ Fetch the accumulated messages and reset

            :rtype: list
            :returns: List of both IncomingMessage & OutgoingMessage objects
        """
        try:
            return self._traffic
        finally:
            self._traffic = []

    def received(self, src, body):
        """ Simulate an incoming message

            :type src: str
            :param src: Message source
            :type boby: str | unicode
            :param body: Message body
            :rtype: IncomingMessage
        """
        # Create the message
        self._msgid += 1
        message = IncomingMessage(src, body, self._msgid)

        # Log traffic
        self._traffic.append(message)

        # Handle it
        self._receive_message(message)

        # Finish
        return message

    def subscribe(self, number, callback):
        """ Register a virtual subscriber which receives messages to the matching number.

            :type number: str
            :param number: Subscriber phone number
            :type callback: callable
            :param callback: A callback(OutgoingMessage) which handles the messages directed to the subscriber.
                The message object is augmented with the .reply(str) method which allows to send a reply easily!
            :rtype: LoopbackProvider
        """
        self._subscribers[digits_only(number)] = callback
        return self

    #endregion


    def send(self, message):
        message = super(LoopbackProvider, self).send(message)

        # Log traffic
        self._traffic.append(message)

        # Deliver to the subscriber
        subscriber_found = message.dst in self._subscribers
        if subscriber_found:
            # Augment the message with .reply(str)
            def reply(body):
                if message.provider_options.allow_reply:
                    self.received(message.dst, body)
            message.reply = reply

            # Deliver
            self._subscribers[message.dst](message)

        # Delivery notification
        if message.provider_options.status_report:
            # Decide on the MessageStatus class to use
            StatusCls = MessageDelivered if subscriber_found else MessageAccepted

            # Handle status
            status = StatusCls(message.msgid)
            status.status = 'OK'
            self._receive_status(status)

        return message
