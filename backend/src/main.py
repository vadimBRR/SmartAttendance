import json
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from src.database.database_query import AttendanceManager
from src.database.database_config import DatabaseConfig
from datetime import time, datetime, timedelta
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Generator
from src.database.models import (student_courses, student_lessons,
                                 teacher_courses, Course, Teacher, Classroom,
                                 Lesson, Student, Attendance)



app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def load_config():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    return config


config = load_config()
START_DATE = config['START_DATE']

db_config = DatabaseConfig(echo_flag=False)
db_config.init_db()
# db = db_config.populate_database()
manager = AttendanceManager(db_config)

if START_DATE:
    START_DATE = datetime.fromisoformat(START_DATE)
else:
    START_DATE = datetime.now()
    print(f"START_DATE not found. Initialized to {START_DATE.isoformat()}.")


def get_db() -> Generator[Session, None, None]:
    session = db_config.Session()
    try:
        yield session
    finally:
        session.close()


@app.get("/lessons{lesson_id}/attendance")
async def get_lessons_attendance(lesson_id: int, session: Session = Depends(get_db)):
    try:
        lesson = session.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            print(f"No lesson found with ID {lesson_id}")
            return []
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


# Dependency to get the database session

# Dependency to get AttendanceManager
def get_attendance_manager(db: Session = Depends(get_db)):
    return AttendanceManager(db_config=db_config)


# Models
class IdentifierPayload(BaseModel):
    id: int
    dt: int


@app.post("/notifications/")
async def receive_attendance(
        payload: IdentifierPayload,
        attendance_manager: AttendanceManager = Depends(get_attendance_manager)
):
    print(f"Adding id={payload.id} to database with arriving timestamp={payload.dt}")
    attendance_manager.add_attendance_by_student_and_time(
        student_id=payload.id, timestamp=payload.dt
    )
    return {"status": "success", "student_id": payload.id}


@app.get("/courses/{teacher_id}")
async def get_courses(
        teacher_id: int,
        session: Session = Depends(get_db)
):
    courses = session.query(Course).join(
        teacher_courses,
        Course.id == teacher_courses.c.course_id
    ).filter(
        teacher_courses.c.teacher_id == teacher_id
    ).all()

    courses_info = [
        {"id": course.id, "name": course.name, "short_name": course.short_name} for course in courses
    ]

    return courses_info


