#!/usr/bin/env python

import sys
import json
import time

import tornado.ioloop
import tornado.web

from server.PikaClient import PikaClient
from server.Logger import Logger
from server.Session import Session


class BaseHandler(tornado.web.RequestHandler):

    def initialize(self, session_store):
        self.session_store = session_store

    def get_user(self):
        self.session_store.get()

    def set_user(self, name):
        self.session_store.set(name)


class MainHandler(BaseHandler):

    def initialize(self, session_store, logger, queue_read, queue_create):
        super(MainHandler, self).initialize(session_store)
        self.logger = logger
        self.queue_read = queue_read
        self.queue_create = queue_create

    @tornado.web.asynchronous
    def get(self):
        self.logger.debug('New GET request incoming')
        if not self.get_user():
            self.redirect('/login')
            return
        self.logger.debug('Index page')
        # TODO: put correct path
        # self.render('index_page')
        self.write('index')
        self.finish()

    @tornado.web.asynchronous
    def post(self):
        self.logger.debug('New POST request incoming')
        # if not self.get_user():
        #     error_msg = {
        #         'status': 400,
        #         'message': 'Something gone wrong'
        #     }
        #     self.write_json(error_msg)
        #     return

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
                'message': message
            }
            routing = self.queue_create

        self.application.pika.sample_message(msg=json.dumps(msg),
                                             routing_key=routing,
                                             tornado_callback=self.write_json)

    def write_json(self, msg):
        messages = json.dumps(msg)
        self.logger.debug('Messages for writing: %s' % str(messages))
        self.set_header("Content-type", "application/json")
        self.write(messages)
        self.finish()


class LoginHandler(BaseHandler):

    def initialize(self, session_store, logger):
        super(LoginHandler, self).initialize(session_store=session_store)
        self.logger = logger

    def get(self):
        self.logger.debug('Login page')
        # TODO: put correct path
        # self.render('login_page')
        self.write('login')
        self.finish()

    def post(self):
        # TODO: definitly, we should use more secure way, but not today
        self.set_user(self.get_argument('name'))
        self.logger.debug('Login is passed, redirecting...')
        self.redirect('/')


def main():
    # TODO: Read it from config
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
    session_store = Session()
    application = tornado.web.Application(
        [(r'/', MainHandler, dict(session_store=session_store,
                                  logger=logger_web,
                                  queue_read=queue_read,
                                  queue_create=queue_create)),
         (r'/login', LoginHandler, dict(session_store=session_store,
                                        logger=logger_web))]
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
