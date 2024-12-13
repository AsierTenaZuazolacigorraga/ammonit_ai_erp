import json
import logging
import os
import time

from dotenv import load_dotenv
from influxdb_client_3 import InfluxDBClient3, Point
from influxdb_client_3.write_client.rest import ApiException

from commons.configs import *
from commons.constants import *
from commons.mqtt import get_mqtt_client

load_dotenv()
logging_config(os.path.dirname(os.path.abspath(__file__)))


def get_influx_client() -> InfluxDBClient3:

    return InfluxDBClient3(
        host=INFLUXDB_HOST, token=os.environ.get("INFLUXDB_TOKEN"), org=INFLUXDB_ORG
    )


influx_client = get_influx_client()


def on_message(mqttc, obj, msg):  # Types not defined on porpouse

    # Parse the message (assuming it's JSON)
    data = json.loads(msg.payload.decode())

    # Prepare the data for InfluxDB
    point = (
        Point("state")
        .tag("machine", data["machine"])
        .field("temperature", data["temperature"])
    )

    # Write to InfluxDB (ugly but it might work)
    try:
        influx_client.write(database=INFLUXDB_DB, record=point)
        logging.info(f"InfluxDB: writting this data - {data}")
    except ApiException as e:
        logging.warning(f"InfluxDB: failed to write data to InfluxDB: {e}")
        influx_client = get_influx_client()
        influx_client.write(database=INFLUXDB_DB, record=point)


def main():

    logging.info("Start mqtt subscriber")

    mqtt_client = get_mqtt_client("sub", on_message=on_message)
    if MQTT_IS_DOCKER:
        mqtt_client.connect(
            "mosquitto", MQTT_HOST["port"], 60
        )  # Use this when running on aws and docker container
    else:
        mqtt_client.connect(
            MQTT_HOST["host"], MQTT_HOST["port"], 60
        )  # Use this when running on my pc
    mqtt_client.loop_start()

    mqtt_client.subscribe(MQTT_HOST["topic"])

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
