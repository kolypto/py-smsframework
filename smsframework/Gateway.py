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
        """ Register a provider on the gateway

            The first provider defined becomes the default one: used in case the routing function has no better idea.

            :type name: str
            :param name: Provider name that will be used to uniquely identify it
            :type Provider: type
            :param Provider: Provider class that inherits from `smsframework.IProvider`
            :param config: Provider configuration. Please refer to the Provider documentation.
            :rtype: IProvider
            :returns: The created provider
        """
        assert issubclass(Provider, IProvider), 'Provider does not implement IProvider'
        assert isinstance(name, str), 'Provider name must be a string'

        # Configure
        provider = Provider(self, name, **config)

        # Register
        assert name not in self._providers, 'Provider is already registered'
        self._providers[name] = provider

        # If first - set default
        if self.default_provider is None:
            self.default_provider = name

        # Finish
        return provider

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
            :raises AssertionError: wrong provider name encountered (returned by the router, or provided to OutgoingMessage)
            :raises MessageSendError: generic errors
            :raises AuthError: provider authentication failed
            :raises LimitsError: sending limits exceeded
            :raises CreditError: not enough money on the account
        """
        # Which provider to use?
        provider_name = self._default_provider  # default
        if message.provider is not None:
            assert message.provider in self._providers, \
                'Unknown provider specified in OutgoingMessage.provideer: {}'.format(provider_name)
            provider = self.get_provider(message.provider)
        else:
            # Apply routing
            if message.routing_values is not None: # Use the default provider when no routing values are given
                # Routing values are present
                provider_name = self.router(message, *message.routing_values) or self._default_provider
                assert provider_name in self._providers, \
                    'Routing function returned an unknown provider name: {}'.format(provider_name)
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


    #region Receipt

    def receiver_blueprint_for(self, name):
        """ Get a Flask blueprint for the named provider that handles incoming messages & status reports

            Note: this requires Flask microframework.

            :rtype: flask.blueprints.Blueprint
            :returns: Flask Blueprint, fully functional
            :raises KeyError: provider not found
            :raises NotImplementedError: Provider does not implement a receiver
        """
        # Get the provider & blueprint
        provider = self.get_provider(name)
        bp = provider.make_receiver_blueprint()

        # Register a Flask handler that initializes `g.provider`
        # This is the only way for the blueprint to get the current IProvider instance
        from flask.globals import g  # local import as the user is not required to use receivers at all

        @bp.before_request
        def init_g():
            g.provider = provider

        # Finish
        return bp

    def receiver_blueprints(self):
        """ Get Flask blueprints for every provider that supports it

            Note: this requires Flask microframework.

            :rtype: dict
            :returns: A dict { provider-name: Blueprint }
        """
        blueprints = {}
        for name in self._providers:
            try:
                blueprints[name] = self.receiver_blueprint_for(name)
            except NotImplementedError:
                pass  # Ignore providers that does not support receivers
        return blueprints

    def receiver_blueprints_register(self, app, prefix='/'):
        """ Register all provider receivers on the provided Flask application under '/{prefix}/provider-name'

            Note: this requires Flask microframework.

            :type app: flask.Flask
            :param app: Flask app to register the blueprints on
            :type prefix: str
            :param prefix: URL prefix to hide the receivers under.
                You likely want some random stuff here so no stranger can simulate incoming messages.
            :rtype: flask.Flask
        """
        # Register
        for name, bp in self.receiver_blueprints().items():
            app.register_blueprint(
                bp,
                url_prefix='{prefix}{name}'.format(
                    prefix='/'+prefix.strip('/')+'/' if prefix else '/',
                    name=name
                )
            )

        # Finish
        return app

    #endregion
