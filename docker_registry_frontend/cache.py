import time


class cache_with_timeout:
    DEFAULT_TIMEOUT = 60

    def __init__(self, timeout=None):
        self.__cache = {}
        self.__timeout = timeout

    def __call__(self, f):
        def decorator(*args, **kwargs):
            timeout = self.__timeout or cache_with_timeout.DEFAULT_TIMEOUT
            key = (args, frozenset(kwargs))

            if key in self.__cache:
                ts, result = self.__cache[key]
                if (time.time() - ts) < timeout:
                    return result

            result = f(*args, **kwargs)
            self.__cache[key] = (time.time(), result)

            return result
        return decorator
