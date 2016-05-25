import pika
import time
import tornado.httpserver
import tornado.ioloop
import tornado.web

from pika.adapters.tornado_connection import TornadoConnection


class PikaClient(object):
    tornado_callback = None
    _closing = False
    _connect_index = 0
    _connect_pull = None

    def __init__(self, logger, queue_name, queue_read, queue_create):
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

        # TODO: read from config
        # self.credentials = pika.PlainCredentials('guest', 'guest')
        # self.host = 'localhost'
        # self.port = 5672
        # self.virtual_host = '/'

        # TODO: for demonstration purposes
        self.host = '127.0.0.1'
        main = pika.ConnectionParameters(host=self.host, port=5672)
        repl1 = pika.ConnectionParameters(host=self.host, port=5673)
        repl2 = pika.ConnectionParameters(host=self.host, port=5674)

        self._connect_pull = [main, repl1, repl2]

    def connect(self):
        if self.connecting:
            self.logger.warning('Already connecting to RabbitMQ')
            return
        param = self._connect_pull[self._connect_index]
        self.logger.debug('Connecting to RabbitMQ on '
                          '{host}:{port}'.format(host=param.host,
                                                 port=param.port))
        self.connecting = True
        try:
            self.connection = TornadoConnection(param,
                                                on_open_callback=self.on_connected)
            self.connection.add_on_close_callback(self.on_closed)
        except:
            self.reconnect()

    def on_connected(self, connection):
        self.logger.debug('Connected to RabbitMQ on '
                          '{host}'.format(host=self.host))
        self.connected = True
        self.connection = connection
        self.connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        self.logger.debug('Channel Open, Declaring Exchange')
        self.channel = channel
        self.channel.exchange_declare(exchange='tornado',
                                      type='topic',
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
        # self.logger.debug('Pending Messages')
        for properties, body in self.pending:
            self.logger.debug('Pending Message: %s | %s' % (properties, body))
            self.channel.basic_publish(exchange='tornado',
                                       # TODO: save routing_key or
                                       # it already in properties
                                       routing_key='reading',
                                       body=body,
                                       properties=properties)

    def on_pika_message(self, channel, method, header, body):
        self.logger.debug('Message receive: '
                          'body: {body}'.format(method=method,
                                                header=header,
                                                body=body))
        self.messages.append(body)
        if self.tornado_callback:
            self.tornado_callback(self.get_messages())

    def on_basic_cancel(self, frame):
        self.logger.debug('Basic Cancel Ok')
        self.connection.close()

    def on_closed(self, *args):
        self.logger.warning('kwargs:' + str(args))
        self.logger.warning('On closed. Try to reconnect...')
        self.reconnect()

    def reconnect(self):
        self.connecting = False
        self.connected = False
        self.logger.warning('Some waiting...')
        # some sleep for demonstration purposes
        # TODO: masg like 'Start reconnect after 3...2...1..'
        time.sleep(4)
        self.logger.warning('Start reconnect')
        if not self._closing:
            self._connect_index = (self._connect_index + 1) % len(self._connect_pull)
            self.logger.warning('Reconnect to %s' %
                self._connect_pull[self._connect_index])
            self.connect()
        else:
            self.logger.warning('Closing. Stop trying')

    def stop(self):
        self.logger.warning('STOP')
        self._closing = True
        tornado.ioloop.IOLoop.instance().stop()

    def sample_message(self, msg, routing_key, tornado_callback):
        self.logger.debug('Sample Message to %s' % routing_key)
        self.tornado_callback = tornado_callback
        properties = pika.BasicProperties(delivery_mode=1)
        self.channel.basic_publish(exchange='tornado',
                                   routing_key=routing_key,
                                   body=msg,
                                   properties=properties)

    def get_messages(self):
        output = self.messages
        self.messages = list()
        return output
