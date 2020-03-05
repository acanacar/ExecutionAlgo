#10.1.26.182
#'localhost'

import redis

config = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
}

r = redis.StrictRedis(**config)
