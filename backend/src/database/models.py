from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, BigInteger, Boolean, Table, Time
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Association table for the many-to-many relationship between students and lessons
student_lessons = Table(
    'student_lessons', Base.metadata,
    Column('student_id', BigInteger, ForeignKey('students.id'), primary_key=True),
    Column('lesson_id', Integer, ForeignKey('lessons.id'), primary_key=True)
)

student_courses = Table(
'student_courses', Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True)
)

# Association table for the many-to-many relationship between teachers and courses
teacher_courses = Table(
    'teacher_courses', Base.metadata,
    Column('teacher_id', Integer, ForeignKey('teachers.id'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True)
)


class Student(Base):
    __tablename__ = 'students'
    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    email = Column(String)
    courses = relationship('Course', secondary=student_courses, back_populates="students")
    lessons = relationship("Lesson", secondary=student_lessons, back_populates="students")
    attendances = relationship("Attendance", back_populates="student")


class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    short_name = Column(String)
    lessons = relationship("Lesson", back_populates="course")
    teachers = relationship("Teacher", secondary=teacher_courses, back_populates="courses")
    students = relationship('Student', secondary=student_courses, back_populates='courses')


class Teacher(Base):
    __tablename__ = 'teachers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    # short_course_day = Column(String)
    lessons = relationship("Lesson", back_populates="teacher")
    courses = relationship("Course", secondary=teacher_courses, back_populates="teachers")


class Classroom(Base):
    __tablename__ = 'classrooms'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    number = Column(String)
    lessons = relationship("Lesson", back_populates="classroom")


class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    classroom_id = Column(Integer, ForeignKey('classrooms.id'))
    day_of_week = Column(String)
    start_time = Column(Time)
    finish_time = Column(Time)
    course = relationship("Course", back_populates="lessons")
    teacher = relationship("Teacher", back_populates="lessons")
    classroom = relationship("Classroom", back_populates="lessons")
    students = relationship("Student", secondary=student_lessons, back_populates="lessons")
    attendances = relationship("Attendance", back_populates="lesson")


class Attendance(Base):
    __tablename__ = 'attendances'
    id = Column(Integer, primary_key=True)
    student_id = Column(BigInteger, ForeignKey('students.id'))
    lesson_id = Column(Integer, ForeignKey('lessons.id'))
    week_number = Column(Integer)
    arrival_time = Column(DateTime)
    present = Column(Boolean, nullable=True)  # True for present, False for absent, NULL for not recorded
    student = relationship("Student", back_populates="attendances")
    lesson = relationship("Lesson", back_populates="attendances")

