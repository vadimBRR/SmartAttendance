import json
import logging
from functools import partial
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from src.database.database_config import DatabaseConfig
from datetime import datetime, timedelta, timezone, date
from jose import jwt, JWTError
from typing import List, Annotated
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from src.database.models import (student_courses, student_lessons,
                                 teacher_courses, Course, Teacher, Classroom,
                                 Lesson, Student, Attendance, Classroom, User as UserM ,Transaction as TransactionM)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from src.config_file import *
from src.utils import __get_current_week, get_date_details
# from src.config_file import update_config_file, read_config_key
# from src.config_file import get_classroom_id, set_classroom
# from src.database.database_query import (get_all_classrooms, get_classroom_name, get_teacher_by_email, \
#                                          get_student_by_email, delete_lesson_by_id, get_lesson_collisions_in_classroom, get_student_lessons_collision, \
#                                          get_student_by_id, is_student_assigned_to_a_course, assign_course_to_a_student, get_teacher_by_id, get_course_by_id, \
#                                          get_classroom_by_id, __add_students_to_lesson, __add_lesson, __validate_lesson_request, LessonRequest, \
#                                          get_lesson_by_id, get_student_attendance_by_week, report_attendance, \
#                                          get_all_students_not_assigned_to_course, get_teacher_lessons, get_teacher_courses, \
#                                          get_lesson_by_classroom_time, get_all_student_attendance, is_student_assigned_to_a_lesson, get_classroom_by_name,)
from src.database.database_query import *
from src.utils import __get_current_week, get_date_details
from src.config_file import set_classroom
from src.sheduler import LessonScheduler
from src.notifier import handle_activity
from src.database.database_query import get_lesson_by_course_id
from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger
from src.notifier import fast_mqtt
from src.database.database_query import __validate_lesson_request
from src.database.database_query import __add_lesson, __add_students_to_lesson
from src.config_file import set_mode
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from src.database.database_query import get_students_lessons

scheduler = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global scheduler

    try:
        await fast_mqtt.mqtt_startup()
        logging.info("Startup event triggered.")

        # Initialize the scheduler
        scheduler = LessonScheduler(
            session=db_config.get_session(),
            handle_activity=partial(handle_activity, fast_mqtt)
        )
        scheduler.start(classroom_id=1)
        logging.info("Scheduler started successfully.")

        yield
    finally:
        if fast_mqtt:
            await fast_mqtt.mqtt_shutdown()
            logging.info("Shutdown event triggered.")

        if scheduler:
            scheduler.shutdown()
            logging.info("Scheduler shut down successfully.")


app = FastAPI(lifespan=lifespan)
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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

load_dotenv('local.env')

db_config = DatabaseConfig(echo_flag=False)
db_config.init_db()

def get_db() -> Session:
    session = db_config.get_session()
    try:
        yield session
    finally:
        session.close()




@app.get("/lessons{lesson_id}/attendance")
async def get_lessons_attendance(lesson_id: int, session: Session = Depends(get_db)):
    try:
        lesson = get_lesson_by_id(lesson_id=lesson_id, session=session)
        if not lesson:
            raise HTTPException(status_code=400, detail=f"No lesson found with ID {lesson_id}")

        course = get_course_by_id(course_id = lesson.course_id, session=session)
        if not course:
            raise HTTPException(status_code=400, detail=f"No course was found with lesson ID {lesson_id}")
        students = lesson.students
        students_data = []
        for student in students:
            attendances = get_all_student_attendance(lesson_id=lesson_id, student_id=student.id, session=session)
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


