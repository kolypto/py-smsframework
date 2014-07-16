from smsframework import IProvider, exc


class ForwardClientProvider(IProvider):
    def __init__(self, gateway, name, server_url):
        """ Init the forwarding client
        :param server_url: URL to forwarding receiver installed on the server
        :type server_url: str
        """
        self.server_url = server_url
        super(ForwardClientProvider, self).__init__(gateway, name)

    def send(self, message):
        """ Send a message by forwarding it to the server
        :param message: Message
        :type message: smsframework.data.OutgoingMessage
        :rtype: smsframework.data.OutgoingMessage
        """
        # Serialize it

        # Send it

        # Unserialize it

        # Finish


    def make_receiver_blueprint(self):
        """ Create the receiver so server can send messages to us
        :rtype: flask.Blueprint
        """


class ForwardServerProvider(IProvider):
    def __init__(self, gateway, name, client_chooser=None):
        self.client_chooser = client_chooser
        super(ForwardClientProvider, self).__init__(gateway, name)


    def send(self, message):
        """ Send a message: pass it to a client, chosen by self.client_chooser
        :param message: Message
        :type message: data.OutgoingMessage
        :rtype: data.OutgoingMessage
        """

    def make_receiver_blueprint(self):
        """ Create the receiver: it gets messages from clients and actually sends them by looping to the own gateway
        :rtype: flask.Blueprint
        """
