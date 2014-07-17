import json, urllib2
from functools import wraps

from smsframework import IProvider, exc
from .jsonex import JsonExEncoder, JsonExDecoder


#region JsonEx

from smsframework.data import *
from smsframework.data.OutgoingMessageOptions import OutgoingMessageOptions
from smsframework.exc import *

classes = {C.__name__: C for C in (
    IncomingMessage, OutgoingMessage,
    OutgoingMessageOptions,
    MessageStatus, MessageAccepted, MessageDelivered, MessageExpired, MessageError,
)}

exceptions = {E.__name__: E for E in (
    ProviderError, ConnectionError,
    MessageSendError, RequestError, UnsupportedError, ServerError, AuthError, LimitsError, CreditError
)}

try:
    from flask import make_response
    from werkzeug.exceptions import HTTPException
except ImportError: pass

def jsonex_dumps(data):
    """ Serialize with JsonEx
    :rtype: basestring
    """
    return json.dumps(data, cls=JsonExEncoder)


def jsonex_loads(s):
    """ Unserialize with JsonEx
    :rtype: dict
    """
    return json.loads(s, cls=JsonExDecoder, classes=classes, exceptions=exceptions)


def jsonex_api(f):
    """ View wrapper for JsonEx responses. Catches exceptions as well """
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Call, catch exceptions
        try:
            code, res = 200, f(*args, **kwargs)
        except HTTPException as e:
            code, res = e.code, {'error': e}
        except Exception as e:
            code, res = 500, {'error': e}

        # Response
        response = make_response(jsonex_dumps(res), code)
        return response
    return wrapper


def jsonex_request(url, data):
    """ Make a request with JsonEx
    :param url: URL
    :type url: str
    :param data: Data to POST
    :type data: dict
    :return: Response
    :rtype: dict
    """
    req = urllib2.Request(url, headers={'Content-type', 'application/json'})
    response = urllib2.urlopen(req, jsonex_dumps(data))
    res_str = response.read()
    return jsonex_loads(res_str)

#endregion


class ForwardClientProvider(IProvider):
    """ Forwarding client Provider

        - Sends messages through a remote ForwardServerProvider
        - Receives messages from a remote ForwardServerProvider
    """

    def __init__(self, gateway, name, server_url):
        """ Init the forwarding client
        :param server_url: Server URL.
            The URL should point to ForwardServerProvider registered on the server
        :type server_url: str
        """
        self.server_url = server_url
        super(ForwardClientProvider, self).__init__(gateway, name)

    def send(self, message):
        """ Send a message by forwarding it to the server
        :param message: Message
        :type message: smsframework.data.OutgoingMessage
        :rtype: smsframework.data.OutgoingMessage
        :raise Exception: any exception reported by the other side
        """
        res = jsonex_request(self.server_url, {'message': message})
        if res['error']:  # Exception object
            raise res['error']
        return res['message']  # OutgoingMessage object

    def make_receiver_blueprint(self):
        """ Create the receiver so server can send messages to us
        :rtype: flask.Blueprint
        """
        from .receiver_client import bp
        return bp


class ForwardServerProvider(IProvider):
    """ Forwarding server Provider

        Hooks into the gateway and:
        - Forwards all received messages and statuses to clients
        - Receives messages from clients and sends them through the gateway
    """
    def __init__(self, gateway, name, clients):
        """ Init server
        :param clients: List of client URLs to forward the messages to.
            The URL should point to ForwardClientProvider registered on the client
        :type clients: list[str]
        """
        self.clients = clients
        super(ForwardServerProvider, self).__init__(gateway, name)

        # Hook into the gateway
        self.gateway.onReceive += self.forward
        self.gateway.onStatus += self.forward

    def choose_clients(self, obj):
        """ Given a message, decides which clients will receive it.

        Override to have custom routing. Default: send to all clients

        :param obj: The object to be forwarded
        :type obj: smsframework.data.OutgoingMessage|smsframework.data.MessageStatus
        :return: List of client URLs to forward the message to
        :rtype: list[str]
        """
        return self.clients

    def _forward_object_to_client(self, client, obj):
        """ Forward an object to client
        :type client: str
        :type obj: smsframework.data.OutgoingMessage|smsframework.data.MessageStatus
        :rtype: smsframework.data.OutgoingMessage|smsframework.data.MessageStatus
        :raise Exception: any exception reported by the other side
        """
        assert isinstance(obj, (IncomingMessage, MessageStatus)), 'Tried to forward an object of an unsupported type: {}'.format(obj)

        # Forward
        url, name = ('/im', 'message') if isinstance(obj, IncomingMessage) else ('/status', 'status')
        res = jsonex_request(client + url, {name: obj})

        # Finish
        if 'error' in res:
            raise res['error']
        return res[name]

    def forward(self, obj):
        """ Forward an object to clients.

        :param obj: The object to be forwarded
        :type obj: smsframework.data.OutgoingMessage|smsframework.data.MessageStatus
        """
        clients = self.choose_clients(obj)

        # TODO: parallelize with threads!
        for client in clients:
            self._forward_object_to_client(client, obj)

    def send(self, message):
        """ Send a message by looping back to gateway so it sends with some other provider
        :param message: Message
        :type message: data.OutgoingMessage
        :rtype: data.OutgoingMessage
        """
        return self.gateway.send(message)

    def make_receiver_blueprint(self):
        """ Create the receiver: it gets messages from clients and actually sends them by looping to the own gateway
        :rtype: flask.Blueprint
        """
        from .receiver_server import bp
        return bp
