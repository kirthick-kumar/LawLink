from flask_login import UserMixin
from . import db

class Rating(db.Model, UserMixin):
    __table_name__ = 'rating'
    id: db.Mapped[int] = db.mapped_column(primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    review = db.Column(db.String(200), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    rating_date = db.Column(db.String(20), nullable=False)

    # Relationship
    rating_author: db.Mapped["User"] = db.relationship(back_populates="rating_user")
    author_id: db.Mapped[int] = db.mapped_column(db.ForeignKey("user.id"))
    lawyer: db.Mapped["Lawyer"] = db.relationship(back_populates="lawyer_rating")
    lawyer_id: db.Mapped[int] = db.mapped_column(db.ForeignKey("lawyer.id"))