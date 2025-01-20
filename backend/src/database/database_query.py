from datetime import datetime, time
from http.client import HTTPException
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.database.models import (Student, Teacher, Course, Lesson,
                                 Attendance, Classroom, student_courses, teacher_courses,
                                student_lessons)
from src.config_file import get_classroom_id

from src.utils import __is_valid_day_format
from datetime import datetime, timedelta


class AttendanceInfo(BaseModel):
    present: List[Optional[bool]]
    arrival_time: List[Optional[datetime]]

    class Config:
        arbitrary_types_allowed = True

AttendanceInfo.model_rebuild()


class StudentInfo(BaseModel):
    student_id: int
    name: str
    attendance: List[AttendanceInfo]


class LessonRequest(BaseModel):
    course_id: int
    students: List[StudentInfo]
    created_at: datetime
    day_of_week: str
    start_time: time
    finish_time: time
    teacher_id: int
    classroom_id: int

def __get_lesson_by_classroom_moment():
    pass


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

def delete_lesson_by_id(lesson_id: int, session = None):
    if not session:
        return

    session.query(Lesson).filter(Lesson.id == lesson_id).delete(synchronize_session='fetch')
    session.query(Attendance).filter(Attendance.lesson_id == lesson_id).delete(synchronize_session='fetch')
    session.query(student_lessons).filter(student_lessons.c.lesson_id == lesson_id).delete(synchronize_session='fetch')
    session.commit()

def get_lesson_collisions_in_classroom(lesson: Lesson, session = None):
    if session is None:
        return

    return session.query(Lesson).filter(
        Lesson.day_of_week == lesson.day_of_week,
        Lesson.classroom_id == lesson.classroom_id,
        (Lesson.start_time < lesson.finish_time) & (Lesson.finish_time > lesson.start_time),
    ).first()

def get_student_lessons_collision(lesson: Lesson, student: Student, session = None):
    if not session:
        return

    return session.query(Lesson).join(Lesson.students).filter(
        Lesson.day_of_week == lesson.day_of_week,
        Lesson.students.any(Student.id == student.student_id),
        (Lesson.start_time < lesson.finish_time) & (Lesson.finish_time > lesson.start_time),
    ).all()

def is_student_assigned_to_a_course(lesson: Lesson, student: Student, session = None):
    if not session:
        return

    return session.query(student_courses).filter(
        student_courses.c.course_id == lesson.course_id,
        student_courses.c.student_id == student.id
    ).first()

def is_student_assigned_to_a_lesson(lesson_id, student_id, session = None):
    if session is None:
        return
    students_lessons = get_students_lessons_t(student_id=student_id, session=session)
    lesson_ids = [lesson.id for lesson in students_lessons]
    if lesson_id in lesson_ids:
        return True
    return False
def assign_course_to_a_student(course_id: int, student_id: int, session = None):
    if not session:
        return

    session.execute(
        student_courses.insert().values(course_id=course_id, student_id=student_id)
    )

def get_course_by_id(course_id: int, session = None):
    if not session:
        return

    return session.query(Course).filter_by(id=course_id).first()

def get_classroom_by_id(classroom_id: int, session = None):
    if not session:
        return

    return session.query(Classroom).filter_by(id=classroom_id).first()

def __add_lesson(course_id: int, teacher_id: int, classroom_id: int, day_of_week: str,
                 start_time, finish_time, session = None):
    if not session:
        return
    try:
        lesson = Lesson(
            course_id=course_id,
            teacher_id=teacher_id,
            classroom_id=classroom_id,
            day_of_week=day_of_week,
            start_time=start_time,
            finish_time=finish_time
        )
        print("here")
        session.add(lesson)
        session.commit()

        return lesson

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pass
        # session.close()


