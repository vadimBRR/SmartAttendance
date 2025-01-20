import logging

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta, date
import pytz
from dotenv import load_dotenv, set_key
import os

from sqlalchemy.orm import Session
from src.database.models import Lesson, Attendance, Classroom

from src.config_file import set_mode


class LessonScheduler:
    def __init__(self, session: Session, handle_activity, timezone_str='Europe/Bratislava', env_path='local.env'):
        self.session = session
        self.timezone = pytz.timezone(timezone_str)
        self.scheduler = BackgroundScheduler(timezone=self.timezone)
        self.env_path = env_path
        self.handle_activity = handle_activity
        self.current_lesson_id = None
        self.time_before_lesson = 10


        # Load the .env file
        load_dotenv(self.env_path)

        # Load or initialize the start date from the .env file
        self.start_date = self.get_start_date_from_env()

        # Calculate the current week number from the start date
        self.current_week_num = self.calculate_week_number()
        logging.info(f"Starting scheduler for classroom ID: {self.current_lesson_id}")

    def start(self, classroom_id):
        # Schedule a job to check for the next lesso
        logging.info(f"Starting scheduler for classroom ID: {classroom_id}")
        self.scheduler.add_job(self.check_and_schedule_next_lesson, 'interval', minutes=1, args=[classroom_id])

        # Schedule a job to recalculate the week number every Sunday at midnight
        self.scheduler.add_job(self.update_week_number, 'cron', day_of_week='sun', hour=23, minute=59)

        # Update the .env file with the current week number at program start
        self.update_week_number()

        self.scheduler.start()
        logging.info("Scheduler started.")

    def shutdown(self):
        self.scheduler.shutdown()

    def get_start_date_from_env(self):
        start_date_str = os.getenv('START_DATE')
        if not start_date_str:
            # If no start date exists in .env, initialize it with today's date
            start_date = datetime.now(self.timezone).date()
            set_key(self.env_path, 'START_DATE', start_date.isoformat())
            print(f"START_DATE not found in .env. Initialized to {start_date.isoformat()}.")
        else:
            # Parse the existing start date
            start_date = datetime.fromisoformat(start_date_str).date()
        return start_date

    def calculate_week_number(self):
        today = datetime.now(self.timezone).date()
        delta = today - self.start_date
        week_num = delta.days // 7 + 1  # Week number starts from 1
        return week_num

    def update_week_number(self):
        self.current_week_num = self.calculate_week_number()
        print(f"Updating week number to: {self.current_week_num}")

        try:
            # Write the updated week number back to the .env file
            set_key(self.env_path, 'CURRENT_WEEK_NUM', str(self.current_week_num))
            print(f"Week number updated to {self.current_week_num} in .env file.")
        except Exception as e:
            print(f"Error updating week number in .env file: {e}")

    def get_next_lesson(self, classroom_id):
        current_time = datetime.now(self.timezone).time()
        today = datetime.now(self.timezone).strftime('%A')
        print(f"Fetching next lesson for classroom ID {classroom_id}. Current time: {current_time}, Day: {today}")

        next_lesson = (
            self.session.query(Lesson)
            .filter(
                Lesson.classroom_id == classroom_id,
                Lesson.day_of_week == today,
                Lesson.start_time >= current_time
            )
            .order_by(Lesson.start_time)
            .first()
        )

        if next_lesson:
            print(f"Next lesson found: Lesson ID {next_lesson.id}, Start Time: {next_lesson.start_time}")
        else:
            print("No upcoming lessons found.")
        return next_lesson

    def check_and_schedule_next_lesson(self, classroom_id):
        next_lesson = self.get_next_lesson(classroom_id)

        if not next_lesson:
            print(f"No more lessons for classroom ID {classroom_id} today.")
            return

        if self.current_lesson_id == next_lesson.id:
            print(f"Lesson ID {next_lesson.id} is already scheduled. Skipping.")
            return  # Avoid re-scheduling the same lesson

        # Schedule jobs for the next lesson
        print(f"Scheduling notifications and absence marking for lesson ID {next_lesson.id}.")
        self.schedule_lesson_jobs(next_lesson)
        self.current_lesson_id = next_lesson.id  # Update the current lesson tracker

    def schedule_lesson_jobs(self, lesson):
        print(f"Scheduling jobs for lesson ID {lesson.id}.")
        if lesson.course_id == 404:
            self.__set_time_before_lesson(0)
            print("TEST!!!")
            set_mode("TEST")
        else:
            set_mode("NORMAL")
            time_before = self.__check_how_much_time_before_lesson(lesson)
            if time_before <= timedelta(minutes=10):
                self.__set_time_before_lesson(time_before)
            else:
                self.__set_time_before_lesson(10)



        lesson_start_datetime = self.timezone.localize(datetime.combine(date.today(), lesson.start_time))
        start_notification_time = lesson_start_datetime - timedelta(minutes=self.time_before_lesson)
        # start_notification_time = lesson_start_datetime

        if datetime.now(self.timezone) < start_notification_time:
            self.scheduler.add_job(
                self.send_notification, 'date', run_date=start_notification_time, args=[lesson, 'start']
            )

        lesson_end_datetime = self.timezone.localize(datetime.combine(date.today(), lesson.finish_time))
        self.scheduler.add_job(
            self.send_notification, 'date', run_date=lesson_end_datetime, args=[lesson, 'end']
        )
        self.scheduler.add_job(
            self.mark_absences_for_lesson, 'date', run_date=lesson_end_datetime, args=[lesson.id]
        )

    def send_notification(self, lesson, action='start'):
        if action == 'start':
            self.handle_activity("wake_up")
        elif action == 'end':
            self.handle_activity("sleep")
        else:
            print("Unknown action specified for notification.")


    def mark_absences_for_lesson(self, lesson_id):
        print(f"Marking absences for lesson ID {lesson_id} in week {self.current_week_num}.")

        unrecorded_attendances = self.session.query(Attendance).filter(
            Attendance.lesson_id == lesson_id,
            Attendance.present.is_(None),
            Attendance.week_number == self.current_week_num
        ).all()

        for attendance in unrecorded_attendances:
            attendance.present = False  # Mark as absent
            print(f"Marked student {attendance.student_id} as absent for lesson {lesson_id}.")

        try:
            self.session.commit()
        except Exception as e:
            print(f"Error committing changes to the database: {e}")
            self.session.rollback()

    def __set_time_before_lesson(self, time: int):
        self.time_before_lesson = time


    def __check_how_much_time_before_lesson(self, lesson):
        now = datetime.now()
        lesson_start_time = datetime.combine(now.date(), lesson.start_time)
        time_difference = lesson_start_time - now
        return time_difference if time_difference > timedelta(0) else -1

