from flask_login import UserMixin
from typing import List
from . import db

class Lawyer(db.Model, UserMixin):
    __table_name__ = 'lawyer'
    id: db.Mapped[int] = db.mapped_column(primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    pic_url = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.String(200), nullable=False)
    education = db.Column(db.String(20), nullable=False)
    bar_council_id = db.Column(db.Integer, nullable=False, unique=True)
    location = db.Column(db.String(200), nullable=False)
    expertise = db.Column(db.String(200), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    ongoing = db.Column(db.Integer, nullable=False)
    won = db.Column(db.Integer, nullable=False)
    lost = db.Column(db.Integer, nullable=False)
    verified = db.Column(db.Boolean, default=False)
    phone = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(200), nullable=False)
    fee = db.Column(db.Integer, nullable=False)
    id_url = db.Column(db.String(200), nullable=False)
    verified_sum = db.Column(db.Integer, default=0)
    verified_count = db.Column(db.Integer, default=0)
    
    # Relationship
    user: db.Mapped["User"] = db.relationship(back_populates="lawyer")
    user_id: db.Mapped[int] = db.mapped_column(db.ForeignKey("user.id"))
    lawyer_rating: db.Mapped[List["Rating"]] = db.relationship(back_populates="lawyer")
    lawyer_contact: db.Mapped[List["Contact"]] = db.relationship(back_populates="lawyer")