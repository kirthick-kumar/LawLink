from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from services.redis_service import RedisService
from services.chat_service import ChatService

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chat-service-secret-key'
CORS(app, origins=["http://localhost:5000"])  # Allow main app origin
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize services
redis_service = RedisService()
chat_service = ChatService(redis_service)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "chat-service"})

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """API endpoint to get chat history"""
    try:
        history = chat_service.get_chat_history()
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat/cache/status', methods=['GET'])
def get_cache_status():
    """Get current cache status"""
    try:
        status = chat_service.get_cache_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
     
@app.route('/api/chat/cache/clear', methods=['GET'])
def clear_cache():
    """Clear cache with detailed response"""
    try:
        result = chat_service.clear_cache()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat/cache/refresh', methods=['GET'])
def refresh_cache():
    """Clear and rebuild cache from JSON file"""
    try:
        # Clear existing cache
        chat_service.clear_cache()
        
        # Get latest messages to rebuild cache
        messages = chat_service.get_chat_history(limit=1000)
        
        # This will automatically rebuild cache on next access
        return jsonify({
            "message": "Cache refresh initiated",
            "messages_in_json": len(messages)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/chat/stats', methods=['GET'])
def get_chat_stats():
    """API endpoint to get chat statistics"""
    try:
        stats = chat_service.get_chat_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'data': 'Connected to chat service'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle incoming chat messages"""
    try:
        user_name = data.get('user_name')
        message = data.get('message')
        
        if user_name and message:
            # Save message
            chat_service.save_message(user_name, message)
            
            # Broadcast to all clients
            emit('new_message', {
                'user_name': user_name,
                'message': message,
                'timestamp': chat_service.get_current_timestamp()
            }, broadcast=True)
            
    except Exception as e:
        emit('error', {'error': str(e)})

@socketio.on('join_chat')
def handle_join_chat(data):
    """Handle user joining chat"""
    user_name = data.get('user_name')
    if user_name:
        emit('user_joined', {
            'user_name': user_name,
            'message': f'{user_name} joined the chat',
            'timestamp': chat_service.get_current_timestamp()
        }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)