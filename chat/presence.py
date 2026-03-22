import os

from redis import Redis
from redis.exceptions import RedisError


ONLINE_USERS_SET = 'presence:online_users'
USER_CONNECTIONS_KEY = 'presence:user:{user_id}:connections'
REDIS_URL = os.environ.get('PRESENCE_REDIS_URL', 'redis://127.0.0.1:6379/1')


def _client():
    return Redis.from_url(REDIS_URL, decode_responses=True)


def mark_user_online(user_id, connection_id):
    try:
        client = _client()
        user_connections_key = USER_CONNECTIONS_KEY.format(user_id=user_id)

        with client.pipeline() as pipe:
            pipe.sadd(ONLINE_USERS_SET, user_id)
            pipe.sadd(user_connections_key, connection_id)
            pipe.expire(user_connections_key, 60 * 60)
            pipe.execute()
    except RedisError:
        return


def mark_user_offline(user_id, connection_id):
    try:
        client = _client()
        user_connections_key = USER_CONNECTIONS_KEY.format(user_id=user_id)

        with client.pipeline() as pipe:
            pipe.srem(user_connections_key, connection_id)
            pipe.scard(user_connections_key)
            result = pipe.execute()

        open_connections = result[1]
        if open_connections == 0:
            with client.pipeline() as pipe:
                pipe.srem(ONLINE_USERS_SET, user_id)
                pipe.delete(user_connections_key)
                pipe.execute()
    except RedisError:
        return


def is_user_online(user_id):
    try:
        client = _client()
        return bool(client.sismember(ONLINE_USERS_SET, user_id))
    except RedisError:
        return False
