import cPickle as pickle
from uuid import uuid4
from rediscluster import StrictRedisCluster
from Logger import Logger


class Session(object):
    sessionid = None

    def __init__(self, **options):
        self.options = {
            'key_prefix': 'session',
            'expire': 7200,
        }
        self.options.update(options)
        self.redis = StrictRedisCluster(
            startup_nodes=self.options['startup_nodes'])
        self.logger = Logger('session').get()

    def get(self):
        self.logger.debug('Get session')
        if self.sessionid:
            return self._get_session(self.sessionid, 'user')
        else:
            self.sessionid = self._generate_sid()
            return None

    def set(self, name):
        self.logger.debug('Set new session: name {name}'.format(name=name))
        self._set_session(self.sessionid, 'user', name)

    def delete(self):
        self.redis.delete(self._prefixed(self.sessionid))

    def _prefixed(self, sid):
        return '%s:%s' % (self.options['key_prefix'], sid)

    def _generate_sid(self, ):
        return uuid4().get_hex()

    def _get_session(self, sid, name):
        data = self.redis.hget(self._prefixed(sid), name)
        session = pickle.loads(data) if data else None
        return session

    def _set_session(self, sid, session_data, name):
        expiry = self.options['expire']
        self.redis.hset(self._prefixed(sid), name, pickle.dumps(session_data))
        if expiry:
            self.redis.expire(self._prefixed(sid), expiry)
