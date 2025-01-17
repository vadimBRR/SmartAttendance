from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from src.database.database_config import DatabaseConfig  # Ensure this import reflects your actual project structure
from src.database.models import Student, Teacher, Course, Lesson, Attendance, Classroom

from src.database.models import teacher_courses


class AttendanceManager:
    def __init__(self, db_config, classroom_name="Solaris", start_date=datetime(2023, 9, 1)):
        self.db_config = db_config  # DatabaseConfig instance
        self.classroom_name = classroom_name
        self.start_date = start_date

    def get_current_week(self, current_date=None):
        if current_date is None:
            current_date = datetime.now()
        delta = current_date.date() - self.start_date.date()
        if delta.days < 0:
            return 0  # Before the start date

        adjust_start = (7 - self.start_date.weekday()) % 7
        adjusted_start_date = self.start_date + timedelta(days=adjust_start)
        full_weeks = (current_date.date() - adjusted_start_date.date()).days // 7
        return full_weeks + 1

    def get_date_details(self, unix_timestamp):
        arrival_time = datetime.fromtimestamp(unix_timestamp)
        week_num = arrival_time.isocalendar()[1]
        week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        day_of_week = week_days[arrival_time.weekday()]
        return {
            'arrival_time': arrival_time,
            'week_num': week_num,
            'day_of_week': day_of_week
        }

    def get_students_by_lesson(self, lesson_id):
        session = self.db_config.Session()
        student_ids = []
        try:
            lesson = session.query(Lesson).filter(Lesson.id == lesson_id).first()
            if lesson:
                student_ids = [student.id for student in lesson.students]
            else:
                print(f"No lesson found with ID {lesson_id}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            session.close()
        return student_ids

    def get_student_name_by_id(self, student_id):
        session = self.db_config.Session()
        student_info = {"student_name": None, "student_surname": None}
        try:
            student = session.query(Student).filter(Student.id == student_id).first()
            if student:
                student_info["student_name"] = student.name
                student_info["student_surname"] = student.surname
            else:
                print(f"No student found with ID {student_id}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            session.close()
        return student_info

    def get_students_attendance_by_lesson(self, lesson_id):
        session = self.db_config.Session()
        try:
            # Fetch the lesson
            lesson = session.query(Lesson).filter(Lesson.id == lesson_id).first()
            if not lesson:
                print(f"No lesson found with ID {lesson_id}")
                return []

            # Get all students for the lesson
            students = lesson.students

            # Build the response with attendance
            students_data = []
            for student in students:
                # Fetch attendance records for the student in the specified lesson
                attendances = session.query(Attendance).filter(
                    Attendance.lesson_id == lesson_id,
                    Attendance.student_id == student.id
                ).all()

                # Collect attendance records as a list of dictionaries with present and arrival_time
                attendance_records = [
                    {"present": attendance.present, "arrival_time": attendance.arrival_time}
                    for attendance in attendances
                ]

                # Add student data to the result
                students_data.append({
                    "student_id": student.id,
                    "student_name": student.name,
                    "attendance": attendance_records
                })

            return {"students": students_data}

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return []
        finally:
            session.close()

    def get_all_attendances_by_lesson_student(self, lesson_id, student_id):
        session = self.db_config.Session()
        student_attendances = []
        try:
            student_attendances = session.query(Attendance).filter(Attendance.lesson_id == lesson_id).filter(Attendance.student_id == student_id).all()
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            session.close()
        return student_attendances

    def get_lesson_id_by_class_time(self, classroom_name, day_of_week, date_time):
        session = self.db_config.Session()
        lesson_id = None
        try:
            specific_time = date_time.time()
            lesson = session.query(Lesson.id).join(Classroom).filter(Classroom.name == classroom_name).filter(Lesson.day_of_week == day_of_week).filter(Lesson.start_time <= specific_time).filter(Lesson.finish_time >= specific_time).first()
            if lesson:
                lesson_id = lesson[0]
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            session.close()
        return lesson_id

    def add_attendance(self, student_id, lesson_id, week_number, arrival_time=None):
        if arrival_time is None:
            arrival_time = datetime.now()

        session = self.db_config.Session()  # Directly call Session
        try:
            attendance = Attendance(
                student_id=student_id,
                lesson_id=lesson_id,
                week_number=week_number,
                arrival_time=arrival_time,
                present=True
            )
            session.add(attendance)
            session.commit()
            print("Attendance recorded successfully.")
        except IntegrityError as e:
            print(f"Failed to record attendance: {e}")
            session.rollback()
        finally:
            session.close()

    def set_absence_for_null_records(self):
        session = self.db_config.Session()
        try:
            records_to_update = session.query(Attendance).filter(Attendance.present.is_(None)).all()
            for record in records_to_update:
                record.present = False
            session.commit()
            print(f"Updated {len(records_to_update)} attendance records to mark as absent.")
        except Exception as e:
            session.rollback()
            print(f"An error occurred: {str(e)}")
        finally:
            session.close()

    def add_attendance_by_student_and_time(self, student_id, timestamp):
        date = self.get_date_details(timestamp)
        week_num = date['week_num']
        arrival_time = date['arrival_time']
        day_of_week = date['day_of_week']
        lesson_id = self.get_lesson_id_by_class_time(self.classroom_name, day_of_week, arrival_time)
        self.add_attendance(student_id, lesson_id, week_num, arrival_time)

    def get_all_courses_for_teacher(self, teacher_id):
        session = self.db_config.Session()
        try:
            stmt = (
                select(Course.id, Course.name)
                .join(teacher_courses, teacher_courses.c.course_id == Course.id)
                .where(teacher_courses.c.teacher_id == teacher_id)
            )
            results = session.execute(stmt).fetchall()

            courses_dict = {row.id: row.name for row in results}
            return courses_dict
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return []
        finally:
            session.close()


    def get_all_lessons_by_course_teacher(self, course_id, teacher_id):
        session = self.db_config.Session()
        try:
            lessons = session.query(Lesson).filter(Lesson.course_id==course_id).filter(Lesson.teacher_id==teacher_id).all()
            return {
                lesson.id: {
                    "day_of_week": lesson.day_of_week,
                    "start_time": str(lesson.start_time),
                    "finish_time": str(lesson.finish_time)
                }
                for lesson in lessons
            }
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return []
        finally:
            session.close()

    def add_new_lesson(self, course_id, teacher_id, classroom_id, day_of_week, students_id: list,
                       start_time=None, finish_time=None):
        session = self.db_config.Session()
        try:
            # Use current time if no start_time is provided
            if not start_time:
                start_time = datetime.now().time()
            if not finish_time:
                finish_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes=5)).time()

            # Check for collisions
            conflicting_lessons = session.query(Lesson).filter(
                Lesson.day_of_week == day_of_week,
                (
                        (Lesson.start_time < finish_time) & (Lesson.finish_time > start_time)
                # Overlapping time condition
                ),
                (
                        (Lesson.teacher_id == teacher_id) |  # Same teacher
                        (Lesson.classroom_id == classroom_id)  # Same classroom
                )
            ).all()

            if conflicting_lessons:
                print(f"Cannot add lesson. Found {len(conflicting_lessons)} conflicting lesson(s):")
                for conflict in conflicting_lessons:
                    print(
                        f" - Conflict with Lesson ID {conflict.id}, Teacher ID {conflict.teacher_id}, Classroom ID {conflict.classroom_id}")
                return []

            # Create the new lesson
            lesson = Lesson(course_id=course_id, teacher_id=teacher_id, classroom_id=classroom_id,
                            day_of_week=day_of_week, start_time=start_time, finish_time=finish_time)

            # Assign students to the lesson
            for student_id in students_id:
                student = session.query(Student).filter_by(id=student_id).one_or_none()
                if student:
                    # Check if the student has a collision
                    student_conflicts = session.query(Lesson).filter(
                        Lesson.day_of_week == day_of_week,
                        (Lesson.start_time < finish_time) & (Lesson.finish_time > start_time),
                        Lesson.students.any(Student.id == student_id)
                    ).all()

                    if student_conflicts:
                        print(f"Student ID {student_id} has a schedule conflict. Skipping assignment.")
                        continue

                    student.lessons.append(lesson)

            # Add and commit the lesson
            session.add(lesson)

            session.commit()
            print("Lesson added successfully!")

        except Exception as e:
            session.rollback()
            print(f"An error occurred: {str(e)}")
            return []
        finally:
            session.close()

