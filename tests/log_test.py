import unittest
from testfixtures import LogCapture

from smsframework import Gateway
from smsframework.providers import LogProvider
from smsframework import OutgoingMessage


class LoopbackProviderTest(unittest.TestCase):
    """ Test LoopbackProvider """

    def setUp(self):
        self.gw = Gateway()
        # Providers
        self.gw.add_provider('main', LogProvider)

    def test_basic_send(self):
        with LogCapture() as l:
            msg = self.gw.send(OutgoingMessage('+1234', 'body'))
            l.check(
                ('smsframework.providers.log', 'INFO', 'Sent SMS to {}: {}'.format(msg.dst, msg.body)),
            )
