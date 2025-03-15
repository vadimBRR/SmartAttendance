        # Отримання ключа шифрування
import json
import time
from states.state import AbstractState
from states.idle import Idle
from utils.encryptor import SimpleEncryptor
from utils.base64 import base64_encode
import utime


class PublishData(AbstractState):
    def __init__(self, device, card_data=None):
        self.device = device
        self.card_data = card_data

        encryption_key_base64 = self.device.config.get("encryption_key", "")
        self.encryptor = SimpleEncryptor(encryption_key_base64)

    def exec(self):
        print("Publishing data...")

        if not self.device.mqtt:
            print("MQTT client is not initialized. Returning to Idle state.")
            self.device.change_state(Idle(self.device))
            return

        try:
            base_topic = self.device.config['mqtt']['base_topic']
            topic = f"{base_topic}/identifier"

            if self.card_data:
                if isinstance(self.card_data["id"], int):
                    encrypted_id = self.encryptor.xor_encrypt(self.card_data["id"].to_bytes(8, 'big'))
                else:
                    encrypted_id = self.encryptor.xor_encrypt(self.card_data["id"])

                self.card_data["id"] = base64_encode(encrypted_id)

            message = self.card_data if self.card_data else {
                "id": base64_encode(self.encryptor.xor_encrypt(0).to_bytes(8, 'big')),
                "dt": int(time.time()),
                "class": self.device.config.get("current_class", "Unknown")
            }

            message_json = json.dumps(message)
            self.device.mqtt.publish(topic, message_json)
            print(f"Published data to {topic}: {message_json}")
            self.device.set_status_color((0, 1023, 0))
            self.device.play_buzzer(frequency=1000, duration=0.5)

            utime.sleep(1)
            self.device.set_status_color((0, 0, 0))
        except Exception as e:
            print(f"Error publishing data: {e}")

        self.device.change_state(Idle(self.device))
