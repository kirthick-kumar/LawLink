from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .lawyer import Lawyer
from .rating import Rating
from .contact import Contact

__all__ = ['db', 'User', 'Lawyer', 'Rating', 'Contact']