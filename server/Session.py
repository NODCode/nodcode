import cPickle as pickle
import datetime
import time
import tornado.ioloop
from rediscluster import StrictRedisCluster
from Logger import Logger


class Session(object):
    _uui = None
    _max_retry = 5
    _retry_num = 0

    def __init__(self, **options):
        self.options = {
            'key_prefix': 'session',
            'expire': 7200,
        }
        self.options.update(options)
        self.connect()
        self.logger = Logger('session').get()

    def connect(self):
        def func():
            self.redis = StrictRedisCluster(
                startup_nodes=self.options['startup_nodes'])
        self._safe_way(func)

    def get(self, uui):
        self.logger.debug('Try to get session')

        def _get():
            return self._get_session(uui)
        return self._safe_way(_get)

    def set(self, uui):
        self.logger.debug('Try to set new session: '
                          'uuid {name}'.format(name=uui))
        self._uui = uui

        def _set():
            self._set_session(uui,
                              str(datetime.datetime.now().time()))
        self._safe_way(_set)

    def _safe_way(self, func):
        try:
            return func()
        except:
            if self._max_retry == self._retry_num:
                self.logger.debug('Max try to reconnect. Closed')
                tornado.ioloop.IOLoop.instance().stop()
            else:
                self._retry_num += 1
                self.logger.debug('Fail to connect.'
                                  'Try to reconnect after 6 sec')
                time.sleep(6)
                self.connect()
                return func()

    def delete(self):
        self.logger.debug('Try to delete session')
        self.redis.delete(self._prefixed(self._uui))

    def _prefixed(self, sid):
        return '%s:%s' % (self.options['key_prefix'], sid)

    def _get_session(self, uui):
        try_to_get = self._prefixed(uui)
        self.logger.debug('Get session data: {data}'.format(data=try_to_get))
        data = self.redis.hget(try_to_get, 'user')
        session = pickle.loads(data) if data else None
        self.logger.debug('Got: %s' % session)
        return session

    def _set_session(self, uui, session_data):
        expiry = self.options['expire']
        try_to_set = self._prefixed(uui)
        self.logger.debug('Set session data: {data}'.format(data=try_to_set))
        self.redis.hset(try_to_set,
                        'user',
                        pickle.dumps(session_data))
        if expiry:
            self.redis.expire(self._prefixed(uui), expiry)
