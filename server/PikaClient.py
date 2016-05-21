import pika
import tornado
from pika.adapters.tornado_connection import TornadoConnection

from Logger import Logger


class PikaClient(object):

    def __init__(self):
        self.connecting = False
        self.connection = None
        self.channel = None
        self.logger = Logger('pika client').get()

    def connect(self):
        if self.connecting:
            self.logger.warning('Already connecting to RabbitMQ.')
            return
        self.logger.info("Connecting to RabbitMQ")
        self.connecting = True
        params = pika.ConnectionParameters(host='localhost')
        self.connection = TornadoConnection(params,
                                            on_open_callback=self.on_connect)
        self.connection.add_on_close_callback(self.on_closed)

    def on_connect(self, connection):
        self.connection = connection
        connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        self.logger.info('Channel Open')
        self.channel = channel

    def on_exchange_declare(self, frame):
        self.logger.info("Exchange declared.")

    def on_basic_cancel(self, frame):
        self.logger.info('Basic Cancel Ok.')
        self.connection.close()

    def on_closed(self, connection):
        tornado.ioloop.IOLoop.instance().stop()
