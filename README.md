[![Build Status](https://travis-ci.org/kolypto/py-smsframework.png?branch=master)](https://travis-ci.org/kolypto/py-miracle)

SMSframework
============

SMS framework with pluggable providers.

Key features:

* Send messages
* Receive messages
* Delivery confirmations
* Handle multiple pluggable providers with a single gateway
* Synchronous message receipt through events
* Reliable message handling
* Supports provider APIs (like getting the balance)
* Providers use [Flask microframework](http://flask.pocoo.org) for message receivers
* 0 dependencies
* Unit-tested






Table of Contents
=================

* <a href="#supported-providers">Supported Providers</a>
* <a href="#gateway">Gateway</a>
    * <a href="#providers">Providers</a>
        * <a href="#gatewayadd_providername-provider-configiprovider">Gateway.add_provider(name, Provider, **config):IProvider</a>
        * <a href="#gatewaydefault_provider">Gateway.default_provider</a>
        * <a href="#gatewayget_providernameiprovider">Gateway.get_provider(name):IProvider</a>
    * <a href="#sending-messages">Sending Messages</a>
        * <a href="#gatewaysendmessageoutgoingmessage">Gateway.send(message):OutgoingMessage</a>
    * <a href="#event-hooks">Event Hooks</a>
        * <a href="#gatewayonsend">Gateway.onSend</a>
        * <a href="#gatewayonreceive">Gateway.onReceive</a>
        * <a href="#gatewayonstatus">Gateway.onStatus</a>
* <a href="#data-objects">Data Objects</a>
    * <a href="#incomingmessage">IncomingMessage</a>
    * <a href="#outgoingmessage">OutgoingMessage</a>
    * <a href="#messagestatus">MessageStatus</a>
    * <a href="#exceptions">Exceptions</a>
* <a href="#provider-http-receivers">Provider HTTP Receivers</a>
* <a href="#message-routing">Message Routing</a>
* <a href="#bundled-providers">Bundled Providers</a>
    * <a href="#nullprovider">NullProvider</a>
    * <a href="#logprovider">LogProvider</a>
    * <a href="#loopbackprovider">LoopbackProvider</a>
        * <a href="#loopbackproviderget_trafficlist">LoopbackProvider.get_traffic():list</a>
        * <a href="#loopbackproviderreceivedsrc-bodyincomingmessage">LoopbackProvider.received(src, body):IncomingMessage</a>
        * <a href="#loopbackprovidersubscribenumber-callbackiprovider">LoopbackProvider.subscribe(number, callback):IProvider</a> 






Supported Providers
===================

SMSframework supports the following bundled providers:

* [log](#logprovider): log provider for testing. Bundled.
* [null](#nullprovider): null provider for testing. Bundled.
* [loopback](#loopbackprovider): loopback provider for testing. Bundled.

Supported providers list:

* [Clickatell](https://npmjs.org/package/smsframework-clickatell)
* Expecting more!

Also see the [full list of providers](https://pypi.python.org/pypi?%3Aaction=search&term=smsframework).






Gateway
=======

SMSframework handles the whole messaging thing with a single *Gateway* object.

Let's start with initializing a gateway:

```python
from smsframework import Gateway

gateway = Gateway()
```

The `Gateway()` constructor currently has no arguments.



Providers
---------
A *Provider* is a package which implements the logic for a specific SMS provider.

Each provider reside in an individual package `smsframework_*`.
You'll probably want to install [some of these](#supported-providers) first.

### Gateway.add_provider(name, Provider, **config):IProvider
Register a provider on the gateway

Arguments:

* `provider: str` Provider name that will be used to uniquely identify it
* `Provider: type` Provider class that inherits from `smsframework.IProvider`
  You'll use this string in order to send messages via a specific provider.
* `**config` Provider configuration. Please refer to the Provider documentation.

```python
from smsframework.providers import NullProvider
from smsframework_clickatell import ClickatellProvider

gateway.add_provider('main', ClickatellProvider)  # the default ont
gateway.add_provider('null', NullProvider)
```

The first provider defined becomes the default one: used in case the routing function has no better idea.
See: [Message Routing](#message-routing).

### Gateway.default_provider
Property which contains the default provider name. You can change it to something else:

```python
gateway.default_provider = 'null'
```

### Gateway.get_provider(name):IProvider
Get a provider by name

You don't normally need this, unless the provider has some public API:
refer to the provider documentation for the details.



Sending Messages
----------------

### Gateway.send(message):OutgoingMessage
To send a message, you first create the [`OutgoingMessage`](#outgoingmessage) object
and then pass it as the first argument.

Arguments:

* `message: OutgoingMessage`: The messasge to send

Exceptions:

* `AssertionError`: wrong provider name encountered (returned by the router, or provided to OutgoingMessage)
* `MessageSendError`: Generic sending error
* `AuthError`: provider authentication failed
* `LimitsError`: sending limits exceeded
* `CreditError`: not enough money on the account

Returns: the same `OutgoingMessage`, with some additional fields populated: `msgid`, `meta`, ..

```python
from smsframework import OutgoingMessage

msg = gateway.send(OutgoingMessage('+123456789', 'hi there!'))
```

A message sending fail when the provider raises an exception. This typically occurs when the wrapped HTTP API
has returned an immediate error. Note that some errors occur later, and are typically reported with status messages:
see [`MessageStatus`](#messagestatus)



Event Hooks
-----------

The `Gateway` object has three events you can subscribe to.

The event is a simple object that implements the `+=` and `-=` operators which allow you to subscribe to the event
and unsubscribe respectively.

Event hook is a python callable which accepts arguments explained in the further sections.

Note that if you accidentally replace the hook with a callable (using the `=` operator instead of `+=`), you'll end
up having a single hook, but smsframework will continue to work normally: thanks to the implementation.

See [smsframework/lib/events.py](smsframework/lib/events.py).

### Gateway.onSend
Outgoing Message: a message that was successfully sent.

Arguments:

* `message: OutgoingMessage`: The message that was sent. See [OutgoingMessage](#outgoingmessage).

The message object is populated with the additional information from the provider, namely, the `msgid` and `meta` fields.

Note that if the hook raises an Exception, it will propagate to the place where `Gateway.send()` was called!

```python
def on_send(message):
    """ :type message: OutgoingMessage """
    print message

gw.onSend += on_send
```

### Gateway.onReceive
Incoming Message: a message that was received from the provider.

Arguments:

* `message: IncomingMessage`: The received message. See [IncomingMessage](#incomingmessage).

Note that if the hook raises an Exception, the Provider will report the error to the sms service.
Most services will retry the message delivery with increasing delays.

```python
def on_receive(message):
    """ :type message: IncomingMessage """
    print message

gw.onReceive += on_receive
```

### Gateway.onStatus
Message Status: a message status reported by the provider.

A status report is only delivered when explicitly requested with `OutgoingMessage.options(status_report=True)`.

Arguments:

* `status: MessageStatus`: The status info. See [MessageStatus](#messagestatus) and its subclasses.

Note that if the hook raises an Exception, the Provider will report the error to the sms service.
Most services will retry the status delivery with increasing delays.

```python
def on_status(status):
    """ :type status: MessageStatus """
    print status

gw.onStatys += status
```






Data Objects
============
SMSframework uses the following objects to represent message flows.

Note that internally all non-digit characters are removed from all phone numbers, both outgoing and incoming.
Phone numbers are typically provided in international formats, though some local providers may be less strict with this.

IncomingMessage
---------------
A messsage received from the provider.

Source: [smsframework/data/IncomingMessage.py](smsframework/data/IncomingMessage.py).

OutgoingMessage
--------------
A message being sent.

Source: [smsframework/data/OutgoingMessage.py](smsframework/data/OutgoingMessage.py).

MessageStatus
-------------
A status report received from the provider.

Source: [smsframework/data/MessageStatus.py](smsframework/data/MessageStatus.py).

Exceptions
----------

Source: [smsframework/exc.py](smsframework/exc.py).






Provider HTTP Receivers
=======================
TODO





Message Routing
===============
SMSframework requires you to explicitly specify the provider for each message:
otherwise, it uses the first defined provider by default.

In real world conditions with multiple providers, you may want a router function that decides on which provider to use
and which options to pick.

In order to achieve flexible message routing, we need to associate some metadata with each message, for instance:

* `module`: name of the sending module: e.g. "users"
* `type`: type of the message: e.g. "notification"

These 2 arbitrary strings need to be standardized in the application code, thus offering the possibility to define
complex routing rules.

When creating the message, use `OutgoingMessage.route()` function to specify these values:

```python
gateway.send(OutgoingMessage('+1234', 'hi').route('users', 'notification'))
```

Now, set a router function on the gateway:
a function which gets an outgoing message + some additional routing values, and decides on the provider to use:

```python
gateway.add_provider('primary', ClickatellProvider, ...)
gateway.add_provider('quick', ClickatellProvider, ...)
gateway.add_provider('usa', ClickatellProvider, ...)

def router(message, module, type):
    """ Custom router function """
    if message.dst.startswith('1'):
        return 'usa'  # Use 'usa' for all messages sent to the United States
    elif type == 'notification':
        return 'quick'  # use the 'quick' for all notifications
    else:
        return None  # Use the default provider ('primary') for everything else

    self.gw.router = router
```

Router function is also the right place to specify provider-specific options.






Bundled Providers
=================
The following providers are bundled with SMSframework and thus require no additional packages.

NullProvider
------------

Source: [smsframework/providers/null.py](smsframework/providers/null.py)

The `'null'` provider just ignores all outgoing messages.

Configuration: none

Sending: does nothing, but increments message.msgid

Receipt: Not implemented

Status: Not implemented

```python
from smsframework.providers import NullProvider

gw.add_provider('null', NullProvider)
```

LogProvider
-----------

Source: [smsframework/providers/log.py](smsframework/providers/log.py)

Logs the outgoing messages to a python logger provided as the config option.

Configuration:

* `logger: logging.Logger`: The logger to use

Sending: does nothing, increments message.msgid, prints the message to the log

Receipt: Not implemented

Status: Not implemented

Example:

```python
import logging
from smsframework.providers import LogProvider

gw.add_provider('log', LogProvider, logger=logging.getLogger(__name__))
```

LoopbackProvider
----------------

Source: [smsframework/providers/loopback.py](smsframework/providers/loopback.py)

The `'loopback'` provider is used as a dummy for testing purposes.

All messages are stored in the local log and can be retrieved as a list.

The provider even supports status & delivery notifications.

In addition, is supports virtual subscribers: callbacks bound to some phone numbers which are called when any
simulated message is sent to their phone number. Replies are also supported!

Configuration: none

Sending: sends message to a registered subscriber (see: :meth:`LoopbackProvider.subscribe`),
    silently ignores other messages.

Receipt: simulation with a method

Status: always reports success

### LoopbackProvider.get_traffic():list
LoopbackProvider stores all messages that go through it: both IncomingMessage and OutgoingMessage.

To get those messages, call `.get_traffic()`.
This method empties the message log and returns its previous state:

```python
from smsframework.providers import LoopbackProvider

gateway.add_provider('lo', LoopbackProvider);
gateway.send(OutgoingMessage('+123', 'hi'))

traffic = gateway.get_provider('lo').get_traffic()
print traffic[0].body  #-> 'hi'
```

### LoopbackProvider.received(src, body):IncomingMessage
Simulate an incoming message.

The message is reported to the Gateway as if it has been received from the sms service.

Arguments:

* `src: str`: Source number
* `body: str | unicode`: Message text

Returns: IncomingMessage

### LoopbackProvider.subscribe(number, callback):IProvider
Register a virtual subscriber which receives messages to the matching number.

Arguments:

* `number: str`: Subscriber phone number
* `callback: `: A `callback(OutgoingMessage)` which handles the messages directed to the subscriber.
    The message object is augmented with the `.reply(str)` method which allows to send a reply easily!

```python
def subscriber(message):
    print message  #-> OutgoingMessage('1', 'obey me')
    message.reply('got it')  # use the augmented reply method

provider = gateway.get_provider('lo')
provider.subscribe('+1', subscriber)  # register the subscriber

gateway.send('+1', 'obey me')
```
