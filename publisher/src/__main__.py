import json
import logging
import os
import pickle
import time

from dotenv import load_dotenv

from commons.configs import *
from commons.constants import *
from commons.files import *
from commons.mqtt import get_mqtt_client

load_dotenv()
logging_config(os.path.dirname(os.path.abspath(__file__)))


def main():

    logging.info("Start mqtt publisher")

    mqtt_client = get_mqtt_client("pub")
    mqtt_client.connect(MQTT_HOST, MQTT_HOSTS[MQTT_HOST]["port"], 60)
    mqtt_client.loop_start()

    i = 0
    while True:
        i += 1

        # Publishing a message
        payload = json.dumps({"temperature": 22.5 + i, "humidity": 60 - i})
        mqtt_client.publish(MQTT_TOPIC, payload)

        logging.info(f"Message sent: {payload}")
        time.sleep(1)


if __name__ == "__main__":
    main()
