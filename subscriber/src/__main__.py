import json
import logging
import os
import pickle
import threading
import time

from dotenv import load_dotenv
from influxdb_client_3 import InfluxDBClient3, Point

from commons.configs import *
from commons.constants import *
from commons.files import *
from commons.mqtt import get_mqtt_client

load_dotenv()
logging_config(os.path.dirname(os.path.abspath(__file__)))


influx_client = InfluxDBClient3(
    host=INFLUXDB_HOST, token=os.environ.get("INFLUXDB_TOKEN"), org=INFLUXDB_ORG
)


def on_message(mqttc, obj, msg):

    # Parse the message (assuming it's JSON)
    data = json.loads(msg.payload.decode())

    # Prepare the data for InfluxDB
    point = (
        Point("state")
        .tag("machine", data["machine"])
        .field("temperature", data["temperature"])
    )

    # Write to InfluxDB
    influx_client.write(database=INFLUXDB_DB, record=point)
    logging.info(f"InfluxDB: writting this data - {data}")


def main():

    logging.info("Start mqtt subscriber")

    mqtt_client = get_mqtt_client("sub", on_message=on_message)
    mqtt_client.connect(MQTT_HOST["host"], MQTT_HOST["port"], 60)
    mqtt_client.loop_start()

    mqtt_client.subscribe(MQTT_HOST["topic"])

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
