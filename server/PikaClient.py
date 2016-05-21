import pika
import tornado
from pika.adapters.tornado_connection import TornadoConnection

# TODO: logging instead print()


class PikaClient(object):

    def __init__(self):
        self.connecting = False
        self.connection = None
        self.channel = None

    def connect(self):
        if self.connecting:
            print('Already connecting to RabbitMQ.')
            return
        print("Connecting to RabbitMQ")
        self.connecting = True
        params = pika.ConnectionParameters(host='localhost')
        self.connection = TornadoConnection(params,
                                            on_open_callback=self.on_connect)
        self.connection.add_on_close_callback(self.on_closed)

    def on_connect(self, connection):
        self.connection = connection
        connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        print('Channel Open')
        self.channel = channel

    def on_exchange_declare(self, frame):
        print("Exchange declared.")

    def on_basic_cancel(self, frame):
        print('Basic Cancel Ok.')
        self.connection.close()

    def on_closed(self, connection):
        tornado.ioloop.IOLoop.instance().stop()
