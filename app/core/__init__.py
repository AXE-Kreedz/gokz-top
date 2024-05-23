from redis import Redis


def get_cache():
    return Redis(host='localhost', port=6379)