@app.get('/get_test_lesson')
async def get_test_lesson(session: Session = Depends(get_db)):
    course_id = 404
    # set_mode('TEST')
    course = get_course_by_id(course_id=course_id, session=session)
    if not course:
        raise HTTPException(status_code=400, detail=f"No course was found with lesson ID {course.id}")
    lesson = get_lesson_by_course_id(course_id=course_id, session=session)
    if not lesson:
        raise HTTPException(status_code=400, detail=f"No lesson found with ID {lesson.id}")
    students = lesson.students
    students_data = []
    for student in students:
        attendances = get_all_student_attendance(lesson_id=lesson.id, student_id=student.id, session=session)
        attendance_records = [
            {"present": attendance.present, "arrival_time": attendance.arrival_time}
            for attendance in attendances
        ]

        students_data.append({
            "student_id": f"{student.id}",
            "student_name": student.name,
            "course_name": course.name,
            "short_course_name": course.short_name,
            "lesson_id": lesson.id,
            "attendance": attendance_records,
            "start_time": lesson.start_time,
            "finish_time": lesson.finish_time
        })

    return {"students": students_data}

@app.get("/delete_test_lesson")
async def delete_test_lesson(session: Session = Depends(get_db)):
    course_id = 404
    set_mode('NORMAL')
    course = get_course_by_id(course_id=course_id, session=session)
    if not course:
        raise HTTPException(status_code=400, detail=f"No course was found with lesson ID {lesson.id}")
    lesson = get_lesson_by_course_id(course_id=course_id, session=session)
    if not lesson:
        raise HTTPException(status_code=400, detail=f"No lesson found with ID {lesson.id}")
    delete_lesson_by_id(lesson_id=lesson.id, session=session)
    session.query(student_courses).filter(student_courses.c.course_id == course_id).delete(synchronize_session='fetch')
    session.commit()
    scheduler.cancel_or_finish_lesson(lesson_id=lesson.id, finish_immediately=True)


@app.get("/lessons{lesson_id}/attendance/{student_id}")
async def get_lessons_attendance_for_student(lesson_id: int, student_id: int, session: Session = Depends(get_db)):
    try:
        if not get_lesson_by_id(lesson_id=lesson_id, session=session):
            raise HTTPException(status_code=400, detail=f"No lesson found with ID {lesson_id}")
        if not get_student_by_id(id=student_id, session=session):
            raise HTTPException(status_code=400, detail=f"No such student with ID {student_id} in db.")

        if not is_student_assigned_to_a_lesson(student_id=student_id, lesson_id=lesson_id, session=session):
            raise HTTPException(status_code=400, detail=f"Student with ID {student_id} does not have lesson with ID {lesson_id}.")

        attendances = get_all_student_attendance(lesson_id=lesson_id, student_id=student_id, session=session)
        course = get_course_by_id(lesson_id, session=session)

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


class IdentifierPayload(BaseModel):
    id: int
    dt: int


@app.post("/notifications/")
async def receive_attendance(
        payload: IdentifierPayload,
        session: Session = Depends(get_db)
):
    try:
        # Retrieve date information and validate payload
        date_info = get_date_details(payload.dt)
        print(payload.id, payload.dt)  # Log for debugging
        if not payload.id or not payload.dt:
            raise HTTPException(status_code=400, detail="Error during reading ISIC.")

        # Extract details from date_info
        week_num = date_info['week_num']
        arrival_time = date_info['arrival_time']
        day_of_week = date_info['day_of_week']
        
        print(arrival_time)

        # Retrieve the lesson for the given time slot
        lesson = get_lesson_by_classroom_time(day_of_week=day_of_week, arrival_time=arrival_time, session=session)
        if not lesson:
            print("here1")
            raise HTTPException(status_code=404, detail="There is no lesson right now.")

        lesson_id = lesson.id
        if not lesson_id:
            print("here2")
          
            raise HTTPException(status_code=404, detail="There is no lesson right now.")

        # Record attendance for the student
        print(f"lesson_id: {lesson_id}, week_num: {week_num}, student_id: {payload.id}")
        await post_lesson_attendance(
            lesson_id=lesson_id,
            week_number=week_num,
            student_id=payload.id,
            present=True,
            session=session
        )
        # Commit the transaction to the database
        session.commit()

        # Return success response
        return {"status": "success", "student_id": payload.id}

    except Exception as e:
        # Rollback on error and raise HTTP exception
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to record attendance: {str(e)}")

    finally:
        pass
        # Always close the session
        # session.close()


