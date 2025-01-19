from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, BigInteger, Boolean, Table, Time, Float
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Association table for the many-to-many relationship between students and lessons
student_lessons = Table(
    'student_lessons', Base.metadata,
    Column('student_id', BigInteger, ForeignKey('students.id', ondelete="CASCADE"), primary_key=True),
    Column('lesson_id', Integer, ForeignKey('lessons.id', ondelete="CASCADE"), primary_key=True)
)

student_courses = Table(
    'student_courses', Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id', ondelete="CASCADE"), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id', ondelete="CASCADE"), primary_key=True)
)

teacher_courses = Table(
    'teacher_courses', Base.metadata,
    Column('teacher_id', Integer, ForeignKey('teachers.id', ondelete="CASCADE"), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id', ondelete="CASCADE"), primary_key=True)
)

class Student(Base):
    __tablename__ = 'students'
    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    email = Column(String)
    courses = relationship('Course', secondary=student_courses, back_populates="students", cascade="all, delete")
    lessons = relationship("Lesson", secondary=student_lessons, back_populates="students", cascade="all, delete")
    attendances = relationship("Attendance", back_populates="student", cascade="all, delete, delete-orphan")

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    short_name = Column(String)
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete, delete-orphan")
    teachers = relationship("Teacher", secondary=teacher_courses, back_populates="courses", cascade="all, delete")
    students = relationship('Student', secondary=student_courses, back_populates='courses', cascade="all, delete")

class Teacher(Base):
    __tablename__ = 'teachers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    lessons = relationship("Lesson", back_populates="teacher", cascade="all, delete, delete-orphan")
    courses = relationship("Course", secondary=teacher_courses, back_populates="teachers", cascade="all, delete")

class Classroom(Base):
    __tablename__ = 'classrooms'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    number = Column(String)
    lessons = relationship("Lesson", back_populates="classroom", cascade="all, delete, delete-orphan")

class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete="CASCADE"))
    teacher_id = Column(Integer, ForeignKey('teachers.id', ondelete="CASCADE"))
    classroom_id = Column(Integer, ForeignKey('classrooms.id', ondelete="CASCADE"))
    day_of_week = Column(String)
    start_time = Column(Time)
    finish_time = Column(Time)
    course = relationship("Course", back_populates="lessons")
    teacher = relationship("Teacher", back_populates="lessons")
    classroom = relationship("Classroom", back_populates="lessons")
    students = relationship("Student", secondary=student_lessons, back_populates="lessons")
    attendances = relationship("Attendance", back_populates="lesson", cascade="all, delete, delete-orphan")

class Attendance(Base):
    __tablename__ = 'attendances'
    id = Column(Integer, primary_key=True)
    student_id = Column(BigInteger, ForeignKey('students.id', ondelete="CASCADE"))
    lesson_id = Column(Integer, ForeignKey('lessons.id', ondelete="CASCADE"))
    week_number = Column(Integer)
    arrival_time = Column(DateTime)
    present = Column(Boolean, nullable=True)  # True for present, False for absent, NULL for not recorded
    student = relationship("Student", back_populates="attendances")
    lesson = relationship("Lesson", back_populates="attendances")
    
    
class Transaction(Base):
  __tablename__ = "transactions"

  id = Column(Integer, primary_key=True, index=True)
  amount = Column(Float)
  category = Column(String, index=True)
  description = Column(String, index=True)
  is_income = Column(Boolean) 
  date = Column(String)
  
class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True, index=True)
  email = Column(String, unique=True, index=True)  
  hashed_password = Column(String)
