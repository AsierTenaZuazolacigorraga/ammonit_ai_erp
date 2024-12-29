import json
import logging
import os
import time

from dotenv import load_dotenv

from iot_commons.mqtt import get_mqtt_client

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def on_message(mqttc, obj, msg):  # Types not defined on porpouse

    # Parse the message (assuming it's JSON)
    data = json.loads(msg.payload.decode())

    # Prepare the data for db

    # Write to db using the API


def main():

    logging.info("Start mqtt subscriber")

    mqtt_client = get_mqtt_client(
        os.getenv("MQTT_SUB"),
        os.getenv("MQTT_USER"),
        os.getenv("MQTT_PSW"),
        on_message=on_message,
    )
    mqtt_client.connect(os.getenv("MQTT_HOST"), int(os.getenv("MQTT_PORT")), 60)
    mqtt_client.loop_start()

    # Subscribe
    mqtt_client.subscribe("machines")

    # Loop forever
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