@app.get("/courses/{teacher_id}")
async def get_courses(
        teacher_id: int,
        session: Session = Depends(get_db)
):
    courses = get_teacher_courses(teacher_id=teacher_id, session=session)
    courses_info = [
        {"id": course.id, "name": course.name, "short_name": course.short_name} for course in courses
    ]

    return courses_info


@app.get("/lessons/{teacher_id}")
async def get_lessons_by_teacher(
        teacher_id: int,
        session: Session = Depends(get_db)
):
    try:
        lessons = get_teacher_lessons(teacher_id=teacher_id, session=session)

        result = {}
        for lesson in lessons:
            course = get_course_by_id(course_id=lesson.course_id, session=session)

            if course:
                result[lesson.id] = {
                    "course_name": course.name,
                    "short_course_name": course.short_name,
                    "day_of_week": lesson.day_of_week,
                    "start_time": str(lesson.start_time),
                    "finish_time": str(lesson.finish_time)
                }
        return {"lessons": result}

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {"lessons": []}

    finally:
        session.close()


@app.get("/lessons/student/{student_id}")
async def get_lessons_by_student(
        student_id: int,
        session: Session = Depends(get_db)
):
    try:
        lessons = get_students_lessons(student_id=student_id, session=session)
        result = {}
        for lesson in lessons:
            course = get_course_by_id(lesson.course_id, session=session)

            if course:
                result[lesson.id] = {
                    "course_name": course.name,
                    "short_course_name": course.short_name,
                    "day_of_week": lesson.day_of_week,
                    "start_time": str(lesson.start_time),
                    "finish_time": str(lesson.finish_time)
                }
        return {"lessons": result}

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {"lessons": []}
    finally:
        pass

@app.post("/lessons/lesson_{lesson_id}/attendance/{week_number}/{student_id}")
async def post_lesson_attendance(
        lesson_id: int,
        week_number: int,
        student_id: int,
        present: int,
        session: Session = Depends(get_db)
):
    try:
        lesson = get_lesson_by_id(lesson_id=lesson_id, session=session)
        lesson_date = date.today()
        arrival_time = datetime.combine(lesson_date, lesson.start_time)

        int_to_bool = {
            1: True,
            2: False,
            3: None
        }
        present_value = int_to_bool.get(present, None)

        attendance = get_student_attendance_by_week(lesson_id=lesson_id, week_num=week_number, student_id=student_id,
                                                    session=session)
        if not attendance:
            raise HTTPException(status_code=404, detail="No such attendance in db.")

        report_attendance(attendance=attendance, present=present_value, arrival_time=arrival_time, session=session)
        session.commit()

    except Exception as e:
        print(f"Failed to record attendance: {e}")
        session.rollback()
    finally:
        session.close()

@app.get("/create_group")
async def get_all_students_without_course(course_id: int, session: Session = Depends(get_db)):
    students = get_all_students_not_assigned_to_course(course_id=course_id, session=session)

    students_info = [
        {"id": f"{student.id}", "name": student.name, "email": student.email}
        for student in students
    ]

    return students_info


@app.post("/add_lesson/")
async def add_lesson(lesson_request: LessonRequest, session: Session = Depends(get_db)):
    try:
        if lesson_request.course_id == 404:
            set_mode("TEST")

        __validate_lesson_request(lesson_request, session)

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


@app.get('/delete/lesson_{lesson_id}')
async def delete_lesson(lesson_id: int, session: Session = Depends(get_db)):
    delete_lesson_by_id(lesson_id = lesson_id, session=session)
    scheduler.cancel_or_finish_lesson(lesson_id=lesson_id, finish_immediately=True)


class Transaction(BaseModel):
    amount: float
    category: str
    description: str
    is_income: bool
    date: str


class TransactionModel(BaseModel):
    id: int

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: str  # Замість email
    password: str

