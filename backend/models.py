from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    usn = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    marks = db.relationship('Mark', backref='student', lazy=True)
    rewards = db.relationship('Reward', backref='student', lazy=True)

    def __repr__(self):
        return f"Student('{self.name}', '{self.usn}')"

class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject_code = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    subjects = db.relationship('Subject', backref='faculty', lazy=True)

    def __repr__(self):
        return f"Faculty('{self.name}', '{self.subject_code}')"

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    class_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Department('{self.name}', '{self.class_name}')"

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    marks = db.relationship('Mark', backref='subject', lazy=True)
    rewards = db.relationship('Reward', backref='subject', lazy=True)
    applicable_classes = db.Column(db.String(200), nullable=True)  # comma-separated list

    def __repr__(self):
        return f"Subject('{self.name}', '{self.code}')"

class Mark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    internal_number = db.Column(db.Integer, nullable=False)  # 1, 2, or 3
    marks = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (f"Mark(Student: '{self.student_id}', Subject: '{self.subject_id}', "
                f"Internal: '{self.internal_number}', Marks: '{self.marks}')")

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    internal_number = db.Column(db.Integer, nullable=False)
    reward_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    encrypted_message = db.Column(db.Text, nullable=True)
    encrypted_aes_key = db.Column(db.Text, nullable=True)
    nonce = db.Column(db.Text)
    tag = db.Column(db.Text)

    def __repr__(self):
        return f"Reward(Student: '{self.student_id}', Type: '{self.reward_type}')"

class MotivationMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    encrypted_message = db.Column(db.LargeBinary, nullable=False)
    encrypted_key = db.Column(db.LargeBinary, nullable=False)
    iv = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"MotivationMessage(Student: '{self.student_id}', Subject: '{self.subject_id}')"

class StudentKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), unique=True, nullable=False)
    public_key = db.Column(db.Text, nullable=False)
    private_key = db.Column(db.Text, nullable=False)
