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
        database_url = os.getenv('DATABASE_URL', 'sqlite:///src/database/uni_attendance.db')
        db_folder = os.path.dirname(database_url.replace('sqlite:///', ''))
        if not os.path.exists(db_folder):
            os.makedirs(db_folder)
        self.engine = create_engine(database_url, echo=echo_flag, connect_args={"check_same_thread": False})
        self.Session = sessionmaker(bind=self.engine)

    def init_db(self):
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        return self.Session()