import simplejson as json
import redis

r = redis.Redis()


def cache(duration):
    def decorate(func):
        def wrapper(self, *args, **kwargs):
            # set up the key for the cache
            key = ':'.join([func.__module__,
                           func.__name__,
                           self.search_engine,
                           self.keyword,
                           self.domain])
            value_flat = r.get(key)
            if value_flat is None:
                value = func(self, *args, **kwargs)
                value_flat = json.dumps(value)
                r.set(key, value_flat)
                r.expire(key, duration)
            else:
                value = json.loads(value_flat)
            return value
        return wrapper
    return decorate
