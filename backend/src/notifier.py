import base64
import json
import os
from datetime import datetime, timedelta
import time
# from sched import scheduler

import requests
from apprise import apprise
from apprise.decorators import notify
from apprise.plugins.fcm.priority import NotificationPriority
from dotenv import load_dotenv
from loguru import logger
import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage
import json

from src.models import Notification, Settings
from src.database.database_config import DatabaseConfig
from src.sheduler import LessonScheduler

load_dotenv('local.env')

settings = Settings()
logger.debug(settings)

NOTIFIER_BROKER = os.getenv('NOTIFIER_BROKER')
NOTIFIER_USER = os.getenv('NOTIFIER_USER')
NOTIFIER_PASSWORD = os.getenv('NOTIFIER_PASSWORD')
NOTIFIER_BASE_TOPIC = os.getenv('NOTIFIER_BASE_TOPIC')
FASTAPI_URL = os.getenv('FASTAPI_URL')
SECRET_KEY = base64.b64decode("NDA0X2JldGFfa2V5MTIzNDU=")
TIMEZONE = os.getenv('TIMEZONE')

def send_to_fastapi(data, url = FASTAPI_URL):
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        logger.info(f"Successfully sent data to FastAPI: {response.json()}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send data to FastAPI: {e}")

# def get_from_fastapi(endpoint):
#     url = f"{FASTAPI_URL}/{endpoint}"
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         data = response.json()
#         logger.info(f"Successfully fetched data from FastAPI: {data}")
#         return data
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Failed to fetch data from FastAPI: {e}")
#         return None
#


def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties):
    logger.debug(f"Connected with result code {reason_code}")
    print(settings.base_topic)
    client.subscribe(settings.base_topic)
    client.subscribe(f'{settings.base_topic}/identifier')
    client.subscribe(f'{settings.base_topic}/cmd')
    client.subscribe(f'{settings.base_topic}/status')

    client.publish(f'{settings.base_topic}/status-notifer', json.dumps({'status': 'online'}), retain=True)
    # scheduler.start()


def handle_commands(client: mqtt.Client, payload: dict):
    if 'cmd' in payload:
        match payload['cmd']:
            case 'shutdown':
                logger.info("Going to shutdown")
                client.disconnect()
                quit(0)


def xor_decrypt(encrypted_data):

    decrypted = bytes(encrypted_data[i] ^ SECRET_KEY[i % len(SECRET_KEY)] for i in range(len(encrypted_data)))
    return int.from_bytes(decrypted, 'big')

def handle_identifier(client: mqtt.Client, payload: dict):
    if 'id' not in payload or 'dt' not in payload:
        logger.error(f"Invalid identifier payload: {payload}")
        return

    try:
        encrypted_id = base64.b64decode(payload['id'])

        identifier_id = xor_decrypt(encrypted_id)
        timestamp = payload['dt']

        logger.info(f"Processing identifier:encrypted_id={encrypted_id} ID={identifier_id}, Timestamp={timestamp}")
        send_to_fastapi({
            "id": identifier_id,
            "dt": timestamp
        })

    except Exception as e:
        logger.error(f"Failed to process identifier: {e}")

def notify(client: mqtt.Client, payload: dict):
    notification = Notification(**payload)
    apobj = apprise.Apprise()
    apobj.add(str(notification.urls))
    apobj.notify(
        body=notification.body,
        title=notification.title,
    )


def on_message(client: mqtt.Client, userdata, msg: MQTTMessage):
    logger.debug(f'{msg.topic}: {msg.payload}')
    payload = json.loads(msg.payload.decode())

    if msg.topic.endswith('/status'):
        print('status')
        status = payload.get('status')
        timestamp = payload.get('timestamp')
        if status == "online":
            __update_config_file(file_path='config.json', key='STATE', value=status)
            logger.info(f"Device is online since {time.localtime(timestamp)}")
        elif status == "offline":
            __update_config_file(file_path='config.json', key='STATE', value=status)
            logger.info(f"Device went offline at {time.localtime(timestamp)}")
        elif status == "sleep":
            __update_config_file(file_path='config.json', key='STATE', value=status)
            logger.info(f"Device went offline at {time.localtime(timestamp)}")
    elif msg.topic.endswith('/cmd'):
        handle_commands(client, payload)
    elif msg.topic.endswith('/identifier'):
        handle_identifier(client, payload)
    else:
        notify(client, payload)


def __update_config_file(file_path: str, key: str, value):
    try:
        try:
            with open(file_path, 'r') as file:
                config = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {}

        config[key] = value

        with open(file_path, 'w') as file:
            json.dump(config, file, indent=4)
        print(f"Updated '{key}' in {file_path}")
    except Exception as e:
        print(f"Failed to update config file: {e}")



def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(settings.user, settings.password)
    client.will_set(f'{settings.base_topic}/status', json.dumps({'status': 'offline'}), retain=True)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(settings.broker, settings.port, 60)

    db_config = DatabaseConfig()

    # Create a session instance from the sessionmaker
    session = db_config.Session()

    # Pass the session instance to the LessonScheduler
    scheduler = LessonScheduler(session=session)

    # Start the scheduler
    scheduler.start(classroom_id=1)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        client.disconnect()
        # scheduler.shutdown()


if __name__ == '__main__':
    main()

# sF-$aE7uGcNAzt*