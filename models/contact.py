from flask_login import UserMixin
from . import db

class Contact(db.Model, UserMixin):
    __table_name__ = 'contact'
    id: db.Mapped[int] = db.mapped_column(primary_key=True)
    socials = db.Column(db.String(200), nullable=False)
    usernames = db.Column(db.String(200), default=False)
    
    # Relationship
    lawyer: db.Mapped["Lawyer"] = db.relationship(back_populates="lawyer_contact")
    lawyer_id: db.Mapped[int] = db.mapped_column(db.ForeignKey("lawyer.id"))