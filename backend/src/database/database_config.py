import os
from datetime import datetime, time

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, Teacher, Course, Classroom, Lesson, Student, Attendance

load_dotenv('../../local.env')

class DatabaseConfig:
    def __init__(self, echo_flag=True):
        # Get the base directory of the `src` folder
        database_url = os.getenv('DATABASE_URL', 'sqlite:///src/database/uni_attendance.db')
        db_folder = os.path.dirname(database_url.replace('sqlite:///', ''))
        if not os.path.exists(db_folder):
            os.makedirs(db_folder)
        self.engine = create_engine(database_url, echo=echo_flag, connect_args={"check_same_thread": False})
        self.Session = sessionmaker(bind=self.engine)

        # self.engine = create_engine(database_url, echo=True)
        # self.Session = sessionmaker(bind=self.engine)

        # base_dir = os.path.dirname(os.path.abspath(__file__))  # Current file's directory
        # root_dir = os.path.join(base_dir, "../")  # Navigate to the root directory
        # db_path = os.path.join(root_dir, 'uni_attendance.db')  # Database file path at root
        # db_url = f"sqlite:///{db_path}"  # SQLite URL

        # Create the engine and session factory
        # self.engine = create_engine(db_url, echo=echo_flag)

    def init_db(self):
        Base.metadata.create_all(bind=self.engine)
        # self.populate_database()

    # def populate_database(self):
    #     """Populate the database with sample data."""
    #     session = self.Session()
    #     try:
    #         # Clear existing data
    #         session.query(Attendance).delete()
    #         session.query(Lesson).delete()
    #         session.query(Classroom).delete()
    #         session.query(Student).delete()
    #         session.query(Teacher).delete()
    #         session.query(Course).delete()
    #
    #         # Add classrooms
    #         classroom1 = Classroom(name="Room A", number="101")
    #         classroom2 = Classroom(name="Room B", number="102")
    #         session.add_all([classroom1, classroom2])
    #
    #         # Add courses
    #         course1 = Course(name="Math 101", short_name="MATH101")
    #         course2 = Course(name="History 202", short_name="HIST202")
    #         session.add_all([course1, course2])
    #
    #         # Add teachers
    #         teacher1 = Teacher(name="Alice Smith", email="alice@example.com")
    #         teacher2 = Teacher(name="Bob Johnson", email="bob@example.com")
    #         teacher1.courses.append(course1)
    #         teacher2.courses.append(course2)
    #         session.add_all([teacher1, teacher2])
    #
    #         # Add students
    #         student1 = Student(id= 1, name="John Doe", email="john@example.com")
    #         student2 = Student(id = 2, name="Jane Roe", email="jane@example.com")
    #         student1.courses.extend([course1, course2])
    #         student2.courses.append(course1)
    #         session.add_all([student1, student2])
    #
    #         # Add lessons
    #         lesson1 = Lesson(
    #             course=course1,
    #             teacher=teacher1,
    #             classroom=classroom1,
    #             day_of_week="Monday",
    #             start_time=time(9, 0),
    #             finish_time=time(10, 0)
    #         )
    #         lesson2 = Lesson(
    #             course=course2,
    #             teacher=teacher2,
    #             classroom=classroom2,
    #             day_of_week="Tuesday",
    #             start_time=time(10, 30),
    #             finish_time=time(11, 30)
    #         )
    #         session.add_all([lesson1, lesson2])
    #
    #         # Link students to lessons
    #         lesson1.students.append(student1)
    #         lesson2.students.extend([student1, student2])
    #
    #         # Add attendance records
    #         attendance1 = Attendance(
    #             student=student1,
    #             lesson=lesson1,
    #             week_number=1,
    #             arrival_time=datetime(2025, 1, 15, 8, 55),
    #             present=True
    #         )
    #         attendance2 = Attendance(
    #             student=student2,
    #             lesson=lesson2,
    #             week_number=1,
    #             arrival_time=datetime(2025, 1, 16, 10, 25),
    #             present=True
    #         )
    #         session.add_all([attendance1, attendance2])
    #
    #         session.commit()
    #         print("Database populated successfully!")
    #     except Exception as e:
    #         session.rollback()
    #         print(f"An error occurred: {e}")
    #     finally:
    #         session.close()

