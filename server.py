#!/usr/bin/env python

#import platform
#import os
import sys
import time
import json
#import uuid

import pika
import tornado.ioloop
import tornado.web

from server.PikaClient import PikaClient

import redis

# TODO: get rid of weird 'print'. Use logging for it!
# import logging


class BaseHandler(tornado.web.RequestHandler):

    # TODO: use more secure way for that:
    # generate uuid and save as hset
    def get_user(self):
        self.redis_store.get('user')

    def set_user(self, name):
        self.redis_store.set('user', name)


class MainHandler(BaseHandler):

    def initialize(self, redis_store, pika_client):
        self.redis_store = redis_store
        self.pika_client = pika_client
        self.queue_to_logic = 'task_logic'
        self.queue_for_waiting = 'task_rest'
        self.pika_client.channel.queue_declare(queue=self.queue_for_waiting,
                                               callback=self.on_queue_consume,
                                               durable=True)

    @tornado.web.asynchronous
    def get(self):
        user = self.get_user()
        if not self.get_user():
            self.redirect("/login")
            return
        self.write('hello, {user_name}'.format(
            user_name=tornado.escape.xhtml_escape(user)))
        self.finish()

    @tornado.web.asynchronous
    def post(self):
        if not self.get_user():
            # TODO: common error json response
            return

        id = self.get_argument('id')
        message = self.get_argument('message')

        # TODO: parameter error json response

        msg = {
            'id': id,
            'message': message
        }
        self.mq_ch = self.pika_client.channel
        props = pika.BasicProperties(delivery_mode=1)
        self.mq_ch.basic_publish(exchange='', routing_key=self.queue_to_logic,
                                 body=json.dumps(msg), properties=props)

    def on_queue_consume(self, frame):
        print('Queue Bound. Issuing Basic Consume.')
        self.mq_ch.basic_consume(consumer_callback=self.on_response,
                                 queue=self.queue_for_waiting, no_ack=True)

    def on_response(self, channel, method, header, body):
        # TODO: correct response handling!
        self.write('got it: {some_body}'.format(some_body=body))
        self.flush()
        # self.finish()
        # TODO: BUT FINISH TWICE?! HOW TO SOLVE IT?!


class LoginHandler(BaseHandler):

    def initialize(self, redis_store):
        self.redis_store = redis_store

    def get(self):
        # TODO: add "login" fomr here
        # self.write('Put your name somewhere...')
        self.render('../client/src/index.html')

    def post(self):
        self.set_user('user', self.get_argument('name'))
        self.redirect('/')


def main():
    pika_client = PikaClient()
    redis_store = redis.StrictRedis()
    settings = {
        'static_path': '../client/src'
    }
    application = tornado.web.Application(
        [(r'/', MainHandler, dict(redis_store=redis_store,
                                  pika_client=pika_client)),
         (r'/login', LoginHandler, dict(redis_store=redis_store))],
         settings
    )
    try:
        port = int(sys.argv[1])
    except:
        port = 8080
    application.listen(port)
    print("Tornado is serving on port {0}.".format(port))
    ioloop = tornado.ioloop.IOLoop.instance()
    # TODO: make it after login?
    ioloop.add_timeout(time.time() + .1, pika_client.connect)
    ioloop.start()

if __name__ == '__main__':
    main()
