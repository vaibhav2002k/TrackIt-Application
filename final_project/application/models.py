from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=True)
    trackers = db.relationship('Tracker', backref='user', lazy=True)

    def __repr__(self):
        return f'User: {self.username}'

class Tracker(db.Model):
    __tablename__ = 'tracker'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String(1000))
    tracker_type = db.Column(db.String, nullable=False)
    settings = db.Column(db.String, default=None)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    logs = db.relationship('Log', backref='tracker', lazy=True)

    def __repr__(self):
        return f'Tracker: {self.name}'


class Log(db.Model):
    __tablename__ = 'log'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    tracker_id = db.Column(db.Integer, db.ForeignKey('tracker.id', ondelete="CASCADE"), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    value = db.Column(db.String, nullable=False)
    note = db.Column(db.String(1000))

    def __repr__(self):
        return f'Tracker Id: {self.tracker_id}, time: {self.timestamp}'