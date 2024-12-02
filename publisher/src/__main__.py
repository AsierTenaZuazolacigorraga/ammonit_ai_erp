import json
import logging
import os
import pickle
import time
from datetime import datetime, timezone

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
    mqtt_client.connect(MQTT_HOST["host"], MQTT_HOST["port"], 60)
    mqtt_client.loop_start()

    i = 0
    while True:
        i += 1

        # Get the current time in UTC
        current_time_utc = datetime.now(timezone.utc)

        # Format as ISO 8601 string
        iso_8601_time = current_time_utc.isoformat()

        # Publishing a message
        payload = json.dumps(
            {
                "timestamp": iso_8601_time,
                "machine": "fresadora trimodo",
                "temperature": i,
                "humidity": 10 + i,
            }
        )
        mqtt_client.publish(MQTT_HOST["topic"], payload)

        logging.info(f"Message sent: {payload}")
        time.sleep(5)


if __name__ == "__main__":
    main()
