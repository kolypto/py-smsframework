from abc import abstractmethod


class IProvider(object):
    """ SmsFramework provider interface

        Implements methods to interact with the :class:`smsframework.Gateway`
    """

    def __init__(self, gateway, name, **config):
        """ Initialize the provider

            :type gateway: Gateway
            :param gateway: Parent Gateway
            :type name: str
            :param name: Provider name. Used to uniquely identify the provider
            :param config: Provider-dependent configuration
        """
        self.gateway = gateway
        self.name = name

    def send(self, message):
        """ Send a message

            Providers are required to:
            * Populate `message.msgid` and `message.meta` on completion
            * Expect that `message.src` can be empty
            * Support both ASCII and Unicode messages
            * Use `message.params` for provider-dependent configuration
            * Raise exceptions from `exc.py` for errors

            :type message: data.OutgoingMessage
            :param message: The message to send
            :rtype: OutgoingMessage
            :returns: The sent message with populated fields
            :raises MessageSendError: sending errors
        """
        raise NotImplementedError('Provider.send not implemented')

    def make_receiver_blueprint(self):
        """ Get a Blueprint for the HTTP receiver

            :rtype: flask.Blueprint
            :returns: configured Flask Blueprint receiver
            :raises NotImplementedError: Provider does not support message reception
        """
        raise NotImplementedError('Provider does not support message reception')


    #region Receiver callbacks

    def _receive_message(self, message):
        """ Incoming message callback

            Calls Gateway.onReceive event hook

            Providers are required to:
            * Cast phone numbers to digits-only
            * Support both ASCII and Unicode messages
            * Populate `message.msgid` and `message.meta` fields
            * If this method fails with an exception, the provider is required to respond with an error to the service

            :type message: IncomingMessage
            :param message: The received message
            :rtype: IncomingMessage
        """
        # Populate fields
        message.provider = self.name

        # Fire the event hook
        self.gateway.onReceive(message)

        # Finish
        return message

    def _receive_status(self, status):
        """ Incoming status callback

            Calls Gateway.onStatus event hook

            Providers are required to:
            * Cast phone numbers to digits-only
            * Use proper MessageStatus subclasses
            * Populate `status.msgid` and `status.meta` fields
            * If this method fails with an exception, the provider is required to respond with an error to the service

            :type status: MessageStatus
            :param status: The received status
            :rtype: MessageStatus
        """
        # Populate fields
        status.provider = self.name

        # Fire the event hook
        self.gateway.onStatus(status)

        # Finish
        return status

    #endregion
