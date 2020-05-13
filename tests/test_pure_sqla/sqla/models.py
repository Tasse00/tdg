from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()


class School(Base):
    __tablename__ = 'schools'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), unique=True, nullable=False)


class Grade(Base):
    __tablename__ = 'grades'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), unique=True, nullable=False)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    school = relationship('School', backref=backref('grades', lazy=False))


#

class Class(Base):
    __tablename__ = 'classes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), unique=True, nullable=False)
    grade_id = Column(Integer, ForeignKey('grades.id'), nullable=False)
    grade = relationship('Grade', backref=backref('classes', lazy=False))


t_stu_has_hobby = Table(
    'stu_has_hobby',
    Base.metadata,
    Column('hobby_id', ForeignKey('hobbies.id'), primary_key=True, nullable=False, index=True),
    Column('student_id', ForeignKey('students.id'), primary_key=True, nullable=False, index=True),
)


class Hobby(Base):
    __tablename__ = "hobbies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    class_id = Column(Integer, nullable=False)
    grade_id = Column(Integer, nullable=False)
    school_id = Column(Integer, nullable=False)

    hobbies = relationship('Hobby', secondary='stu_has_hobby', backref='students')
