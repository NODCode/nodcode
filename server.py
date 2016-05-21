#!/usr/bin/env python

import sys
import json
import time

import pika
import tornado.ioloop
import tornado.web

from server.PikaClient import PikaClient
from server.Logger import Logger
from server.Session import Session


class BaseHandler(tornado.web.RequestHandler):

    def initialize(self, session_store, pclient):
        self.session_store = session_store
        self.pclient = pclient
        self.logger = Logger('tornado').get()

    def get_user(self):
        self.session_store.get('user')

    def set_user(self, name):
        self.session_store.set('user', name)


class MainHandler(BaseHandler):

    def initialize(self, session_store, pclient=None):
        super(MainHandler, self).initialize(session_store, pclient)
        self.queue_to_read = 'reading'
        self.queue_to_create = 'creation'
        self.queue_for_waiting = 'answer'
        if pclient:
            self.pclient.channel.queue_declare(queue=self.queue_for_waiting,
                                               callback=self.on_queue_consume,
                                               durable=True)

    @tornado.web.asynchronous
    def get(self):
        self.logger.debug('New GET request')
        if not self.get_user():
            self.redirect('/login')
            return
        self.logger.debug('Index page')
        # TODO: put correct path
        self.render('index?')
        self.finish()

    @tornado.web.asynchronous
    def post(self):
        self.logger.debug('New POST request')
        if not self.get_user():
            error_msg = {
                'status': 400,
                'message': 'Something gone wrong'
            }
            self.write(json.dumps(error_msg))
            self.finish()
            return

        user_id = self.get_argument('id', default=None)
        message = self.get_argument('message', default=None)

        if not user_id:
            # request without user_id is not allowed
            error_msg = {
                'status': 400,
                'message': 'id is not found'
            }
            self.write(json.dumps(error_msg))
            self.finish()
            return
        elif not message:
            # read message request
            msg = {
                'id': user_id
            }
            routing = self.queue_to_read
        else:
            # add message here
            msg = {
                'id': user_id,
                'message': message
            }
            routing = self.queue_to_create

        self.mq_ch = self.pclient.channel
        props = pika.BasicProperties(delivery_mode=1)
        self.mq_ch.basic_publish(exchange='', routing_key=routing,
                                 body=json.dumps(msg), properties=props)

    def on_queue_consume(self, frame):
        self.logger.info('Queue Bound. Issuing Basic Consume.')
        self.mq_ch.basic_consume(consumer_callback=self.on_response,
                                 queue=self.queue_for_waiting, no_ack=True)

    def on_response(self, channel, method, header, body):
        self.logger.debug('Got response:\n'
                          'body: {body}\n'
                          'header: {header}\n'
                          'channel: {channel}'.format(body=body,
                                                      header=header,
                                                      channel=channel))
        msg = {
            'status': 400,
            'message': str(body)
        }
        self.write_json(msg)
        self.flush()
        # self.finish()
        # TODO: BUT FINISH TWICE?! HOW TO SOLVE IT?!


class LoginHandler(BaseHandler):

    def initialize(self, session_store):
        super(LoginHandler, self).initialize(session_store=session_store,
                                             pclient=None)

    def get(self):
        self.logger.debug('Login page')
        # TODO: put correct path
        self.render('login?')
        self.finish()

    def post(self):
        # TODO: definitly, we should use more secure way, but not today
        self.set_user('user', self.get_argument('name'))
        self.logger.debug('Login is passed, redirecting...')
        self.redirect('/')


def main():
    pclient = PikaClient()
    session_store = Session()
    application = tornado.web.Application(
        [(r'/', MainHandler, dict(session_store=session_store,
                                  pclient=pclient)),
         (r'/login', LoginHandler, dict(session_store=session_store))]
    )
    # TODO: Read it from config
    try:
        port = int(sys.argv[1])
    except:
        port = 8080
    application.listen(port)
    Logger('app').get().info('Tornado is serving on port {0}.'.format(port))
    ioloop = tornado.ioloop.IOLoop.instance()

    # TODO: make it after login?
    ioloop.add_timeout(time.time() + .1, pclient.connect)
    ioloop.start()

if __name__ == '__main__':
    main()
