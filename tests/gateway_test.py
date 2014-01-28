import unittest

from smsframework import Gateway
from smsframework.providers import NullProvider, LoopbackProvider
from smsframework import OutgoingMessage, IncomingMessage, MessageStatus


class GatewatTest(unittest.TestCase):
    """ Test LoopbackProvider, and the whole smsframework by the way """

    def setUp(self):
        self.gw = Gateway()

        # Providers
        self.gw.add_provider('one', NullProvider)
        self.gw.add_provider('two', NullProvider)
        self.gw.add_provider('three', NullProvider)

        # Router
        def router(message, module, method):
            if module == 'main':
                return None  # use 'one' for module 'main'
            elif method == 'alarm':
                return 'two'  # use 'three' for all alerting methods
            else:
                return 'three'  # use 'two' for everything else
        self.gw.router = router

    def test_struct(self):
        """ Test structure """

        # Default provider is fine
        self.assertEqual(self.gw.default_provider, 'one')

        # Getting providers
        self.assertIsInstance(self.gw.get_provider('one'), NullProvider)
        self.assertIsInstance(self.gw.get_provider('two'), NullProvider)
        self.assertIsInstance(self.gw.get_provider('three'), NullProvider)
        self.assertRaises(KeyError, self.gw.get_provider, 'none')

        # Redeclare a provider
        self.assertRaises(AssertionError, self.gw.add_provider, 'one', NullProvider)

        # Pass a non-IProvider class
        self.assertRaises(AssertionError, self.gw.add_provider, 'ok', Exception)

    def test_routing(self):
        """ Test routing """

        # Sends through 'one'
        msg = self.gw.send(OutgoingMessage('', '').route('main', ''))
        self.assertEqual(msg.provider, 'one')

        # Sends through 'two'
        msg = self.gw.send(OutgoingMessage('', '').route('', 'alarm'))
        self.assertEqual(msg.provider, 'two')

        # Sends through 'three'
        msg = self.gw.send(OutgoingMessage('', '').route('', ''))
        self.assertEqual(msg.provider, 'three')

        # Send through 'one' (explicitly set)
        msg = self.gw.send(OutgoingMessage('', '', provider='one').route('', ''))
        self.assertEqual(msg.provider, 'one')

        # No routing specified: using the default route
        msg = self.gw.send(OutgoingMessage('', '', provider='one'))
        self.assertEqual(msg.provider, 'one')

        # Wrong provider specified
        self.assertRaises(AssertionError, self.gw.send, OutgoingMessage('', '', provider='zzz'))


    def test_events(self):
        """ Test events """

        # Counters
        self.recv = 0
        self.send = 0
        self.status = 0

        def inc_recv(message): self.recv += 1
        def inc_send(message): self.send += 1
        def inc_status(message): self.status += 1

        # Hooks
        self.gw.onReceive = inc_recv
        self.gw.onSend = inc_send
        self.gw.onStatus = inc_status

        # Emit some events
        provider = self.gw.get_provider('one')
        self.gw.send(OutgoingMessage('', ''))
        provider._receive_message(IncomingMessage(provider.name, '', ''))
        provider._receive_status(MessageStatus(provider.name, ''))

        # Check
        self.assertEqual(self.recv, 1)
        self.assertEqual(self.send, 1)
        self.assertEqual(self.status, 1)
