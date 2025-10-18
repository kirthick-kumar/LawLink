import json
import os
from datetime import datetime

class ChatService:
    def __init__(self, redis_service):
        self.redis_service = redis_service
        self.chat_history_key = 'lawlink:chat_history'
        self.cache_ttl = 3600  # 1 hour
        self.chat_file_path = 'chat_storage/chat_history.json'
        
        # Ensure chat storage directory exists
        os.makedirs('chat_storage', exist_ok=True)
        
        # Initialize JSON file if it doesn't exist
        self._initialize_json_file()
    
    def _initialize_json_file(self):
        """Initialize JSON file with empty structure if it doesn't exist"""
        if not os.path.exists(self.chat_file_path):
            initial_data = {
                "metadata": {
                    "created_at": self.get_current_timestamp(),
                    "total_messages": 0,
                    "last_updated": self.get_current_timestamp()
                },
                "messages": []
            }
            self._save_to_json_file(initial_data)
    
    def _save_to_json_file(self, data):
        """Save data to JSON file"""
        try:
            with open(self.chat_file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving to JSON file: {e}")
    
    def _load_from_json_file(self):
        """Load data from JSON file"""
        try:
            if os.path.exists(self.chat_file_path):
                with open(self.chat_file_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            return {"metadata": {"total_messages": 0}, "messages": []}
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error loading from JSON file: {e}")
            return {"metadata": {"total_messages": 0}, "messages": []}
    
    def _get_user_type(self, user_name):
        """Determine user type based on username"""
        user_name_lower = user_name.lower()
        
        if 'admin' in user_name_lower:
            return 'admin'
        elif '(lawyer)' in user_name_lower:
            return 'lawyer'
        else:
            return 'client'
    
    def save_message(self, user_name, message):
        """Save message to both JSON file and Redis cache"""
        # Create message object with all details
        message_data = {
            'user_name': user_name,
            'message': message,
            'user_type': self._get_user_type(user_name),
            'timestamp': self.get_current_timestamp(),
            'message_id': self._generate_message_id()
        }
        
        # Save to permanent storage (JSON file)
        self._save_to_json(message_data)
        
        # Update Redis cache
        self._update_redis_cache(message_data)
    
    def _generate_message_id(self):
        """Generate a unique message ID"""
        return f"msg_{int(datetime.now().timestamp() * 1000)}"
    
    def _save_to_json(self, message_data):
        """Save message to JSON file storage"""
        try:
            # Load existing data
            data = self._load_from_json_file()
            
            # Add new message
            data['messages'].append(message_data)
            
            # Update metadata
            data['metadata']['total_messages'] = len(data['messages'])
            data['metadata']['last_updated'] = self.get_current_timestamp()
            
            # Keep only last 5000 messages in file (prevent file from growing too large)
            if len(data['messages']) > 5000:
                data['messages'] = data['messages'][-5000:]
                data['metadata']['total_messages'] = len(data['messages'])
            
            # Save back to file
            self._save_to_json_file(data)
            
        except Exception as e:
            print(f"Error saving message to JSON: {e}")
    
    def _update_redis_cache(self, message_data):
        """Update Redis cache with new message"""
        try:
            # Get current cache
            cached_chat = self.redis_service.get(self.chat_history_key)
            if cached_chat:
                chat_data = json.loads(cached_chat)
                chat_data['messages'].append(message_data)
            else:
                # If no cache exists, create new cache from JSON file
                chat_data = self._load_chat_from_json_for_cache()
                chat_data['messages'].append(message_data)
            
            # Keep only last 1000 messages in cache for performance
            if len(chat_data['messages']) > 1000:
                chat_data['messages'] = chat_data['messages'][-1000:]
            
            # Update cache
            self.redis_service.setex(
                self.chat_history_key, 
                self.cache_ttl, 
                json.dumps(chat_data)
            )
            
        except Exception as e:
            print(f"Redis cache update error: {e}")
    
    def _load_chat_from_json_for_cache(self):
        """Load chat history from JSON file for cache initialization"""
        try:
            data = self._load_from_json_file()
            # Return only the last 1000 messages for cache
            messages = data.get('messages', [])
            return {
                'messages': messages[-1000:] if len(messages) > 1000 else messages
            }
        except Exception as e:
            print(f"Error loading chat from JSON for cache: {e}")
            return {'messages': []}
    
    def get_chat_history(self, limit=100, user_type=None):
        """Get chat history with optional limit and user type filter"""
        try:
            # Try to get from Redis first
            cached_chat = self.redis_service.get(self.chat_history_key)
            if cached_chat:
                chat_data = json.loads(cached_chat)
                messages = chat_data.get('messages', [])
                
                # Filter by user type if specified
                if user_type:
                    messages = [msg for msg in messages if msg.get('user_type') == user_type]
                
                return messages[-limit:] if limit else messages
            
            # Fallback to JSON file
            data = self._load_from_json_file()
            messages = data.get('messages', [])
            
            # Filter by user type if specified
            if user_type:
                messages = [msg for msg in messages if msg.get('user_type') == user_type]
            
            return messages[-limit:] if limit else messages
            
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []
    
    def get_chat_stats(self):
        """Get detailed chat statistics"""
        try:
            data = self._load_from_json_file()
            messages = data.get('messages', [])
            
            # Calculate statistics
            user_types = {}
            for message in messages:
                user_type = message.get('user_type', 'unknown')
                user_types[user_type] = user_types.get(user_type, 0) + 1
            
            cached_chat = self.redis_service.get(self.chat_history_key)
            cached_messages = 0
            if cached_chat:
                chat_data = json.loads(cached_chat)
                cached_messages = len(chat_data.get('messages', []))
            
            return {
                'total_messages': len(messages),
                'cached_messages': cached_messages,
                'cache_ttl': self.redis_service.ttl(self.chat_history_key),
                'user_types': user_types,
                'metadata': data.get('metadata', {}),
                'service': 'chat-microservice'
            }
        except Exception as e:
            return {'error': str(e), 'service': 'chat-microservice'}
    
    def get_cache_status(self):
        """Get detailed cache status"""
        try:
            cached_chat = self.redis_service.get(self.chat_history_key)
            cache_exists = cached_chat is not None
            ttl = self.redis_service.ttl(self.chat_history_key)
            
            if cached_chat:
                chat_data = json.loads(cached_chat)
                cached_messages = len(chat_data.get('messages', []))
            else:
                cached_messages = 0
                
            return {
                'cache_exists': cache_exists,
                'cached_messages': cached_messages,
                'ttl_seconds': ttl,
                'cache_key': self.chat_history_key
            }
        except Exception as e:
            return {'error': str(e)}

    def clear_cache(self):
        """Clear Redis cache and return status"""
        try:
            # Get status before clearing
            status_before = self.get_cache_status()
            
            # Clear the cache
            result = self.redis_service.delete(self.chat_history_key)
            
            # Get status after clearing
            status_after = self.get_cache_status()
            
            return {
                'success': result == 1,
                'cleared': result,
                'status_before': status_before,
                'status_after': status_after
            }
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_messages_by_user_type(self, user_type, limit=50):
        """Get messages filtered by user type"""
        return self.get_chat_history(limit=limit, user_type=user_type)
    
    def get_messages_by_user(self, username, limit=50):
        """Get messages from a specific user"""
        try:
            data = self._load_from_json_file()
            messages = data.get('messages', [])
            user_messages = [msg for msg in messages if msg.get('user_name', '').rstrip(':').replace('(Lawyer)', '').strip() == username]
            return user_messages[-limit:] if limit else user_messages
        except Exception as e:
            print(f"Error getting messages by user: {e}")
            return []
    
    def search_messages(self, search_term, limit=50):
        """Search messages by content"""
        try:
            data = self._load_from_json_file()
            messages = data.get('messages', [])
            search_results = [
                msg for msg in messages 
                if search_term.lower() in msg.get('message', '').lower()
            ]
            return search_results[-limit:] if limit else search_results
        except Exception as e:
            print(f"Error searching messages: {e}")
            return []
    
    def get_current_timestamp(self):
        """Get current timestamp in readable format"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def clear_cache(self):
        """Clear Redis cache"""
        return self.redis_service.delete(self.chat_history_key)
    
    def export_chat_data(self, output_path=None):
        """Export chat data to a JSON file"""
        try:
            data = self._load_from_json_file()
            export_path = output_path or f'chat_storage/chat_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            
            with open(export_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            
            return export_path
        except Exception as e:
            print(f"Error exporting chat data: {e}")
            return None