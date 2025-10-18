from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO
import os

# Import models
from models import db, User

# Import controllers
from controllers.auth_controller import login, signup, verify_otp, logout
from controllers.lawyer_controller import profile_edit, profile
from controllers.chat_controller import openchat, connect_to_chat_service
from controllers.admin_controller import admin, delete_profile_caller
from controllers.contact_controller import contact
from controllers.search_controller import search as search_function

app = Flask(__name__, static_folder=r'D:\Studies\Pycharm\Projects\Chat Test\static')

# Configuration
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lawlink.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
Bootstrap5(app)
socketio = SocketIO(app)
db.init_app(app)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'error'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Routes
app.add_url_rule('/', 'home', lambda: render_template('index.html'))
app.add_url_rule('/about', 'about', lambda: render_template('about.html'))
app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/signup', 'signup', signup, methods=['GET', 'POST'])
app.add_url_rule('/signup/otp', 'verify_otp', verify_otp, methods=['GET', 'POST'])
app.add_url_rule('/logout', 'logout', logout)
app.add_url_rule('/editprofile/', 'profile_edit', profile_edit, methods=['GET', 'POST'])
app.add_url_rule('/profile/<lawyer_id>', 'profile', profile, methods=['POST', 'GET'])
app.add_url_rule('/search', 'search', search_function, methods=['POST', 'GET'])
app.add_url_rule('/openchat', 'openchat', openchat)
app.add_url_rule('/admin', 'admin', admin, methods=['POST', 'GET'])
app.add_url_rule('/contact', 'contact', contact, methods=['POST', 'GET'])
app.add_url_rule('/delete_profile', 'delete_profile', delete_profile_caller, methods=['POST', 'GET'])


# Create tables within application context
with app.app_context():
    db.create_all()
    # Connect to chat microservice on startup
    chat_connected = connect_to_chat_service()
    if chat_connected:
        print("Successfully connected to chat microservice")
    else:
        print("Failed to connect to chat microservice - chat functionality may be limited")

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, port=5000)