from abc import abstractmethod


class IProvider(object):
    """ SmsFramework provider interface

        Implements methods to interact with the :class:`smsframework.Gateway`
    """

    def __init__(self, gateway, name, **config):
        """ Initialize the provider

            :type gateway: smsframework.Gateway
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

            :type message: smsframework.data.OutgoingMessage.OutgoingMessage
            :param message: The message to send
            :rtype: OutgoingMessage
            :returns: The sent message with populated fields
            :raises MessageSendError: generic errors
            :raises AuthError: authentication failed
            :raises LimitsError: sending limits exceeded
            :raises CreditError: not enough money on account
        """
        raise NotImplementedError('Provider.send not implemented')

    def receiver(self):
        """ Get a Blueprint for the HTTP receiver

            :rtype: flask.Blueprint
            :returns: configured Flask Blueprint receiver
            :raises NotImplementedError: Provider does not support message reception
        """
        raise NotImplementedError('Provider does not support message reception')



