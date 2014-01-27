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
