from django.core.cache import cache as default_cache
from django.utils.timezone import now


def timeout_at(time, cache=default_cache):
    if time is None:
        return cache.default_timeout
    elif cache.default_timeout is None:
        return (time - now()).total_seconds()
    else:
        return min(cache.default_timeout, (time - now()).total_seconds())
