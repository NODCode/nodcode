import pika
import time
import datetime
import tornado.httpserver
import tornado.ioloop
import tornado.web

from pika.adapters.tornado_connection import TornadoConnection
from pika.exceptions import AMQPConnectionError

class PikaClient(object):
    tornado_callback = None
    _closing = False
    _connect_index = 0
    _connect_pull = None
    _one_respond_made = None
    _waiting_to_reconnect = 3
    _expire_reconnect = 15
    _last_reconnect_fail = None

    def __init__(self, logger,
                 queue_name, queue_read, queue_create,
                 node_list):
        # Construct a queue name we'll use for this instance only
        self.queue_name = queue_name

        # Create queue for sending
        self.queue_read = queue_read
        self.queue_create = queue_create

        self.logger = logger
        self.connected = False
        self.connecting = False
        self.connection = None
        self.channel = None

        # A place for us to keep messages sent to us by Rabbitmq
        self.messages = list()
        # A place for us to put pending messages while we're waiting to connect
        self.pending = list()

        self._connect_pull = []
        for node in node_list:
            self._connect_pull.append(
                pika.ConnectionParameters(
                    host=node[0], port=int(node[1])))

    def connect(self):
        if self.connecting:
            self.logger.warning('Already connecting to RabbitMQ')
            return
        param = self._connect_pull[self._connect_index]
        self.logger.debug('Connecting to RabbitMQ on '
                          '{host}:{port}'.format(host=param.host,
                                                 port=param.port))
        self.connecting = True
        # TODO: add on_connection_error
        try:
            self.connection = TornadoConnection(
                param,
                on_open_callback=self.on_connected
            )
            self.connection.add_on_close_callback(self.on_closed)
        except AMQPConnectionError:
            self.reconnect()

    def on_connected(self, connection):
        self.logger.debug('Connected to RabbitMQ on: '
                          '{connection}'.format(connection=connection))
        self.connected = True
        self.connection = connection
        self.connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        self.logger.debug('Channel Open, Declaring Exchange')
        self.channel = channel
        self.channel.exchange_declare(exchange='tornado',
                                      type='direct',
                                      durable=True,
                                      callback=self.on_exchange_declared)

    def on_exchange_declared(self, frame):
        self.logger.debug('Exchange Declared, Declaring Queue')
        self.channel.queue_declare(queue=self.queue_name,
                                   durable=True,
                                   callback=self.on_queue_declared)
        self.channel.queue_declare(queue=self.queue_create,
                                   durable=True,
                                   callback=lambda frame:
                                       self.channel.queue_bind(
                                           exchange='tornado',
                                           queue=self.queue_create,
                                           routing_key=self.queue_create,
                                           callback=None))
        self.channel.queue_declare(queue=self.queue_read,
                                   durable=True,
                                   callback=lambda frame:
                                       self.channel.queue_bind(
                                           exchange='tornado',
                                           queue=self.queue_read,
                                           routing_key=self.queue_read,
                                           callback=None))

    def on_queue_declared(self, frame):
        self.logger.debug('Queue Declared, Binding Queue')
        self.channel.queue_bind(exchange='tornado',
                                queue=self.queue_name,
                                routing_key='answer',
                                callback=self.on_queue_bound)

    def on_queue_bound(self, frame):
        self.logger.debug('Queue Bound, Issuing Basic Consume')
        self.channel.basic_consume(consumer_callback=self.on_pika_message,
                                   queue=self.queue_name,
                                   no_ack=True)

        # TODO: still not implemented
        # for properties, body in self.pending:
        #     self.logger.debug('Pending Message:'
        #                       ' %s | %s' % (properties, body))
        #     self.channel.basic_publish(exchange='tornado',
        #                                # TODO: save routing_key or
        #                                # it already in properties
        #                                routing_key='reading',
        #                                body=body,
        #                                properties=properties)

    def on_pika_message(self, channel, method, header, body):
        self.logger.debug('Message receive: '
                          'body: {body}'.format(method=method,
                                                header=header,
                                                body=body))
        self.messages.append(body)
        if self.tornado_callback and not self._one_respond_made:
            self.tornado_callback(self.get_messages())
            self._one_respond_made = True

    def on_basic_cancel(self, frame):
        self.logger.debug('Basic Cancel Ok')
        self.connection.close()

    def on_closed(self, *args):
        self.logger.warning('On closed. Try to reconnect...')
        self.reconnect()

    def reconnect(self):
        self.logger.warning('Fail to connect')
        if self._last_reconnect_fail:
            current_fail_time = datetime.datetime.now()
            fail_timedelta = current_fail_time - self._last_reconnect_fail
            self.logger.debug('Check reconnect expires, '
                              'timedelta: %s seconds' % fail_timedelta.seconds)
            if fail_timedelta.seconds >= self._expire_reconnect:
                self._closing = False
                self._connect_index = 0
                self._last_reconnect_fail = datetime.datetime.now()
                self.logger.debug('Reconnect time is expired, '
                                  'reset reconnect parameters')
        else:
            self.logger.warning('Set first fail reconnect time')
            self._last_reconnect_fail = datetime.datetime.now()

        self.connecting = False
        self.connected = False
        self.logger.warning('%s sec waiting...' % self._waiting_to_reconnect)
        time.sleep(self._waiting_to_reconnect)
        if not self._closing:
            self._connect_index += 1
            self.logger.warning('Try to reconnect to %s, try number %s' %
                                (self._connect_pull[self._connect_index],
                                 self._connect_index))
            if self._connect_index == len(self._connect_pull) - 1:
                self._closing = True
            self.connect()
        else:
            self.logger.warning('Closing. Stop trying')
            self.stop()

    def stop(self):
        self.logger.warning('STOP')
        self._closing = True
        tornado.ioloop.IOLoop.instance().stop()

    def sample_message(self, msg, routing_key, tornado_callback):
        self.logger.debug('Sample Message to %s' % routing_key)
        self.tornado_callback = tornado_callback
        properties = pika.BasicProperties(delivery_mode=1)

        self._one_respond_made = False
        self.channel.basic_publish(exchange='tornado',
                                   routing_key=routing_key,
                                   body=msg,
                                   properties=properties)

    def get_messages(self):
        output = self.messages
        self.messages = list()
        return output
