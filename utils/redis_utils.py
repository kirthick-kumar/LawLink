import redis
import json

class ChatCache:
    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost', 
            port=6379, 
            db=0, 
            decode_responses=True
        )
        self.chat_key = 'lawlink:chat_history'
        self.ttl = 3600  # 1 hour
    
    def get_chat_history(self):
        """Get chat history from cache"""
        try:
            cached = self.redis_client.get(self.chat_key)
            if cached:
                return json.loads(cached)
        except (redis.RedisError, json.JSONDecodeError):
            pass
        return None
    
    def set_chat_history(self, chat_data):
        """Set chat history in cache"""
        try:
            self.redis_client.setex(
                self.chat_key, 
                self.ttl, 
                json.dumps(chat_data)
            )
            return True
        except redis.RedisError:
            return False
    
    def add_message(self, user_name, message):
        """Add single message to cache"""
        try:
            chat_data = self.get_chat_history() or {'names': [], 'msgs': []}
            chat_data['names'].append(user_name)
            chat_data['msgs'].append(message)
            return self.set_chat_history(chat_data)
        except Exception:
            return False
    
    def clear_cache(self):
        """Clear chat cache"""
        try:
            self.redis_client.delete(self.chat_key)
            return True
        except redis.RedisError:
            return False