@app.get("/lessons/{course_id}/{teacher_id}")
async def get_groups(
        course_id: int,
        teacher_id: int,
        session: Session = Depends(get_db)
):
    try:
        lessons = session.query(Lesson).filter(Lesson.course_id == course_id).filter(
            Lesson.teacher_id == teacher_id).all()
        course = session.query(Course).filter(Course.id == course_id).first()
        return {
            lesson.id: {
                "course_name": course.name,
                "short_course_name": course.short_name,
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

@app.post("/lessons/lesson_{lesson_id}/attendance/{week_number}/{student_id}")
async def post_lesson_attendance(
        lesson_id: int,
        week_number: int,
        student_id: int,
):
    try:
        manager.add_attendance(lesson_id=lesson_id, week_number=week_number, student_id=student_id)
        return {"status": "attendance added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


@app.post("/add_lesson/")
async def add_lesson(lesson_request: LessonRequest, session: Session = Depends(get_db)):
    try:
        if not __is_valid_day_format(lesson_request.day_of_week):
            raise HTTPException(status_code=400,
                                detail=f"'{lesson_request.day_of_week}' is not a valid day format.")

        start_time = lesson_request.start_time or datetime.now().time()
        finish_time = lesson_request.finish_time or (
                datetime.combine(datetime.today(), start_time) + timedelta(minutes=1)).time()
        current_week = __get_current_week(lesson_request.created_at)

        # add lesson to db
        lesson = __add_lesson(course_id=lesson_request.course_id,
                              teacher_id=lesson_request.teacher_id,
                              classroom_id=lesson_request.classroom_id,
                              day_of_week=lesson_request.day_of_week,
                              start_time=start_time,
                              finish_time=finish_time,
                              session=session)

        # assign students to the lesson
        added_students_attendance = __add_students_to_lesson(lesson=lesson, students_info=lesson_request.students,
                                                  start_time=start_time, finish_time=finish_time,
                                                  day_of_week=lesson_request.day_of_week, current_week=current_week, session=session)

        return {
            "message": "Lesson created and students' attendance successfully added.",
            "lesson": {
                "id": lesson.id,
                "course_id": lesson.course_id,
                "teacher_id": lesson.teacher_id,
                "classroom_id": lesson.classroom_id,
                "day_of_week": lesson.day_of_week,
                "start_time": lesson.start_time.isoformat(),
                "finish_time": lesson.finish_time.isoformat(),
            },
            "students": added_students_attendance,
            "current_week": current_week,
        }

    except HTTPException as e:
        session.rollback()
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pass
        # session.close()


def __add_lesson(course_id: int, teacher_id: int, classroom_id: int, day_of_week: str,
                 start_time, finish_time, session: Session = Depends(get_db)):
    try:
        start_time = start_time.replace(
            tzinfo=None) if start_time and start_time.tzinfo else datetime.now().time()
        finish_time = finish_time.replace(
            tzinfo=None) if finish_time and finish_time.tzinfo else (
                datetime.combine(datetime.today(), start_time) + timedelta(minutes=1)).time()

        conflicting_lessons = session.query(Lesson).filter(
            Lesson.day_of_week == day_of_week,
            (Lesson.start_time < finish_time) & (Lesson.finish_time > start_time),
            (Lesson.teacher_id == teacher_id) | (Lesson.classroom_id == classroom_id)
        ).all()

        if conflicting_lessons:
            raise HTTPException(status_code=400,
                                detail=f"Lesson conflicts with {len(conflicting_lessons)} existing lessons.")

        # Create the new lesson
        lesson = Lesson(
            course_id=course_id,
            teacher_id=teacher_id,
            classroom_id=classroom_id,
            day_of_week=day_of_week,
            start_time=start_time,
            finish_time=finish_time
        )

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
                             session: Session = Depends(get_db)):
    try:
        result = {
            "students_info": []
        }
        added_students = []
        for student_info in students_info:
            student = session.query(Student).filter_by(id=student_info.student_id).one_or_none()
            if student:
                # Check for student conflicts
                student_conflicts = session.query(Lesson).filter(
                    Lesson.day_of_week == day_of_week,
                    (Lesson.start_time < finish_time) & (Lesson.finish_time > start_time),
                    Lesson.students.any(Student.id == student_info.student_id)
                ).all()

                if student_conflicts:
                    raise HTTPException(status_code=400,
                                        detail=f"Student ID {student_info.student_id} has a schedule conflict. Skipping assignment.")

                student.lessons.append(lesson)
                added_students.append(student)
                session.commit()

                print(student_info.attendance)

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
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pass
        # session.close()


def __add_attendances_to_all_students(lesson: Lesson, student: Student,
                                      attendance: list[AttendanceInfo], current_week: int,
                                      start_time, session: Session):
    try:
        all_week_attendances = []
        start_datetime = datetime.combine(datetime.now(), start_time)
        attendance_week = attendance[0] if len(attendance) > 0 else None

        for week in range(1, 14):
            if attendance_week and week <= current_week:
                if week == current_week:
                    present = (
                        attendance_week.present[week - 1]
                        if len(attendance_week.present) > week - 1
                        else None
                    )
                    arrival_time = (
                        attendance_week.arrival_time[week - 1].replace(tzinfo=None)
                        if present and len(attendance_week.arrival_time) > week - 1
                        else (datetime.now() if present else None)
                    )
                else:
                    present = (
                        attendance_week.present[week - 1]
                        if len(attendance_week.present) > week - 1
                        else False
                    )
                    arrival_time = (
                        attendance_week.arrival_time[week - 1].replace(tzinfo=None)
                        if len(attendance_week.arrival_time) > week - 1 and present
                        else (start_datetime if present else None)
                    )
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


@app.get("/create_group")
async def get_all_students_without_group(course_id: int, session: Session = Depends(get_db)):
    query = session.query(Student).join(
        student_courses,
        Student.id == student_courses.c.student_id
    ).filter(
        student_courses.c.course_id == course_id
    )

    subquery = session.query(Lesson.id).filter(Lesson.course_id == course_id).subquery()
    students = query.outerjoin(
        student_lessons,
        (Student.id == student_lessons.c.student_id) & (student_lessons.c.lesson_id.in_(subquery))
    ).filter(
        student_lessons.c.lesson_id.is_(None)
    ).all()

    students_info = [
        {"id": student.id, "name": student.name, "email": student.email}
        for student in students
    ]

    return students_info


# from datetime import datetime, timedelta
def __get_current_week(current_date=None):
    if current_date is None:
        current_date = datetime.now()

    return current_date.isocalendar()[1] - START_DATE.isocalendar()[1] + 1


def __is_valid_day_format(day_str):
    valid_days = [
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ]

    return day_str in valid_days


def __validate_attendance(attendance: AttendanceInfo, current_week: int):
    if len(attendance.present) < current_week:
        raise ValueError(f"Insufficient 'present' data. Expected at least {current_week} entries.")
    if len(attendance.arrival_time) < current_week:
        raise ValueError(f"Insufficient 'arrival_time' data. Expected at least {current_week} entries.")


def __validate_student(student: StudentInfo, lesson_request: LessonRequest, session: Session):
    db_student = session.query(Student).filter_by(id=student.student_id).first()
    if not db_student:
        raise ValueError(f"Student ID {student.student_id} does not exist in the database.")

    name_parts = student.name.split()
    if len(name_parts) < 2:
        raise ValueError(f"Invalid student name format: {student.name}. Expected 'name surname'.")

    for attendance in student.attendance:
        __validate_attendance(attendance, current_week=len(attendance.present))

    student_collisions = session.query(Lesson).join(Lesson.students).filter(
        Lesson.day_of_week == lesson_request.day_of_week,
        Lesson.students.any(Student.id == student.student_id),  # Student is in the lesson
        (Lesson.start_time < lesson_request.finish_time) & (Lesson.finish_time > lesson_request.start_time),
    ).all()
    if student_collisions:
        raise ValueError(
            f"Student ID {student.student_id} has a scheduling conflict with {len(student_collisions)} existing lessons.")


def __validate_lesson(lesson_request: LessonRequest, session: Session):
    if not session.query(Course).filter_by(id=lesson_request.course_id).first():
        raise ValueError(f"Course ID {lesson_request.course_id} does not exist in the database.")

    if not session.query(Teacher).filter_by(id=lesson_request.teacher_id).first():
        raise ValueError(f"Teacher ID {lesson_request.teacher_id} does not exist in the database.")

    if not session.query(Classroom).filter_by(id=lesson_request.classroom_id).first():
        raise ValueError(f"Classroom ID {lesson_request.classroom_id} does not exist in the database.")

    if lesson_request.created_at > datetime.now():
        raise ValueError("The 'created_at' timestamp cannot be in the future.")

    if lesson_request.start_time >= lesson_request.finish_time:
        raise ValueError("Start time must be earlier than finish time.")

    if not __is_valid_day_format(lesson_request.created_at):
        raise ValueError(f"'{lesson_request.day_of_week}' is not a valid day format.")

    classroom_collisions = session.query(Lesson).filter(
        Lesson.day_of_week == lesson_request.day_of_week,
        Lesson.classroom_id == lesson_request.classroom_id,
        (Lesson.start_time < lesson_request.finish_time) & (Lesson.finish_time > lesson_request.start_time),
    ).all()
    if classroom_collisions:
        raise ValueError(
            f"Schedule collision detected in the classroom with {len(classroom_collisions)} existing lessons.")


def __validate_lesson_request(lesson_request: LessonRequest, session: Session):
    try:
        __validate_lesson(lesson_request, session)

        for student in lesson_request.students:
            __validate_student(student, lesson_request, session)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
