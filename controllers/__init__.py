from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

# Constants
admins = ['1']
rating_dict = {
    5: '🌕🌕🌕🌕🌕',
    4.7: '🌕🌕🌕🌕🌖',
    4.5: '🌕🌕🌕🌕🌗',
    4.2: '🌕🌕🌕🌕🌘',
    4: '🌕🌕🌕🌕🌑',
    3.7: '🌕🌕🌕🌖🌑',
    3.5: '🌕🌕🌕🌗🌑',
    3.2: '🌕🌕🌕🌘🌑',
    3: '🌕🌕🌕🌑🌑',
    2.7: '🌕🌕🌖🌑🌑',
    2.5: '🌕🌕🌗🌑🌑',
    2.2: '🌕🌕🌘🌑🌑',
    2: '🌕🌕🌑🌑🌑',
    1.7: '🌕🌖🌑🌑🌑',
    1.5: '🌕🌗🌑🌑🌑',
    1.2: '🌕🌘🌑🌑🌑',
    1: '🌕🌑🌑🌑🌑',
}

def admin_only(function):
    """Decorator function to check if the current user is an admin"""
    @wraps(function)
    def wrapper_function(*args, **kwargs):
        if current_user.get_id() in admins:
            return function(*args, **kwargs)
        else:
            flash("Login in as an admin to access that page", "error")
            return redirect(url_for('login'))
    return wrapper_function