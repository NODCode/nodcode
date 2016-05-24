#!/usr/bin/env python

import os
import sys
import json
import time
# import uuid
import datetime

import tornado.ioloop
import tornado.web

from server.PikaClient import PikaClient
from server.Logger import Logger
from server.Session import Session


class BaseHandler(tornado.web.RequestHandler):

    def initialize(self, session_store):
        self.session_store = session_store

    def get_timestamp(self, uuid_key):
        self.session_store.get(uuid_key)

    def set_timestamp(self, uuid_key):
        self.session_store.set(uuid_key, str(datetime.datetime.now().time()))

    def write_json(self, msg):
        # self.logger.debug('Add timestamp: %s' % str(self.timestamp))
        # msg['timestamp'] = self.timestamp
        messages = json.dumps(msg)
        self.logger.debug('Messages for writing: %s' % str(messages))
        self.set_header("Content-type", "application/json")
        self.write(messages)
        self.finish()


class MainHandler(BaseHandler):

    def initialize(self, session_store, logger, queue_read, queue_create):
        super(MainHandler, self).initialize(session_store)
        self.logger = logger
        self.queue_read = queue_read
        self.queue_create = queue_create

    @tornado.web.asynchronous
    def get(self):
        self.render('client/src/index.html')

    @tornado.web.asynchronous
    def post(self):
        self.logger.debug('New POST request incoming')
        # For web client + Cookie
        # if self.get_secure_cookie('user'):
        #     self.logger.debug('Cookie already exists')
        #     uui = self.get_secure_cookie('user')
        #     self.logger.debug('Getting uuid: %' % str(uui))
        #     self.timestamp = self.get_timestamp(uui)
        #     self.logger.debug('Getting shared'
        #                       'timestamp: %' % str(self.timestamp))
        # else:
        #     self.logger.debug('Add cookie')
        #     uuid = str(uuid.uuid1())
        #     self.logger.debug('Generate uuid: %' % str(uui))
        #     self.set_secure_cookie('user', uuid)
        #     self.set_timestamp(uui)

        # Just for demonstrate sharing
        # self.timestamp = self.get_timestamp('user')
        # if not self.timestamp:
        #     self.get_timestamp('user')

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
                'id': user_id
            }
            routing = self.queue_read
        else:
            # add a message
            msg = {
                'id': user_id,
                'content': message
            }
            routing = self.queue_create

        self.application.pika.sample_message(msg=json.dumps(msg),
                                             routing_key=routing,
                                             tornado_callback=self.write_json)


def main():
    try:
        port = int(sys.argv[1])
    except:
        port = 8080

    # queue for waiting answer from rabbit
    queue_waiting = 'answer'

    # queues for sending create/read messages
    queue_read = 'reading'
    queue_create = 'creation'

    logger_web = Logger('tornado-%s' % port).get()

    # TODO: read it from config.ini or pass by args?
    startup_nodes = [{"host": "127.0.0.1", "port": "6380"},
                     {"host": "127.0.0.1", "port": "6381"},
                     {"host": "127.0.0.1", "port": "6382"}]
    #session_store = Session(startup_nodes=startup_nodes)
    session_store = None

    public_root = os.path.join(os.path.dirname(__file__), 'client/src')
    application = tornado.web.Application(
        [(r'/', MainHandler, dict(session_store=session_store,
                                  logger=logger_web,
                                  queue_read=queue_read,
                                  queue_create=queue_create)),
         (r'/(.*)', tornado.web.StaticFileHandler, {'path': public_root})],
        # yeah, it's not secure, but it just for test
        cookie_secret='de973a5e-211f-11e6-bde5-3859f9e0729b'
    )

    logger_pika = Logger('tornado-%s-pika' % port).get()
    pc = PikaClient(logger=logger_pika,
                    queue_name=queue_waiting,
                    queue_read=queue_read,
                    queue_create=queue_create)
    application.pika = pc

    application.listen(port)
    logger_web.info('Tornado is serving on port {0}.'.format(port))
    ioloop = tornado.ioloop.IOLoop.instance()

    ioloop.add_timeout(time.time() + .1, pc.connect)
    ioloop.start()

if __name__ == '__main__':
    main()
