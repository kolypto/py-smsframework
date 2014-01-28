from .null import NullProvider


class LogProvider(NullProvider):
    """ Log Provider

        Logs the outgoing messages to a python logger provided as the config option.

        Configuration: target logger

        Sending: does nothing, increments message.msgid, prints the message to the log

        Receipt: Not implemented

        Status: Not implemented
    """

    def __init__(self, gateway, name, logger):
        """ Configure provider

            :type logger: logging.Logger
            :param logger: The logger to use
        """
        super(NullProvider, self).__init__(gateway, name)
        self.logger = logger

    def send(self, message):
        # Log
        self.logger.info('Sent SMS to {to}: {body}',
                         to=message.to,
                         body=message.body)

        # Finish
        return super(LogProvider, self).send(message)
