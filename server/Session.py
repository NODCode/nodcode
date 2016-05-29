import cPickle as pickle
import datetime
from rediscluster import StrictRedisCluster
from Logger import Logger


class Session(object):
    uui = None

    def __init__(self, **options):
        self.options = {
            'key_prefix': 'session',
            'expire': 7200,
        }
        self.options.update(options)
        self.redis = StrictRedisCluster(
            startup_nodes=self.options['startup_nodes'])
        self.logger = Logger('session').get()

    def get(self, uui):
        self.logger.debug('Try to get session')
        return self._get_session(uui)

    def set(self, uui):
        self.logger.debug('Try to set new session: uuid {name}'.format(name=uui))
        self.uui = uui
        self._set_session(uui,
                          str(datetime.datetime.now().time()))

    def delete(self):
        self.logger.debug('Try to delete session')
        self.redis.delete(self._prefixed(self.uui))

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
