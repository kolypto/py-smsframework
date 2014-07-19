import httplib
import unittest
import threading
import time
from datetime import datetime

from flask import Flask
from werkzeug.serving import run_simple

from smsframework import Gateway, exc
from smsframework.providers import ForwardClientProvider, ForwardServerProvider, LoopbackProvider
from smsframework import OutgoingMessage, IncomingMessage

from smsframework.providers.forward.provider import jsonex_request


class ForwardProviderTest(unittest.TestCase):
    """ Test ForwardClientProvider and ForwardServerProvider """

    def _runFlask(self, gw, port):
        """
        :param gw: Gateway
        :type gw: smsframework.Gateway.Gateway
        :return:
        :rtype:
        """
        # Init flask
        app = Flask(__name__)
        app.debug = True
        app.testing = True

        # Register gateway receivers
        gw.receiver_blueprints_register(app, prefix='/sms')

        # Kill
        @app.route('/kill', methods=['POST'])
        def kill():
            raise KeyboardInterrupt('/kill')

        # Run
        run_simple('0.0.0.0', port, app, passthrough_errors=True)

    def setUp(self):
        self.lock = threading.Lock()

        # Init: client gateway
        self.gw_client = Gateway()
        self.gw_client.add_provider('fwd', ForwardClientProvider, server_url='http://a:b@localhost:5001/sms/fwd')

        # Init: server gateway
        self.gw_server = Gateway()
        self.gw_server.add_provider('lo', LoopbackProvider)
        self.gw_server.add_provider('fwd', ForwardServerProvider, clients=['http://a:b@localhost:5000/sms/fwd'])
        self.lo = self.gw_server.get_provider('lo')
        ' :type: LoopbackProvider '

        # Run client in a thread
        self.t_client = threading.Thread(target=self._runFlask, args=(self.gw_client, 5000))
        self.t_client.daemon = True
        self.t_client.start()

        # Run server in a thread
        self.t_server = threading.Thread(target=self._runFlask, args=(self.gw_server, 5001))
        self.t_server.daemon = True
        self.t_server.start()

        # Give Flask some time to initialize
        time.sleep(0.5)

    def tearDown(self):
        # Kill threads
        for port, thread in ((5000, self.t_client), (5001, self.t_server)):
            try: jsonex_request('http://localhost:{}/kill'.format(port), {})
            except httplib.BadStatusLine: pass
            thread.join()

    def testSend(self):
        """ Send messages """

        # Send a message
        om = OutgoingMessage('+1234', 'Hi man!').options(senderId='me').params(a=1).route(1, 2, 3)
        rom = self.gw_client.send(om)

        # Check traffic
        traffic = self.lo.get_traffic()
        self.assertEqual(len(traffic), 1)
        tom = traffic.pop()

        for m in (om, rom, tom):
            self.assertEqual(m.src, None)
            self.assertEqual(m.dst, '1234')
            self.assertEqual(m.body, 'Hi man!')
            self.assertEqual(m.provider, 'lo')  # Remote provider should be exposed
            self.assertEqual(m.provider_options.senderId, 'me')
            self.assertEqual(m.provider_params, {'a': 1})
            self.assertEqual(m.routing_values, [1, 2, 3])
            self.assertEqual(m.msgid, '1')
            self.assertEqual(m.meta, None)

    def testReceive(self):
        """ Receive messages """
        # Message receiver
        received = []
        def onReceive(message): received.append(message)
        self.gw_client.onReceive += onReceive

        # Receive a message
        self.lo.received('1111', 'Yo')

        # Check
        self.assertEqual(len(received), 1)
        msg = received.pop()
        ':type: IncomingMessage'

        self.assertEqual(msg.msgid, 1)
        self.assertEqual(msg.src, '1111')
        self.assertEqual(msg.body, 'Yo')
        self.assertEqual(msg.dst, None)
        self.assertIsInstance(msg.rtime, datetime)
        self.assertEqual(msg.meta, {})
        self.assertEqual(msg.provider, 'lo')  # Remote provider should be exposed

    def testStatus(self):
        """ Receive statuses """
        # Status receiver
        statuses = []
        def onStatus(status): statuses.append(status)
        self.gw_client.onStatus += onStatus

        # Subscriber
        incoming = []
        def subscriber(message): incoming.append(message)
        self.lo.subscribe('1234', subscriber)

        # Send a message, request status report
        om = OutgoingMessage('+1234', 'Hi man!').options(status_report=True)
        rom = self.gw_client.send(om)

        # Check
        self.assertEqual(len(statuses), 1)
        status = statuses.pop()
        ':type: MessageStatus'
        self.assertEqual(status.msgid, '1')
        self.assertIsInstance(status.rtime, datetime)
        self.assertEqual(status.provider, 'lo')
        self.assertEqual(status.accepted, True)
        self.assertEqual(status.delivered, True)
        self.assertEqual(status.expired, False)
        self.assertEqual(status.error, False)
        self.assertEqual(status.status_code, None)
        self.assertEqual(status.status, 'OK')
        self.assertEqual(status.meta, {})

    def testServerError(self):
        """ Test how errors are transferred from the server """

        # Erroneous subscribers
        def tired_subscriber(message):
            raise OverflowError('Tired')
        self.lo.subscribe('1234', tired_subscriber)

        def offline_subscriber(message):
            raise exc.ServerError('Offline')
        self.lo.subscribe('5678', offline_subscriber)

        # Send: 1
        om = OutgoingMessage('+1234', 'Hi man!')
        self.assertRaises(RuntimeError, self.gw_client.send, om)  # Unknown error classes are converted to RuntimeError

        # Send: 2
        om = OutgoingMessage('+5678', 'Hi man!')
        self.assertRaises(exc.ServerError, self.gw_client.send, om)  # Known errors: as is

    def testClientError(self):
        """ Test how server behaves when the client cannot receive """

        # Message receiver
        def failing_receiver(message):
            raise OverflowError(':(')
        self.gw_client.onReceive += failing_receiver

        # Receive a message
        self.assertRaises(RuntimeError, self.lo.received, '1111', 'Yo')
