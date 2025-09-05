# importing necessary libraries

from app.extensions import db
from flask_security import UserMixin, RoleMixin
import uuid

# the names of models and their attributes are self-explanatory
# constraints and datatypes are mentioned

# association table, as required by flask_security for many-to-many relationship
roles_users = db.Table('roles_users', db.Column('user_id', db.Integer(), db.ForeignKey('user.id')), db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique = True, nullable = False)
    password = db.Column(db.String(120), nullable = False)
    email = db.Column(db.String, unique = True, nullable = False)
    active = db.Column(db.Boolean, default = True, nullable = False)
    roles = db.relationship('Role', secondary = roles_users, backref = db.backref('users', lazy = 'dynamic'))
    fs_uniquifier = db.Column(db.String(64), unique = True, nullable = False, default = lambda: uuid.uuid4().hex)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    description = db.Column(db.Text)

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'))
    name = db.Column(db.String(100), nullable = False)
    description = db.Column(db.Text)
    date_of_quiz = db.Column(db.DateTime)
    time_duration = db.Column(db.Time) # hh:mm

class Question(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    question_text = db.Column(db.Text, nullable = False)
    option1 = db.Column(db.String(100), nullable = False)
    option2 = db.Column(db.String(100), nullable = False)
    option3 = db.Column(db.String(100), nullable = False)
    option4 = db.Column(db.String(100), nullable = False)
    correct_option = db.Column(db.Integer, nullable = False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    total_score = db.Column(db.Integer, nullable = False)
    time_of_attempt = db.Column(db.DateTime, nullable = False)

class Response(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    marked = db.Column(db.Integer, nullable = False)
    correct = db.Column(db.Boolean, nullable = False)