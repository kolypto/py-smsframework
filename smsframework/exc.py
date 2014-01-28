class ProviderError(RuntimeError):
    """ Generic provider error """


class UnsupportedError(ProviderError):
    """ The requested operation is not supported """


class RequestError(ProviderError):
    """ Request error """


class ServerError(ProviderError):
    """ Server error: sevice unavailable, etc """


#region Sending errors


class MessageSendError(ProviderError):
    """ Base for sending errors """


class AuthError(ProviderError):
    """ Authentication error """


class LimitsError(ProviderError):
    """ Sending limits exceeded """


class CreditError(ProviderError):
    """ Not enough money on the account """


#endregion
