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