class TokenData(BaseModel):
    email: str  # Замість email

class User(BaseModel):
    id: int
    email: str  # Замість email





db_dependency = Annotated[Session, Depends(get_db)]


# Transactions
@app.post("/transactions/", response_model=TransactionModel)
async def create_transaction(transaction: Transaction, db: db_dependency):
    db_transaction = TransactionM(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.get("/transactions/", response_model=List[TransactionModel])
async def read_transactions(db: db_dependency, skip: int = 0, limit: int = 100):
    return db.query(TransactionM).offset(skip).limit(limit).all()


# Create User
def get_user_by_email(email: str, db: db_dependency):
    return db.query(UserM).filter(UserM.email == email).first()

def create_user(user: UserCreate, db: db_dependency):
    hashed_password = pwd_context.hash(user.password)
    db_user = UserM(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post('/register/')
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(user.email, db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    return create_user(user, db)

# Login
def authenticate_user(email: str, password: str, db: Session):
    user = get_user_by_email(email, db)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



@app.post('/token/')
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "email": user.email}

# Verify Token
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=403, detail="Token is invalid or expired")
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Token is invalid or expired")

@app.get('/verify-token/{token}')
async def verify_user_token(token: str):
    verify_token(token)
    return {"message": "Token is valid"}

@app.get('/verify-email/teacher')
async def verify_email(email: str,
                       session: Session = Depends(get_db)):
    try:
        result = {"id": "-1", "isTeacher": False}

        teacher = get_teacher_by_email(email=email, session=session)
        if teacher:
            result["id"] = f"{teacher.id}"
            result["isTeacher"] = True
        else:
            student = get_student_by_email(email=email, session=session)
            if student:
                result["id"] = f"{student.id}"

        return result

    except Exception as e:
        print(f"Error verifying email: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while verifying the email.")
    finally:
        session.close()

@app.get('/get-current-week')
async def get_current_week():
    return __get_current_week()

@app.get('/get-pico-state')
async def get_pico_state():
    status = read_config_key(file_path='config.json', key='STATE')
    return {"status": status}


@app.post('/change-classroom')
async def change_classroom(classroom_id: int, session: Session = Depends(get_db)):
    """
    Change the classroom and publish the updated configuration to MQTT.
    """
    try:
        # Update classroom configuration locally
        set_classroom(classroom_id=classroom_id)

        # Get classroom name
        classroom_name = get_classroom_name(classroom_id=classroom_id, session=session)
        classroom_name = classroom_name[0]

        if not classroom_name:
            raise HTTPException(status_code=404, detail="Classroom not found")

        # Prepare the payload
        payload = {
            "classroom_id": classroom_id,
            "classroom_name": classroom_name
        }

        # Publish the payload to the MQTT topic
        base_topic = "kpi/endor/404_beta"  # Replace with your base topic
        topic = f"{base_topic}/config"
        fast_mqtt.publish(topic, json.dumps(payload))
        logger.debug(f"Sent a command: {classroom_id}")# Removed `await`

        return {
            "status": "success",
            "message": "Classroom configuration updated and published.",
            "published_payload": payload
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to change classroom: {str(e)}")


@app.get('/get-classrooms')
async def get_classrooms(session: Session = Depends(get_db)):
    classrooms = get_all_classrooms(session)
    return [
        {"id": classroom.id, "label": classroom.name}
        for classroom in classrooms
    ]
@app.get('/get-current-classroom')
async def get_current_classroom(session: Session = Depends(get_db)):
    current_classroom = get_classroom_id()
    classroom = get_classroom_by_name(classroom_id = current_classroom, session=session)
    return {"id": classroom.id, "label": classroom.name}


@app.get("/is_test")
async def is_in_test_mode(session: Session = Depends(get_db)):
    course_id = 404
    # course = get_course_by_id(course_id=course_id, session=session)
    lesson = get_lesson_by_course_id(course_id = course_id, session=session)
    return {"is_in_test_mode": lesson is not None}



