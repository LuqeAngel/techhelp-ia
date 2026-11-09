from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user') # 'user' o 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Suscripción
    subscription_tier = db.Column(db.String(20), default='free') # 'free' o 'pro'
    subscription_status = db.Column(db.String(50), default='inactive') # 'active', 'inactive', 'canceled'
    stripe_customer_id = db.Column(db.String(120), nullable=True)
    stripe_subscription_id = db.Column(db.String(120), nullable=True)
    
    # Control de uso
    daily_queries_count = db.Column(db.Integer, default=0)
    last_query_date = db.Column(db.Date, default=date.today)

    # Relaciones
    conversations = db.relationship('Conversation', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_pro(self):
        return self.subscription_tier == 'pro' and self.subscription_status == 'active'

    def check_and_reset_daily_limit(self):
        today = date.today()
        if self.last_query_date != today:
            self.daily_queries_count = 0
            self.last_query_date = today

    def can_chat(self, free_limit=5):
        if self.is_pro() or self.is_admin():
            return True, "Ilimitado"
        self.check_and_reset_daily_limit()
        if self.daily_queries_count < free_limit:
            remaining = free_limit - self.daily_queries_count
            return True, f"{remaining} consultas restantes hoy"
        return False, "Has alcanzado el límite diario del plan Free. Actualiza a Pro para consultas ilimitadas."

    def record_chat_query(self):
        self.check_and_reset_daily_limit()
        self.daily_queries_count += 1

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'subscription_tier': self.subscription_tier,
            'subscription_status': self.subscription_status,
            'is_pro': self.is_pro(),
            'daily_queries_count': self.daily_queries_count,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class Conversation(db.Model):
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), default='Nueva incidencia técnica')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan', order_by='Message.created_at')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M'),
            'message_count': len(self.messages)
        }


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False)
    sender = db.Column(db.String(20), nullable=False) # 'user' o 'assistant'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'sender': self.sender,
            'content': self.content,
            'created_at': self.created_at.strftime('%H:%M - %d/%m/%Y')
        }
