from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    display_name = db.Column(db.String(128))
    role = db.Column(db.String(32), default='player')  # player or admin
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Challenge(db.Model):
    __tablename__ = 'challenges'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    category = db.Column(db.String(32))  # crypto, web, forensics
    difficulty = db.Column(db.String(16))  # easy, medium, hard
    description = db.Column(db.Text)
    flag_hash = db.Column(db.String(256), nullable=False)
    points = db.Column(db.Integer, default=100)
    docker_service = db.Column(db.String(64), nullable=True)

class Solve(db.Model):
    __tablename__ = 'solves'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    points_awarded = db.Column(db.Integer)

class Hint(db.Model):
    __tablename__ = 'hints'
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    hint_order = db.Column(db.Integer)
    cost = db.Column(db.Integer, default=10)
    content = db.Column(db.Text)

class HintRequest(db.Model):
    __tablename__ = 'hint_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    ai_response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
