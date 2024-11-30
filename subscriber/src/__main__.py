import json
import logging
import os
import pickle
import threading
import time

from dotenv import load_dotenv

from commons.configs import *
from commons.constants import *
from commons.files import *
from commons.mqtt import get_mqtt_client

load_dotenv()
logging_config(os.path.dirname(os.path.abspath(__file__)))


def main():

    logging.info("Start mqtt subscriber")

    mqtt_client = get_mqtt_client("sub")
    mqtt_client.connect(MQTT_HOST, MQTT_HOSTS[MQTT_HOST]["port"], 60)
    mqtt_client.loop_start()

    mqtt_client.subscribe(MQTT_TOPIC)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
