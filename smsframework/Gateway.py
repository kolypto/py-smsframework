from .IProvider import IProvider
from .lib.events import EventHook


class Gateway(object):
    """ SMS Gateway

        The primary object to send & receive messages.

        Sending Steps:

        1. Instantiate the gateway:

            from smsframework import Gateway
            gw = Gateway()

        1. Register providers with add_provider():

            from smsframework.providers import ClickatellProvider
            gw.add_provider('main', ClickatellProvider, ...)

        2. You already can send messages with send()!

            from smsframework import OutgoingMessage
            gw.send(OutgoingMessage('+123456789', 'hi there!'))

        3. Replace the router() function to get customized routing that depends on message fields:

            gw.router = lambda message: 'main'

        4. Use get_provider() to access provider-specific APIs:

            print gw.get_provider('main').get_balance()

        Receiving steps:

        1. Register providers
        2. Subscribe to onReceive and onStatus events:

            gw.onReceive += my_receive_handler
            gw.onStatus += my_status_handler

        3. Initialize message receiver URLs with ....
        4. Visit your provider's control panel and set up the receiver URLs
        5. Enjoy!
    """

    def __init__(self):
        #: Registered providers
        self._providers = {}

        # Events
        self.onSend = EventHook()
        self.onReceive = EventHook()
        self.onStatus = EventHook()



    #region Providers

    def add_provider(self, name, Provider, **config):
        """ Configure a provider

            :type name: str
            :param name: Provider name that will be used to uniquely identify it
            :type Provider: type
            :param Provider: Provider class
            :param config: Provider configuration. Please refer to the Provider documentation.
        """
        assert issubclass(Provider, IProvider), 'Provider does not implement IProvider'
        assert isinstance(name, str), 'Provider name must be a string'
        assert isinstance(config, dict), 'Provider config must be a dict or None'

        # Configure
        provider = Provider(self, name, **config)

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
