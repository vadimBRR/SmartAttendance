import os
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
from src.config_file import get_mode

load_dotenv('local.env')
try:
    START_DATE = datetime.fromisoformat(os.getenv('START_DATE'))
except Exception as e:
    print(f"Invalid START_DATE format. Using current datetime instead. Error: {e}")
    START_DATE = datetime.now()

def __get_current_week(current_date=None):
    if get_mode() == 'TEST':
        return 1
    if current_date is None:
        current_date = datetime.now()

    return current_date.isocalendar()[1] - START_DATE.isocalendar()[1] + 1

def __is_valid_day_format(day_str):
    valid_days = [
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ]

    return day_str in valid_days

def get_date_details(unix_timestamp):
    arrival_time = datetime.fromtimestamp(unix_timestamp)
    print("1")
    # arrival_time = arrival_time - timedelta(hours=1)
    print("2")
    week_num = __get_current_week(arrival_time)
    day_of_week = datetime.now(pytz.timezone('Europe/Bratislava')).strftime('%A')
    return {
        'arrival_time': arrival_time,
        'week_num': week_num,
        'day_of_week': day_of_week
    }