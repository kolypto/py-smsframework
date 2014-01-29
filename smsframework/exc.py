class ProviderError(RuntimeError):
    """ Generic provider error """


class ConnectionError(ProviderError):
    """ Connection failed """


#region Sending errors

class MessageSendError(ProviderError):
    """ Base for erorrs reported by the provider """


class RequestError(MessageSendError):
    """ Request error: likely, validation errors """


class UnsupportedError(MessageSendError):
    """ The requested operation is not supported """


class ServerError(MessageSendError):
    """ Server error: sevice unavailable, etc """


class AuthError(MessageSendError):
    """ Authentication error """


class LimitsError(MessageSendError):
    """ Sending limits exceeded """


class CreditError(MessageSendError):
    """ Not enough money on the account """


#endregion
