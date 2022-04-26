import redis


class RedisConnection:
  client = redis.StrictRedis(host='redis', port=6379)
