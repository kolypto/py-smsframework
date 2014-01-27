from .IProvider import IProvider
from .lib.events import EventHook


class Gateway(object):
    """ SMS Gateway

        The primary object to send & receive messages.

        Gateway sends messages through a set of configured providers
    """

    def __init__(self):
        #: Registered providers
        self._providers = {}

        # Events
        self.onSend = EventHook()
        self.onReceive = EventHook()
        self.onStatus = EventHook()



    #region Providers

    def add_provider(self, name, Provider, config=None):
        """ Configure a provider

            :type name: str
            :param name: Provider name that will be used to uniquely identify it
            :type Provider: type
            :param Provider: Provider class
        """
        assert issubclass(Provider, IProvider), 'Provider does not implement IProvider'
        assert isinstance(name, str), 'Provider name must be a string'
        if config is None: config = {}
        assert isinstance(config, dict), 'Provider config must be a dict or None'

        # Configure
        provider = Provider(self, name, config)

        # Register
        assert name not in self._providers, 'Provider is already registered'
        self._providers[name] = provider

        # If first - set default
        if self.default_provider is None:
            self.default_provider = name

    _default_provider = None

    @property
    def default_provider(self):
        """ Default provider name

            :rtype: str | None
        """
        return self._default_provider

    @default_provider.setter
    def default_provider(self, name):
        assert name in self._providers, 'Provider "{}" is not registered'.format(name)
        self._default_provider = name

    def get_provider(self, name):
        """ Get a provider by name

            You don't normally need this, unless the provider has some public API:
            refer to the provider documentation for the details.

            :type name: str
            :param name: Provider name
            :rtype: IProvider
            :raises KeyError: provider not found
        """
        return self._providers[name]

    #endregion



    #region Sending

    def router(self, message, *args):
        """ Router function that decides which provider to use for the given message for sending.

            Replace it with a function of your choice for custom routing.

            :type message: data.OutgoingMessage
            :param message: The message being sent
            :type args: Message routing values, as specified with the OutgoingMessage.route
            :rtype: str | None
            :returns: Provider name to use, or None to use the default one
        """
        # By default, this always uses the default provider
        return None

    def send(self, message):
        """ Send a message object

            :type message: data.OutgoingMessage
            :param message: The message to send
            :rtype: data.OutgoingMessage
            :returns: The sent message with populated fields
            :raises KeyError: unknown provider name
            :raises MessageSendError: generic errors
            :raises AuthError: authentication failed
            :raises LimitsError: sending limits exceeded
            :raises CreditError: not enough money on account
        """
        # Which provider to use?
        provider = self._default_provider  # default
        if message.provider is not None:
            provider = self.get_provider(message.provider)
        else:
            # Apply routing
            if message.routing_values is not None: # Use the default provider when no routing values are given
                # Routing values are present
                provider_name = self.router(*message.routing_values)
                if provider_name:
                    provider = self.get_provider(provider_name)

        # Set message provider name
        message.provider = provider.name

        # Send the message using the provider
        message = provider.send(message)

        # Emit the send event
        self.onSend(message)

        # Finish
        return message

    #region