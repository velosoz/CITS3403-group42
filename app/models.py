# app/models.py
from flask_login import UserMixin
from .extensions import db  # ✅ fixed import

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    entries = db.relationship('StudyEntry', backref='user', lazy=True)


from datetime import date

class StudyEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    unit = db.Column(db.String(100), nullable=False)
    hours = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    mood = db.Column(db.String(50))  # Optional
