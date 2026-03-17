from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    fullname      = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role          = db.Column(db.String(20), default='teacher')
    avatar        = db.Column(db.String(200), default='default.png')
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

class Student(db.Model):
    __tablename__ = 'students'
    id            = db.Column(db.Integer, primary_key=True)
    fullname      = db.Column(db.String(100), nullable=False)
    dob           = db.Column(db.Date, nullable=True)
    gender        = db.Column(db.String(10))
    diagnosis     = db.Column(db.String(200))
    parent_name   = db.Column(db.String(100))
    parent_phone  = db.Column(db.String(20))
    parent_email  = db.Column(db.String(120))
    address       = db.Column(db.String(300))
    notes         = db.Column(db.Text)
    status        = db.Column(db.String(20), default='active')
    enrolled_at   = db.Column(db.DateTime, default=datetime.utcnow)
    teacher_id    = db.Column(db.Integer, db.ForeignKey('users.id'))
    teacher       = db.relationship('User', backref='students')
    progress_logs = db.relationship('Progress', backref='student', lazy=True)

class Post(db.Model):
    __tablename__ = 'posts'
    id            = db.Column(db.Integer, primary_key=True)
    title         = db.Column(db.String(300), nullable=False)
    slug          = db.Column(db.String(300), unique=True)
    content       = db.Column(db.Text, nullable=False)
    summary       = db.Column(db.String(500))
    thumbnail     = db.Column(db.String(300))
    category      = db.Column(db.String(50))
    is_published  = db.Column(db.Boolean, default=False)
    views         = db.Column(db.Integer, default=0)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow)
    author_id     = db.Column(db.Integer, db.ForeignKey('users.id'))
    author        = db.relationship('User', backref='posts')

class Event(db.Model):
    __tablename__ = 'events'
    id            = db.Column(db.Integer, primary_key=True)
    title         = db.Column(db.String(200), nullable=False)
    description   = db.Column(db.Text)
    location      = db.Column(db.String(300))
    start_date    = db.Column(db.DateTime, nullable=False)
    end_date      = db.Column(db.DateTime)
    max_slots     = db.Column(db.Integer, default=0)
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    created_by    = db.Column(db.Integer, db.ForeignKey('users.id'))

class Registration(db.Model):
    __tablename__ = 'registrations'
    id             = db.Column(db.Integer, primary_key=True)
    parent_name    = db.Column(db.String(100), nullable=False)
    parent_phone   = db.Column(db.String(20), nullable=False)
    parent_email   = db.Column(db.String(120))
    child_name     = db.Column(db.String(100), nullable=False)
    child_age      = db.Column(db.String(20))
    concern        = db.Column(db.Text)
    preferred_date = db.Column(db.String(100))
    status         = db.Column(db.String(20), default='pending')
    notes          = db.Column(db.Text)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

class Consultation(db.Model):
    __tablename__ = 'consultations'
    id         = db.Column(db.Integer, primary_key=True)
    fullname   = db.Column(db.String(100), nullable=False)
    phone      = db.Column(db.String(20), nullable=False)
    email      = db.Column(db.String(120))
    service    = db.Column(db.String(100))
    message    = db.Column(db.Text)
    status     = db.Column(db.String(20), default='new')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Progress(db.Model):
    __tablename__ = 'progress'
    id           = db.Column(db.Integer, primary_key=True)
    student_id   = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    teacher_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date         = db.Column(db.Date, default=datetime.utcnow)
    session_type = db.Column(db.String(100))
    goals        = db.Column(db.Text)
    achievements = db.Column(db.Text)
    rating       = db.Column(db.Integer)
    next_steps   = db.Column(db.Text)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    teacher      = db.relationship('User', backref='progress_logs')

class FAQ(db.Model):
    __tablename__ = 'faqs'
    id        = db.Column(db.Integer, primary_key=True)
    question  = db.Column(db.String(500), nullable=False)
    answer    = db.Column(db.Text, nullable=False)
    category  = db.Column(db.String(50))
    order     = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

class Service(db.Model):
    __tablename__ = 'services'
    id          = db.Column(db.Integer, primary_key=True)
    slug        = db.Column(db.String(100), unique=True, nullable=False)
    name        = db.Column(db.String(200), nullable=False)
    icon        = db.Column(db.String(20), default='🧩')
    color       = db.Column(db.String(30), default='#1558B0')
    short_desc  = db.Column(db.String(400))
    intro       = db.Column(db.Text)
    content     = db.Column(db.Text)
    benefits    = db.Column(db.Text)   # JSON list
    target_age  = db.Column(db.String(100))
    duration    = db.Column(db.String(150))
    thumbnail   = db.Column(db.String(300))
    video_url   = db.Column(db.String(300))
    gallery     = db.Column(db.Text)   # JSON list
    order       = db.Column(db.Integer, default=0)
    is_active   = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow)
