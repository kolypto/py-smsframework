import unittest

from smsframework import Gateway
from smsframework.providers import LoopbackProvider
from smsframework import OutgoingMessage, IncomingMessage, MessageAccepted, MessageDelivered


class GatewatTest(unittest.TestCase):
    """ Test LoopbackProvider """

    def setUp(self):
        gw = self.gw = Gateway()

        # Providers
        self.gw.add_provider('main', LoopbackProvider)
        provider = self.provider = gw.get_provider('main')
        ' :type: LoopbackProvider '

        # Add subscribers
        self.subscriber_log = []

        def subscriber(name, replies=False):
            def callback(message):
                self.subscriber_log.append('{name}:{src}:{body}'.format(name=name, src=message.src, body=message.body))
                if replies:
                    message.reply('hello')
            return callback

        provider.subscribe('+1', subscriber('1'))
        provider.subscribe('+2', subscriber('2'))
        provider.subscribe('+3', subscriber('3', replies=True))

        # Event handlers
        self.events_log = []

        def out_msg(message):
            self.events_log.append(message)

        def in_msg(message):
            self.events_log.append(message)

        def in_status(status):
            self.events_log.append(status)

        gw.onSend += out_msg
        gw.onReceive += in_msg
        gw.onStatus += in_status

    def test_missing_number(self):
        """ Send to a missing number """
        msg = self.gw.send(OutgoingMessage('+0', 'you there?'))

        self.assertListEqual(self.provider.get_traffic(), [msg])  # traffic works
        self.assertListEqual(self.events_log, [msg])
        self.assertEqual(self.subscriber_log, [])  # no log as there was no subscriber


    def test_missing_number_status(self):
        """ Send to a missing number with status report request """
        msg = self.gw.send(OutgoingMessage('+0', 'you there?').options(status_report=True))

        self.assertListEqual(self.provider.get_traffic(), [msg])  # traffic works
        self.assertEqual(len(self.events_log), 2)
        self.assertIsInstance(self.events_log[0], MessageAccepted)  # accepted, but not delivered
        self.assertSetEqual(self.events_log[0].states, {'accepted'})
        self.assertIs(self.events_log[1], msg)
        self.assertEqual(self.subscriber_log, [])  # no log as there was no subscriber

    def test_subscriber1(self):
        """ Test delivering a message to a subscriber """
        msg = self.gw.send(OutgoingMessage('+1', 'hi!').options(status_report=True))

        self.assertListEqual(self.provider.get_traffic(), [msg])
        self.assertEqual(len(self.events_log), 2)
        self.assertIsInstance(self.events_log[0], MessageDelivered)  # delivered
        self.assertSetEqual(self.events_log[0].states, {'accepted', 'delivered'})
        self.assertIs(self.events_log[1], msg)
        self.assertEqual(self.subscriber_log, ['1:None:hi!'])

    def test_subscriber3(self):
        """ Test replying subscriber """
        msg = self.gw.send(OutgoingMessage('++3', 'hi!').options())

        traffic = self.provider.get_traffic()
        self.assertIs(traffic[0], msg)
        self.assertIsInstance(traffic[1], IncomingMessage)
        self.assertEqual(traffic[1].src, '3')
        self.assertEqual(traffic[1].dst, None)
        self.assertEqual(traffic[1].body, 'hello')

        self.assertEqual(len(self.events_log), 2)
        self.assertIs(self.events_log[1], msg)  # onSend is only emitted once the Provider has finished
        self.assertEqual(self.events_log[0].body, 'hello')  # the reply
        self.assertEqual(self.subscriber_log, ['3:None:hi!'])

    def test_subscriber3_noreply(self):
        """ Test replying subscriber with disabled replies """
        msg = self.gw.send(OutgoingMessage('3', 'hi!').options(status_report=True, allow_reply=False))

        self.assertListEqual(self.provider.get_traffic(), [msg])
        self.assertEqual(len(self.events_log), 2)
        self.assertIsInstance(self.events_log[0], MessageDelivered)  # delivered
        self.assertIs(self.events_log[1], msg)
        self.assertEqual(self.subscriber_log, ['3:None:hi!'])
