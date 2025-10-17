from flask_login import UserMixin
from typing import List
from . import db

class User(db.Model, UserMixin):
    __table_name__ = 'user'
    id: db.Mapped[int] = db.mapped_column(primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    
    # Relationship
    lawyer: db.Mapped["Lawyer"] = db.relationship(back_populates="user")
    rating_user: db.Mapped[List["Rating"]] = db.relationship(back_populates="rating_author")

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)