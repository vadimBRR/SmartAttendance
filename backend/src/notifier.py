import base64
import os
import time
from functools import partial

import requests
from apprise import apprise
from apprise.decorators import notify
from apprise.plugins.fcm.priority import NotificationPriority
from dotenv import load_dotenv
from fastapi_mqtt import FastMQTT, MQTTConfig
from loguru import logger
import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage
import json

from src.models import Notification, Settings
from src.database.database_config import DatabaseConfig
from src.sheduler import LessonScheduler

from src.config_file import update_config_file

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

mqtt_config = MQTTConfig(
    host=NOTIFIER_BROKER,  # Replace with your broker's host
    port=1883,               # Broker port
    username=NOTIFIER_USER,  # Replace with your MQTT username
    password=NOTIFIER_PASSWORD,  # Replace with your MQTT password
    # keepalive=60,
    version=4
)
fast_mqtt = FastMQTT(config=mqtt_config)



def send_to_fastapi(data, url = FASTAPI_URL):
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        logger.info(f"Successfully sent data to FastAPI: {response.json()}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send data to FastAPI: {e}")

# @fast_mqtt.on_connect()
# def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties):
#     logger.debug(f"Connected with result code {reason_code}")
#     print(settings.base_topic)
#     client.subscribe(settings.base_topic)
#     client.subscribe(f'{settings.base_topic}/identifier')
#     client.subscribe(f'{settings.base_topic}/cmd')
#     client.subscribe(f'{settings.base_topic}/status')
#
#     client.publish(f'{settings.base_topic}/status-notifer', json.dumps({'status': 'online'}), retain=True)
#     # scheduler.start()

@fast_mqtt.on_connect()
def on_connect(client, flags, reason_code, properties):
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

def handle_activity(client: mqtt.Client, command: str):
    client.publish(f"{NOTIFIER_BASE_TOPIC}/command", f"{command}")
    logger.debug(f"Sent a command: {command}")


def notify(client: mqtt.Client, payload: dict):
    notification = Notification(**payload)
    apobj = apprise.Apprise()
    apobj.add(str(notification.urls))
    apobj.notify(
        body=notification.body,
        title=notification.title,
    )

@fast_mqtt.on_message()
async def on_message(client: mqtt.Client,  topic: str, payload: bytes, qos: int, properties: dict):
    logger.debug(f'{topic}: {payload}')
    payload = json.loads(payload.decode())

    if topic.endswith('/status'):
        print('status')
        status = payload.get('status')
        timestamp = payload.get('timestamp')
        if status == "online":
            update_config_file(file_path='config.json', key='STATE', value=status)
            logger.info(f"Device is online since {time.localtime(timestamp)}")
        elif status == "offline":
            update_config_file(file_path='config.json', key='STATE', value=status)
            logger.info(f"Device went offline at {time.localtime(timestamp)}")
        elif status == "sleep":
            update_config_file(file_path='config.json', key='STATE', value=status)
            logger.info(f"Device went offline at {time.localtime(timestamp)}")
    elif topic.endswith('/cmd'):
        handle_commands(client, payload)
    elif topic.endswith('/identifier'):
        handle_identifier(client, payload)
    else:
        notify(client, payload)


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
    scheduler = LessonScheduler(session=session, handle_activity=partial(handle_activity, client))

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