#!/usr/bin/env python

import os
import sys
import json
import time
import uuid
import ConfigParser

import tornado.ioloop
import tornado.web

from server.PikaClient import PikaClient
from server.Logger import Logger
from server.Session import Session


class BaseHandler(tornado.web.RequestHandler):
    timestamp = None

    def initialize(self, session_store):
        self.session_store = session_store

    def get_timestamp(self, uuid_key):
        return self.session_store.get(uuid_key)

    def set_timestamp(self, uuid_key):
        self.session_store.set(uuid_key)

    def write_json(self, msg):
        self.logger.debug('Add timestamp: %s' % self.timestamp)
        self.logger.debug('Get mesage: %s' % msg)
        messages = json.dumps(msg)
        self.logger.debug('Message will be write: %s' % messages)
        self.set_header("Content-type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "http://localhost:8080")
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Headers", "Origin, Content-Type")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.write(messages)
        self.finish()


class MainHandler(BaseHandler):

    def initialize(self, session_store, logger,
                   queue_answer, queue_read, queue_create):
        super(MainHandler, self).initialize(session_store)
        self.logger = logger
        self.queue_answer = queue_answer
        self.queue_read = queue_read
        self.queue_create = queue_create

    @tornado.web.asynchronous
    def get(self):
        self.render('client/index.html')

    @tornado.web.asynchronous
    def post(self):
        self.logger.debug('New POST request incoming')

        if self.get_secure_cookie('user'):
            self.logger.debug('Cookie already exists')
            uui = self.get_secure_cookie('user')
            self.logger.debug('Getting uuid: %s' % str(uui))
            self.timestamp = self.get_timestamp(uui)
            self.logger.debug('Getting shared '
                              'timestamp: %s' % str(self.timestamp))
            if not self.timestamp:
                self.logger.debug('Timestamp for uuid is not found, push it')
                self.set_timestamp(uui)
                self.timestamp = uui
        else:
            self.logger.debug('Add cookie')
            uui = str(uuid.uuid1())
            self.logger.debug('Generate uuid: %s' % str(uui))
            self.set_secure_cookie('user', uui)
            self.set_timestamp(uui)

        user_id = self.get_argument('id', default=None)
        message = self.get_argument('message', default=None)

        if not user_id:
            # request without user_id is not allowed
            error_msg = {
                'status': 400,
                'message': 'Id was missing'
            }
            self.write_json(error_msg)
            return
        elif not message:
            # read a message
            msg = {
                'id': user_id,
                'server': self.queue_answer
            }
            routing = self.queue_read
        else:
            # add a message
            msg = {
                'id': user_id,
                'content': message,
                'server': self.queue_answer
            }
            routing = self.queue_create

        self.application.pika.sample_message(msg=json.dumps(msg),
                                             routing_key=routing,
                                             tornado_callback=self.write_json)


def main():
    port = int(sys.argv[1])
    config_file = sys.argv[2]

    # queue for waiting answer from rabbit
    queue_answer = 'answer-%s' % port

    # queues for sending create/read messages
    queue_read = 'reading'
    queue_create = 'creation'

    logger_web = Logger('tornado-%s' % port).get()

    config = ConfigParser.ConfigParser()
    config.read(config_file)

    # TODO: check config
    redis_nodes = zip(config.get('rediscluster', 'hosts').split(' '),
                      config.get('rediscluster', 'ports').split(' '))
    rabbit_nodes = zip(config.get('rabbitmq', 'hosts').split(' '),
                       config.get('rabbitmq', 'ports').split(' '))

    startup_nodes = map(lambda node: {'host': node[0],
                                      'port': int(node[1])}, redis_nodes)
    logger_web.info('Redis has config: {0}'.format(startup_nodes))
    session_store = Session(startup_nodes=startup_nodes)

    public_root = os.path.join(os.path.dirname(__file__), 'client')
    application = tornado.web.Application(
        [(r'/', MainHandler, dict(session_store=session_store,
                                  logger=logger_web,
                                  queue_answer=queue_answer,
                                  queue_read=queue_read,
                                  queue_create=queue_create)),
         (r'/(.*)', tornado.web.StaticFileHandler, {'path': public_root})],
        # yeah, it's not secure, but it just for test
        cookie_secret='de973a5e-211f-11e6-bde5-3859f9e0729b'
    )

    logger_pika = Logger('tornado-%s-pika' % port).get()
    pc = PikaClient(logger=logger_pika,
                    queue_answer=queue_answer,
                    queue_read=queue_read,
                    queue_create=queue_create,
                    node_list=rabbit_nodes)
    application.pika = pc

    application.listen(port)
    logger_web.info('Tornado is serving on port {0}.'.format(port))
    ioloop = tornado.ioloop.IOLoop.instance()

    try:
        ioloop.add_timeout(time.time() + .1, pc.connect)
        ioloop.start()
    except:
        pc.stop()

if __name__ == '__main__':
    main()
