import redis
import json

class RedisService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=3
        )
    
    def get(self, key):
        try:
            return self.redis_client.get(key)
        except redis.RedisError as e:
            print(f"Redis get error: {e}")
            return None
    
    def setex(self, key, ttl, value):
        try:
            self.redis_client.setex(key, ttl, value)
            return True
        except redis.RedisError as e:
            print(f"Redis setex error: {e}")
            return False
    
    def delete(self, key):
        try:
            self.redis_client.delete(key)
            return True
        except redis.RedisError as e:
            print(f"Redis delete error: {e}")
            return False
    
    def ttl(self, key):
        try:
            return self.redis_client.ttl(key)
        except redis.RedisError as e:
            print(f"Redis ttl error: {e}")
            return -1