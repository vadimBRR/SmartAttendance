from datetime import datetime, timedelta
from http.client import HTTPException

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from src.database.database_config import DatabaseConfig  # Ensure this import reflects your actual project structure
from src.database.models import Student, Teacher, Course, Lesson, Attendance, Classroom

from src.database.models import teacher_courses

from src.database.models import student_lessons


def get_lesson_attendances(lesson_id: int, session = None):
    try:
        lesson = session.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            raise HTTPException(status_code=400, detail=f"No lesson found with ID {lesson_id}")
            # return []
        course = session.query(Course).filter(Course.id == lesson.course_id).first()
        if not course:
            raise HTTPException(status_code=400, detail=f"No course was found with lesson ID {lesson_id}")
            # return []
        students = lesson.students
        students_data = []
        for student in students:
            attendances = session.query(Attendance).filter(
                Attendance.lesson_id == lesson_id,
                Attendance.student_id == student.id
            ).order_by(Attendance.week_number.asc()).all()

            attendance_records = [
                {"present": attendance.present, "arrival_time": attendance.arrival_time}
                for attendance in attendances
            ]

            students_data.append({
                "student_id": f"{student.id}",
                "student_name": student.name,
                "course_name": course.name,
                "short_course_name": course.short_name,
                "attendance": attendance_records
            })

        return {"students": students_data}

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return []
    finally:
        session.close()

async def get_lessons_attendance_for_student(lesson_id: int, student_id: int, session = None):
    try:
        lesson = session.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            raise HTTPException(status_code=400, detail=f"No lesson found with ID {lesson_id}")

        student = session.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=400, detail=f"No such studentwith ID {student_id} in db.")

        if not __is_student_have_such_lesson(student_id=student_id, lesson_id=lesson_id):
            raise HTTPException(status_code=400, detail=f"Student with ID {student_id} does not have lesson with ID {lesson_id}.")


        attendances = session.query(Attendance).filter(
            Attendance.lesson_id == lesson_id,
            Attendance.student_id == student_id
        ).order_by(Attendance.week_number.asc()).all()

        course = session.query(Course).filter(Course.id == lesson.course_id).first()

        return [
                {"present": attendance.present,
                 "arrival_time": attendance.arrival_time,
                 "short_course_name": course.short_name,
                 "course_name": course.name
                 }
                for attendance in attendances
            ]

    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
    finally:
        session.close()

def __is_student_have_such_lesson(lesson_id, student_id, session = None):
    return session.query(student_lessons).filter(
        student_lessons.c.lesson_id == lesson_id,
        student_lessons.c.student_id == student_id
    ).first()

def __get_lesson_by_lcassroom_moment():
    pass

# def __validate_attendance(attendance: AttendanceInfo, current_week: int):
#     if len(attendance.present) < current_week:
#         raise ValueError(f"Insufficient 'present' data. Expected at least {current_week} entries.")
#     if len(attendance.arrival_time) < current_week:
#         raise ValueError(f"Insufficient 'arrival_time' data. Expected at least {current_week} entries.")
#
#
# def __validate_student(student: StudentInfo, lesson_request: LessonRequest, session: Session):
#     db_student = session.query(Student).filter_by(id=student.student_id).first()
#     if not db_student:
#         raise ValueError(f"Student ID {student.student_id} does not exist in the database.")
#
#     name_parts = student.name.split()
#     if len(name_parts) < 2:
#         raise ValueError(f"Invalid student name format: {student.name}. Expected 'name surname'.")
#
#     for attendance in student.attendance:
#         __validate_attendance(attendance, current_week=len(attendance.present))
#
#     student_collisions = session.query(Lesson).join(Lesson.students).filter(
#         Lesson.day_of_week == lesson_request.day_of_week,
#         Lesson.students.any(Student.id == student.student_id),  # Student is in the lesson
#         (Lesson.start_time < lesson_request.finish_time) & (Lesson.finish_time > lesson_request.start_time),
#     ).all()
#     if student_collisions:
#         raise ValueError(
#             f"Student ID {student.student_id} has a scheduling conflict with {len(student_collisions)} existing lessons.")
#
#
# def __validate_lesson(lesson_request: LessonRequest, session: Session):
#     if not session.query(Course).filter_by(id=lesson_request.course_id).first():
#         raise ValueError(f"Course ID {lesson_request.course_id} does not exist in the database.")
#
#     if not session.query(Teacher).filter_by(id=lesson_request.teacher_id).first():
#         raise ValueError(f"Teacher ID {lesson_request.teacher_id} does not exist in the database.")
#
#     if not session.query(Classroom).filter_by(id=lesson_request.classroom_id).first():
#         raise ValueError(f"Classroom ID {lesson_request.classroom_id} does not exist in the database.")
#
#     if lesson_request.created_at > datetime.now():
#         raise ValueError("The 'created_at' timestamp cannot be in the future.")
#
#     if lesson_request.start_time >= lesson_request.finish_time:
#         raise ValueError("Start time must be earlier than finish time.")
#
#     if not __is_valid_day_format(lesson_request.day_of_week):
#         raise ValueError(f"'{lesson_request.day_of_week}' is not a valid day format.")
#
#     classroom_collisions = session.query(Lesson).filter(
#         Lesson.day_of_week == lesson_request.day_of_week,
#         Lesson.classroom_id == lesson_request.classroom_id,
#         (Lesson.start_time < lesson_request.finish_time) & (Lesson.finish_time > lesson_request.start_time),
#     ).all()
#     if classroom_collisions:
#         raise ValueError(
#             f"Schedule collision detected in the classroom with {len(classroom_collisions)} existing lessons.")
#
# def __validate_lesson_request(lesson_request: LessonRequest, session: Session):
#     try:
#         __validate_lesson(lesson_request, session)
#
#         for student in lesson_request.students:
#             __validate_student(student, lesson_request, session)
#
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))

def get_classroom_by_name(classroom_id: int, session = None):
    if not session:
        return

    return session.query(Classroom).filter(Classroom.id == classroom_id).first()

def get_all_classrooms(session = None):
    if not session:
        return
    return session.query(Classroom).all()

def get_classroom_name(classroom_id: int, session = None):
    if not session:
        return
    return session.query(Classroom.name).filter(Classroom.id == classroom_id).first()

def get_teacher_by_email(email: str, session = None):
    if not session:
        return
    return session.query(Teacher).filter(Teacher.email == email).first()

def get_teacher_by_id(id: int, session = None):
    if not session:
        return
    return session.query(Teacher).filter(Teacher.id == id).first()


def get_student_by_email(email: str, session = None):
    if not session:
        return
    return session.query(Student).filter(Student.email == email).first()

def get_student_by_id(id: int, session = None):
    if not session:
        return
    return session.query(Student).filter(Student.id == id).first()