from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from flask_socketio import emit
from models import db, User

chats = ''
names = []
msgs = []

def retrieve_chat():
    """Retrieves messages from chat history text file"""
    global chats, names, msgs
    chats = ''
    names = []
    msgs = []
    
    try:
        with open("Chat History/chat.txt", mode='r') as file:
            chats = file.read().rstrip('\n')
        
        if chats:
            chat_list = chats.split('\n')
            for chat in chat_list:
                if ':' in chat:
                    n = chat.index(':') + 1
                    names.append(chat[:n])
                    msgs.append(chat[n:])
    except FileNotFoundError:
        pass

@login_required
def openchat():
    retrieve_chat()
    usernames = [name[:-1].replace('(Lawyer)', '') for name in names]
    
    users = []
    for username in usernames:
        user = db.session.execute(db.Select(User).where(User.username == username)).scalar()
        if user:
            users.append(user)
    
    return render_template('openchat.html', user=current_user, names=names, msgs=msgs, 
                         n=len(names), users=users, admins=['1'])

def handle_chat_event(json, methods=['POST', 'GET']):
    """Handle incoming chat messages via WebSocket"""
    try:
        if 'user_name' in json and 'message' in json:
            with open('Chat History/chat.txt', mode='a') as file:
                file.write(f"{json['user_name']}: {json['message']}\n")
    except KeyError:
        pass
    
    emit('response', json)
    return redirect(url_for('openchat'))