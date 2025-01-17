from fastapi import FastAPI, Depends
from pydantic import BaseModel
from src.database.database_query import AttendanceManager
from src.database.database_config import DatabaseConfig
from src.database.models import Lesson, Student, Attendance
from sqlalchemy.orm import Session
from datetime import time, datetime, timedelta
from http.client import HTTPException
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

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

db_config = DatabaseConfig()
db_config.init_db()
# db = db_config.populate_database()
manager = AttendanceManager(db_config)
class IdentifierPayload(BaseModel):
    id: int
    dt: int

@app.post("/notifications/")
async def receive_attendance(payload: IdentifierPayload):
    print(f"Adding id={payload.id} to database with arriving timestamp={payload.id}")
    manager.add_attendance_by_student_and_time(student_id=payload.id, timestamp=payload.dt)

@app.get("/courses/{teacher_id}")
async def get_courses(teacher_id: int):
    return manager.get_all_courses_for_teacher(teacher_id)

@app.get("/lessons/{courses_id}/{teacher_id}")
async def get_lessons(courses_id: int, teacher_id: int):
    return manager.get_all_lessons_by_course_teacher(course_id=courses_id, teacher_id=teacher_id)

@app.get("teacher_{teacher_id}/course_{course_id}/add/lesson/")

@app.get("/lessons{lesson_id}/attendance")
async def get_lessons_attendance(lesson_id: int):
    return manager.get_students_attendance_by_lesson(lesson_id=lesson_id)





# Dependency to get the database session
def get_db():
    session = db_config.Session()
    try:
        yield session
    finally:
        session.close()

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
    attendance_manager: AttendanceManager = Depends(get_attendance_manager)
):
    return attendance_manager.get_all_courses_for_teacher(teacher_id)

@app.get("/lessons/{course_id}/{teacher_id}")
async def get_lessons(
    course_id: int,
    teacher_id: int,
    attendance_manager: AttendanceManager = Depends(get_attendance_manager)
):
    return attendance_manager.get_all_lessons_by_course_teacher(course_id, teacher_id)

# @app.get("/lessons/{lesson_id}/attendance")
# async def get_lesson_attendance(
#     lesson_id: int,
#     attendance_manager: AttendanceManager = Depends(get_attendance_manager)
# ):
#     return attendance_manager.get_students_attendance_by_lesson(lesson_id)

@app.post("/lessons/lesson_{lesson_id}/attendance/{week_number}/{student_id}")
async def post_lesson_attendance(
    lesson_id: int,
    week_number: int,
    student_id: int,
    attendance_manager: AttendanceManager = Depends(get_attendance_manager)
):
    """
    Add attendance for a specific lesson, week, and student.
    """
    try:
        manager.add_attendance(lesson_id=lesson_id, week_number=week_number, student_id=student_id)
        return {"status": "attendance added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class LessonRequest(BaseModel):
    course_id: int
    teacher_id: int
    classroom_id: int
    day_of_week: str
    students_id: List[int]
    start_time: Optional[time] = None
    finish_time: Optional[time] = None

@app.post("/add_lesson/")
async def add_lesson(lesson_request: LessonRequest):
    session = db_config.Session()
    try:
        # Default times if not provided
        start_time = lesson_request.start_time or datetime.now().time()
        finish_time = lesson_request.finish_time or (datetime.combine(datetime.today(), start_time) + timedelta(minutes=1)).time()

        # Check for collisions (teacher and classroom)
        conflicting_lessons = session.query(Lesson).filter(
            Lesson.day_of_week == lesson_request.day_of_week,
            (Lesson.start_time < finish_time) & (Lesson.finish_time > start_time),
            (Lesson.teacher_id == lesson_request.teacher_id) | (Lesson.classroom_id == lesson_request.classroom_id)
        ).all()

        if conflicting_lessons:
            raise HTTPException(status_code=400, detail=f"Lesson conflicts with {len(conflicting_lessons)} existing lessons.")

        # Create the new lesson
        lesson = Lesson(
            course_id=lesson_request.course_id,
            teacher_id=lesson_request.teacher_id,
            classroom_id=lesson_request.classroom_id,
            day_of_week=lesson_request.day_of_week,
            start_time=start_time,
            finish_time=finish_time
        )
        session.add(lesson)

        # Add students to the lesson and create attendance records
        all_week_attendances = []
        for student_id in lesson_request.students_id:
            student = session.query(Student).filter_by(id=student_id).one_or_none()
            if student:
                # Check for student conflicts
                student_conflicts = session.query(Lesson).filter(
                    Lesson.day_of_week == lesson_request.day_of_week,
                    (Lesson.start_time < finish_time) & (Lesson.finish_time > start_time),
                    Lesson.students.any(Student.id == student_id)
                ).all()

                if student_conflicts:
                    print(f"Student ID {student_id} has a schedule conflict. Skipping assignment.")
                    continue

                # Assign student to the lesson
                student.lessons.append(lesson)

                # Create attendance records for this student
                for week in range(1, 14):  # Loop through weeks 1 to 13
                    attendance = Attendance(
                        student=student,
                        lesson=lesson,
                        week_number=week,
                        arrival_time=None,  # Default value, can be updated later
                        present=None  # Default value, can be updated later
                    )
                    all_week_attendances.append(attendance)

        # Add attendance records to the session
        session.add_all(all_week_attendances)
        session.commit()

        return {"message": "Lesson and attendance added successfully!", "lesson_id": lesson.id}

    except HTTPException as e:
        session.rollback()
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        session.close()

