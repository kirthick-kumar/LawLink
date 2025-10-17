from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from flask_socketio import emit
from models import db, User
import redis
import json
import os

# Redis configuration
redis_client = redis.Redis(
    host='localhost', 
    port=6379, 
    db=0, 
    decode_responses=True,
    socket_connect_timeout=3,
    socket_timeout=3
)

# Constants
CHAT_HISTORY_KEY = 'lawlink:chat_history'
CHAT_CACHE_TTL = 3600  # 1 hour cache

def retrieve_chat():
    """Retrieves messages from Redis cache or text file"""
    global names, msgs
    names = []
    msgs = []
    
    try:
        # Try to get from Redis cache first
        cached_chat = redis_client.get(CHAT_HISTORY_KEY)
        if cached_chat:
            chat_data = json.loads(cached_chat)
            names = chat_data['names']
            msgs = chat_data['msgs']
            return
        
        # If not in cache, read from file and cache it
        if os.path.exists("Chat History/chat.txt"):
            with open("Chat History/chat.txt", mode='r', encoding='utf-8') as file:
                chats = file.read().rstrip('\n')
            
            if chats:
                chat_list = chats.split('\n')
                for chat in chat_list:
                    if ':' in chat:
                        n = chat.index(':') + 1
                        names.append(chat[:n])
                        msgs.append(chat[n:])
                
                # Cache in Redis
                chat_data = {'names': names, 'msgs': msgs}
                redis_client.setex(CHAT_HISTORY_KEY, CHAT_CACHE_TTL, json.dumps(chat_data))
                
    except (redis.RedisError, FileNotFoundError, json.JSONDecodeError) as e:
        # Fallback to file reading if Redis fails
        print(f"Redis/file error: {e}. Using file fallback.")
        try:
            if os.path.exists("Chat History/chat.txt"):
                with open("Chat History/chat.txt", mode='r', encoding='utf-8') as file:
                    chats = file.read().rstrip('\n')
                
                if chats:
                    chat_list = chats.split('\n')
                    for chat in chat_list:
                        if ':' in chat:
                            n = chat.index(':') + 1
                            names.append(chat[:n])
                            msgs.append(chat[n:])
        except Exception as file_error:
            print(f"File reading error: {file_error}")

def save_message_to_file(user_name, message):
    """Save message to both file and update Redis cache"""
    try:
        # Save to permanent storage (file)
        with open('Chat History/chat.txt', mode='a', encoding='utf-8') as file:
            file.write(f"{user_name}: {message}\n")
        
        # Update Redis cache
        update_redis_cache(user_name, message)
        
    except Exception as e:
        print(f"Error saving message: {e}")

def update_redis_cache(user_name, message):
    """Update Redis cache with new message"""
    try:
        # Get current cache
        cached_chat = redis_client.get(CHAT_HISTORY_KEY)
        if cached_chat:
            chat_data = json.loads(cached_chat)
            chat_data['names'].append(user_name)
            chat_data['msgs'].append(message)
        else:
            # If no cache exists, create new cache from file
            chat_data = {'names': [], 'msgs': []}
            if os.path.exists("Chat History/chat.txt"):
                with open("Chat History/chat.txt", mode='r', encoding='utf-8') as file:
                    chats = file.read().rstrip('\n')
                
                if chats:
                    chat_list = chats.split('\n')
                    for chat in chat_list:
                        if ':' in chat:
                            n = chat.index(':') + 1
                            chat_data['names'].append(chat[:n])
                            chat_data['msgs'].append(chat[n:])
            
            # Add new message
            chat_data['names'].append(user_name)
            chat_data['msgs'].append(message)
        
        # Update cache with extended TTL
        redis_client.setex(CHAT_HISTORY_KEY, CHAT_CACHE_TTL, json.dumps(chat_data))
        
    except (redis.RedisError, json.JSONDecodeError) as e:
        print(f"Redis cache update error: {e}")

def clear_chat_cache():
    """Clear Redis chat cache (useful for testing or cache invalidation)"""
    try:
        redis_client.delete(CHAT_HISTORY_KEY)
    except redis.RedisError as e:
        print(f"Error clearing cache: {e}")

def get_chat_stats():
    """Get chat statistics from Redis"""
    try:
        cached_chat = redis_client.get(CHAT_HISTORY_KEY)
        if cached_chat:
            chat_data = json.loads(cached_chat)
            return {
                'cached_messages': len(chat_data['names']),
                'cache_ttl': redis_client.ttl(CHAT_HISTORY_KEY)
            }
        return {'cached_messages': 0, 'cache_ttl': -2}
    except redis.RedisError:
        return {'cached_messages': 0, 'cache_ttl': -1}

@login_required
def openchat():
    retrieve_chat()
    
    # Create a list to store user data for each message
    user_data_list = []
    
    for name in names:
        # Extract username from the name (remove colon and (Lawyer) tag)
        username = name.rstrip(':').replace('(Lawyer)', '').strip()
        
        # Try to find the user in the database
        user = db.session.execute(db.select(User).where(User.username == username)).scalar()
        
        if user:
            user_data_list.append(user)
        else:
            # Create a dummy user object for users not found in database
            class DummyUser:
                def __init__(self, username):
                    self.username = username
                    self.id = None
                    self.lawyer = None
            
            dummy_user = DummyUser(username)
            user_data_list.append(dummy_user)
    
    chat_stats = get_chat_stats()
    
    return render_template('openchat.html', 
                         user=current_user, 
                         names=names, 
                         msgs=msgs, 
                         n=len(names), 
                         users=user_data_list,
                         admins=['1'],
                         chat_stats=chat_stats)

def handle_chat_event(json, methods=['POST', 'GET']):
    """Handle incoming chat messages via WebSocket"""
    try:
        if 'user_name' in json and 'message' in json:
            user_name = json['user_name']
            message = json['message']
            
            # Save to both file and Redis
            save_message_to_file(user_name, message)
            
    except KeyError:
        pass
    except Exception as e:
        print(f"Error handling chat event: {e}")
    
    # Broadcast to all clients
    emit('response', json, broadcast=True)