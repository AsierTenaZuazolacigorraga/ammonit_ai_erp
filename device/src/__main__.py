import json
import logging
import os
import pickle

import paho.mqtt.client as mqtt
from constants import *
from dotenv import load_dotenv

from commons.configs import *
from commons.constants import *
from commons.files import *

load_dotenv()
logging_config(os.path.dirname(os.path.abspath(__file__)))


def main():

    # AWS IoT Core credentials and endpoint
    host = "YOUR_AWS_IOT_ENDPOINT"
    port = 8883
    client_id = "myClientID"
    thing_name = "myIoTDevice"
    topic = "temperatureData"

    # Define the MQTT client
    mqtt_client = mqtt.Client(client_id)
    mqtt_client.tls_set()  # Enable TLS encryption
    mqtt_client.username_pw_set(username="AWS_ACCESS_KEY", password="AWS_SECRET_KEY")

    # Connect to the AWS IoT Core
    mqtt_client.connect(host, port, 60)

    # Sending data (temperature reading as an example)
    payload = {"temperature": 22.5, "timestamp": "2024-11-19T10:00:00"}

    # Publish data to AWS IoT Core
    mqtt_client.publish(topic, json.dumps(payload), qos=1)

    # Keep the connection alive
    mqtt_client.loop_forever()


if __name__ == "__main__":
    main()
