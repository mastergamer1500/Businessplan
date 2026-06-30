from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize the SQLAlchemy database instance
db = SQLAlchemy()

class User(db.Model):
    """Cabinet 1: Secure Identity Profiles"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    # Establish links to relational records
    telemetry_logs = db.relationship('FinancialLog', backref='owner', lazy=True)
    chat_logs = db.relationship('ChatHistory', backref='owner', lazy=True)

class FinancialLog(db.Model):
    """Cabinet 2: Historical Financial Vector Metrics"""
    __tablename__ = 'financial_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    revenue = db.Column(db.Float, nullable=False)
    expenses = db.Column(db.Float, nullable=False)
    cash_reserves = db.Column(db.Float, nullable=False)
    growth_rate = db.Column(db.Float, nullable=False)

class ChatHistory(db.Model):
    """Cabinet 3: Persistent Conversations Memory"""
    __tablename__ = 'chat_histories'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    sender = db.Column(db.String(20), nullable=False) # 'user' or 'copilot'
    message_text = db.Column(db.Text, nullable=False)