from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class School(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)


class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    school = db.relationship('School', backref=db.backref('grades', lazy=False))


class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey('grade.id'), nullable=False)
    grade = db.relationship('Grade', backref=db.backref('classes', lazy=False))


t_stu_has_hobby = db.Table(
    'stu_has_hobby',
    db.Column('hobby_id', db.ForeignKey('hobby.id'), primary_key=True, nullable=False, index=True),
    db.Column('student_id', db.ForeignKey('student.id'), primary_key=True, nullable=False, index=True),
)


class Hobby(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    class_id = db.Column(db.Integer, nullable=False)
    grade_id = db.Column(db.Integer, nullable=False)
    school_id = db.Column(db.Integer, nullable=False)

    hobbies = db.relationship('Hobby', secondary='stu_has_hobby', backref='students')
