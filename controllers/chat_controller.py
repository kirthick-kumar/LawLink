from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from models import db, User
import requests
import socketio

# Chat microservice configuration
CHAT_SERVICE_URL = 'http://localhost:5001'

# Initialize Socket.IO client
sio = socketio.Client()

@login_required
def openchat():
    """Render chat page with history from microservice"""
    try:
        # Get chat history from microservice
        response = requests.get(f"{CHAT_SERVICE_URL}/api/chat/history")
        chat_history = response.json() if response.status_code == 200 else []
        
        # Get all users for user lookup in template
        all_users = db.session.execute(db.select(User)).scalars()
        
        return render_template('openchat.html', 
                             user=current_user,
                             chat_history=chat_history,
                             all_users=all_users,
                             admins=['1'])
                             
    except requests.RequestException as e:
        print(f"Error connecting to chat service: {e}")
        # Fallback: render empty chat
        return render_template('openchat.html',
                             user=current_user,
                             chat_history=[],
                             all_users=[],
                             admins=['1'])

def connect_to_chat_service():
    """Connect to chat microservice"""
    try:
        sio.connect(CHAT_SERVICE_URL)
        print("Connected to chat microservice")
        return True
    except Exception as e:
        print(f"Failed to connect to chat service: {e}")
        return False

# Socket event handlers
@sio.event
def connect():
    print('Connected to chat microservice')

@sio.event
def disconnect():
    print('Disconnected from chat microservice')

@sio.event
def new_message(data):
    """Handle new messages from chat service"""
    # Messages are handled by frontend JavaScript
    pass

@sio.event
def user_joined(data):
    """Handle user join notifications"""
    # Handled by frontend JavaScript
    pass