def __add_students_to_lesson(lesson: Lesson, students_info: list, start_time, finish_time,
                             day_of_week: str, current_week: int,
                             session=None):
    if not session:
        return

    try:
        result = {
            "students_info": []
        }
        added_students = []
        for student_info in students_info:
            student = get_student_by_id(student_info.student_id, session=session)
            if student:
                student.lessons.append(lesson)
                if not is_student_assigned_to_a_course(lesson=lesson, student=student, session=session):
                    assign_course_to_a_student(course_id=lesson.course_id, student_id=student.id, session=session)

                # session.commit()
                added_students.append(student)

                attendance = __add_attendances_to_all_students(
                    lesson=lesson,
                    student=student,
                    attendance=student_info.attendance,
                    current_week=current_week,
                    start_time=start_time,
                    session=session
                )

                result["students_info"].append({
                    "id": student.id,
                    "name": student.name,
                    "email": student.email,
                    "attendance": attendance
                })

        session.commit()

        return result

    except HTTPException as e:
        session.rollback()
        raise e
    except Exception as e:
        session.rollback()
        # raise HTTPException(status_code=500, detail=str(e))
    finally:
        pass
        # session.close()


def __add_attendances_to_all_students(lesson: Lesson, student: Student,
                                      attendance: list[AttendanceInfo], current_week: int,
                                      start_time, session=None):
    if not session:
        return

    try:
        all_week_attendances = []
        start_datetime = datetime.combine(datetime.now(), start_time)
        attendance_week = attendance[0] if len(attendance) > 0 else None
        print(attendance_week)
        for week in range(1, 14):
            if attendance_week and week <= current_week:
                try:
                    if week == current_week:
                        present = (
                            attendance_week.present[week - 1]
                            if week - 1 < len(attendance_week.present)
                            else None
                        )
                        arrival_time = (
                            attendance_week.arrival_time[week - 1].replace(tzinfo=None)
                            if week - 1 < len(attendance_week.arrival_time) and attendance_week.arrival_time[
                                week - 1] is not None
                            else datetime.now() if present and week - 1 < len(attendance_week.arrival_time)
                            else None
                        )
                    else:
                        present = (
                            attendance_week.present[week - 1]
                            if week - 1 < len(attendance_week.present)
                            else False
                        )
                        arrival_time = (
                            attendance_week.arrival_time[week - 1].replace(tzinfo=None)
                            if week - 1 < len(attendance_week.arrival_time) and attendance_week.arrival_time[
                                week - 1] is not None
                            else None
                        )
                except IndexError:
                    present = None
                    arrival_time = None
            else:
                arrival_time = None
                present = None

            week_attendance = Attendance(
                student=student,
                lesson=lesson,
                week_number=week,
                arrival_time=arrival_time,
                present=present
            )
            print(f"Week {week}: Present={present}, Arrival={arrival_time}")
            all_week_attendances.append(week_attendance)

        session.add_all(all_week_attendances)
        session.commit()

        return all_week_attendances

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def __validate_attendance(attendance: AttendanceInfo, current_week: int):
    if len(attendance.present) < current_week:
        raise ValueError(f"Insufficient 'present' data. Expected at least {current_week} entries.")
    if len(attendance.arrival_time) < current_week:
        raise ValueError(f"Insufficient 'arrival_time' data. Expected at least {current_week} entries.")


def __validate_student(student: StudentInfo, lesson_request: LessonRequest, session: Session):
    if not get_student_by_id(id=student.student_id, session=session):
        raise ValueError(f"Student ID {student.student_id} does not exist in the database.")

    name_parts = student.name.split()
    if len(name_parts) < 2:
        raise ValueError(f"Invalid student name format: {student.name}. Expected 'name surname'.")

    for attendance in student.attendance:
        __validate_attendance(attendance, current_week=len(attendance.present))

    if get_student_lessons_collision(lesson=lesson_request, student=student, session=session):
        raise ValueError(
            f"Student ID {student.student_id} has a scheduling conflict with existing lessons.")


