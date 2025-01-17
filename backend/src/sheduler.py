from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.database.models import Lesson, Attendance, Classroom


class LessonScheduler:
    def __init__(self, session, timezone_str='Europe/Bratislava'):
        self.session = session
        self.timezone = pytz.timezone(timezone_str)
        self.scheduler = BackgroundScheduler(timezone=self.timezone)
        self.current_lesson_id = None  # Track the last scheduled lesson

    def start(self, classroom_id):
        # Periodically check and schedule the next lesson every minute
        self.scheduler.add_job(self.check_and_schedule_next_lesson, 'interval', minutes=1, args=[classroom_id])
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown()

    def get_next_lesson(self, classroom_id):
        """
        Get the next lesson for the current day in the specified classroom.
        """
        current_time = datetime.now(self.timezone).time()
        today = datetime.now(self.timezone).strftime('%A')

        next_lesson = (
            self.session.query(Lesson)
            .filter(
                Lesson.classroom_id == classroom_id,
                Lesson.day_of_week == today,
                Lesson.start_time > current_time
            )
            .order_by(Lesson.start_time)
            .first()
        )
        return next_lesson

    def check_and_schedule_next_lesson(self, classroom_id):
        """
        Periodically checks for the next lesson and schedules jobs if not already scheduled.
        """
        next_lesson = self.get_next_lesson(classroom_id)

        if not next_lesson:
            print(f"No more lessons for classroom ID {classroom_id} today.")
            return

        if self.current_lesson_id == next_lesson.id:
            print(f"Lesson ID {next_lesson.id} is already scheduled.")
            return  # Avoid re-scheduling the same lesson

        # Schedule jobs for the next lesson
        print(f"Scheduling notifications and absence marking for lesson ID {next_lesson.id}.")
        self.schedule_lesson_jobs(next_lesson)
        self.current_lesson_id = next_lesson.id  # Update the current lesson tracker

    def schedule_lesson_jobs(self, lesson):
        """
        Schedules notifications and absence marking for the given lesson.
        """
        print(f"Lesson ID {lesson.id} is")
        lesson_start_datetime = datetime.combine(datetime.date.today(), lesson.start_time)
        start_notification_time = lesson_start_datetime - timedelta(minutes=10)

        # Schedule start notification
        if datetime.now(self.timezone) < start_notification_time:
            self.scheduler.add_job(
                self.send_notification, 'date', run_date=start_notification_time, args=[lesson, 'start']
            )

        # Schedule end notification and absence marking at the lesson's finish time
        lesson_end_datetime = datetime.combine(datetime.date.today(), lesson.finish_time)
        self.scheduler.add_job(
            self.send_notification, 'date', run_date=lesson_end_datetime, args=[lesson, 'end']
        )
        self.scheduler.add_job(
            self.mark_absences_for_lesson, 'date', run_date=lesson_end_datetime, args=[lesson.id]
        )

    def send_notification(self, lesson, action='start'):
        """
        Sends notifications for lessons.
        """
        if action == 'start':
            print(
                f"Sending start notification for lesson {lesson.course.name} at {lesson.start_time} in {lesson.classroom.name}."
            )
        elif action == 'end':
            print(
                f"Sending end notification for lesson {lesson.course.name} at {lesson.finish_time} in {lesson.classroom.name}."
            )
        else:
            print("Unknown action specified for notification.")

    def mark_absences_for_lesson(self, lesson_id):
        """
        Marks students as absent for a specific lesson after it has ended.
        """
        print(f"Marking absences for lesson ID {lesson_id} at {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S')}.")

        # Fetch attendance records for this lesson where attendance has not been recorded
        unrecorded_attendances = self.session.query(Attendance).filter(
            Attendance.lesson_id == lesson_id,
            Attendance.present.is_(None)  # None indicates attendance has not been recorded
        ).all()

        # Mark absent for all unrecorded attendances
        for attendance in unrecorded_attendances:
            attendance.present = False  # Mark as absent
            print(f"Marked student {attendance.student_id} as absent for lesson {lesson_id}.")

        # Commit changes to the database
        try:
            self.session.commit()
        except Exception as e:
            print(f"Error committing changes to the database: {e}")
            self.session.rollback()

    def lesson_added_callback(self, classroom_id):
        """
        Callback to be triggered when a new lesson is added to the system.
        """
        print(f"New lesson added for classroom ID {classroom_id}. Re-evaluating next lesson scheduling...")
        self.check_and_schedule_next_lesson(classroom_id)
