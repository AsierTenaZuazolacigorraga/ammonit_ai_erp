import logging
import os

from dotenv import load_dotenv

load_dotenv()

# Logger

LOGGER_FILE = "logs.txt"
LOGGER_MAX_BYTES = 5 * 1024 * 1024
LOGGER_BACKUP_COUNT = 5
LOGGER_LEVEL = logging.INFO
LOGGER_DATE_FMT = "%Y-%m-%d %H:%M:%S"
LOGGER_LINE_FMT = "%(asctime)s - %(levelname)s - %(message)s"
LOGGER_FORMATTER = logging.Formatter(LOGGER_LINE_FMT, LOGGER_DATE_FMT)

# Mqtt
MQTT_HOSTS = {
    "aws": {
        "host": os.getenv("AWS_HOST"),
        "port": 1884,
        "user": os.getenv("MQTT_USER"),
        "psw": os.getenv("MQTT_PSW"),
        "topic": "test/topic/16011",
        # "cafile": "/home/atena/my_projects/iot_bind/.gitignores/mosquitto.org.crt",
        # "key": "",
        # "cert": "",
    },
    "mosquitto.org": {
        "host": "test.mosquitto.org",
        "port": 8885,
        "user": "rw",
        "psw": "readwrite",
        "cafile": "/home/atena/my_projects/iot_bind/.gitignores/mosquitto.org.crt",
        # "key": "",
        # "cert": "",
    },
    "local": {
        "host": "localhost",
        "port": 8883,
        "user": "iot_bind",
        "psw": "iot_bind",
        "cafile": "/etc/mosquitto/conf.d/custom_ca.crt",
        # "key": "/etc/mosquitto/conf.d/custom_client.key",
        # "cert": "/etc/mosquitto/conf.d/custom_client.crt",
    },
}

# Influx
INFLUXDB_HOST = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUXDB_ORG = "iot_bind"
INFLUXDB_DB = "iot_bind_db"

# User configurations
MQTT_HOST = MQTT_HOSTS["aws"]
MQTT_IS_DOCKER = True