def __validate_lesson(lesson_request: LessonRequest, session: Session):
    if not get_course_by_id(course_id=lesson_request.course_id, session=session):
        raise ValueError(f"Course ID {lesson_request.course_id} does not exist in the database.")

    if not get_teacher_by_id(id=lesson_request.teacher_id, session=session):
        raise ValueError(f"Teacher ID {lesson_request.teacher_id} does not exist in the database.")

    if not get_classroom_by_id(classroom_id=lesson_request.classroom_id, session=session):
        raise ValueError(f"Classroom ID {lesson_request.classroom_id} does not exist in the database.")

    if lesson_request.created_at > datetime.now():
        raise ValueError("The 'created_at' timestamp cannot be in the future.")

    if lesson_request.start_time >= lesson_request.finish_time:
        raise ValueError("Start time must be earlier than finish time.")

    if not isinstance(lesson_request.start_time, time) or not isinstance(lesson_request.finish_time, time):
        raise ValueError("Invalid start_time or finish_time. They must be valid time objects.")

    if not __is_valid_day_format(lesson_request.day_of_week):
        raise ValueError(f"'{lesson_request.day_of_week}' is not a valid day format.")

    if get_lesson_collisions_in_classroom(lesson_request, session):
        raise ValueError(
            f"Schedule collision detected in the classroom .")


def __validate_lesson_request(lesson_request: LessonRequest, session: Session):
    try:
        __validate_lesson(lesson_request, session)

        for student in lesson_request.students:
            __validate_student(student, lesson_request, session)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_lesson_by_id(lesson_id: int, session = None):
    if session is None:
        return

    return session.query(Lesson).filter(Lesson.id == lesson_id).first()

def get_student_attendance_by_week(lesson_id: int, week_num: int, student_id: int, session = None):
    if session is None:
        return
    return session.query(Attendance) \
            .filter(Attendance.lesson_id == lesson_id) \
            .filter(Attendance.week_number == week_num) \
            .filter(Attendance.student_id == student_id) \
            .first()

def get_all_student_attendance(lesson_id:int, student_id: int, session = None):
    if session is None:
        return
    return session.query(Attendance).filter(
            Attendance.lesson_id == lesson_id,
            Attendance.student_id == student_id
        ).order_by(Attendance.week_number.asc()).all()

def report_attendance(attendance: Attendance, present: bool, arrival_time, session = None):
    if session is None:
        return
    attendance.present = present
    attendance.arrival_time = arrival_time

def get_students_lessons_t(student_id: int, session = None):
    if session is None:
        return
    return session.query(Lesson).filter(
            Lesson.id.in_(
                session.query(student_lessons.c.lesson_id).filter(student_lessons.c.student_id == student_id)
            )
        ).all()

def get_teacher_lessons(teacher_id: int, session = None):
    if session == None:
        return
    return session.query(Lesson).filter(
            Lesson.teacher_id == teacher_id
        ).all()

def get_all_students_assigned_to_course(course_id: int, session = None):
    if not session:
        return

    return session.query(student_courses.c.student_id).filter(student_courses.c.course_id == course_id)

def get_all_students_not_assigned_to_course(course_id: int, session = None):
    if not session:
        return
    return session.query(Student).filter(
        ~Student.id.in_(
            get_all_students_assigned_to_course(course_id=course_id, session=session)
        )
    ).all()

def get_teacher_courses(teacher_id: int, session = None):
    if not session:
        return
    return session.query(Course).join(
        teacher_courses,
        Course.id == teacher_courses.c.course_id
    ).filter(
        teacher_courses.c.teacher_id == teacher_id
    ).all()

def get_lesson_by_classroom_time(arrival_time, day_of_week: str, session=None):
    if not session:
        return None

    if isinstance(arrival_time, datetime):
        pass
    elif isinstance(arrival_time, time):
        today = datetime.today().date()
        arrival_time = datetime.combine(today, arrival_time)
    else:
        arrival_time = datetime.strptime(arrival_time, "%Y-%m-%d %H:%M:%S")


    today = datetime.today().date()

    lessons = session.query(Lesson).filter(
        Lesson.classroom_id == get_classroom_id(),
        Lesson.day_of_week == day_of_week,
    ).all()

    if not lessons:
        return None

    for lesson in lessons:
        start_time = lesson.start_time
        finish_time = lesson.finish_time

        lesson_start_datetime = datetime.combine(today, start_time)
        lesson_finish_datetime = datetime.combine(today, finish_time)

        lesson_start_datetime_minus_10 = lesson_start_datetime - timedelta(minutes=10)

        if lesson_start_datetime_minus_10 <= arrival_time <= lesson_finish_datetime:
            return lesson

    return None


def get_lesson_by_course_id(course_id: int, session = None):
    if not session:
        return
    return session.query(Lesson).filter(Lesson.course_id == course_id).first()