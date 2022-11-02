from .database import db

class User(db.Model):
    __tablename__='User'
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)

class Tracker(db.Model):
    __tablename__='Tracker'
    tracker_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("User.user_id"),nullable=False)
    tracker_name = db.Column(db.String, nullable = False)
    tracker_description = db.Column(db.String)
    tracker_type = db.Column(db.String, nullable = False)
    settings = db.Column(db.String)
class Log(db.Model):
    __tablename__='Log'
    log_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("User.user_id"), nullable=False)
    tracker_id = db.Column(db.Integer, db.ForeignKey("Tracker.tracker_id"), nullable=False)
    time_stamp = db.Column(db.String, nullable=False)
    value = db.Column(db.String, nullable=False)
    note = db.Column(db.String)