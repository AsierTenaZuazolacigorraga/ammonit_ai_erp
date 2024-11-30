import logging

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
    "test.mosquitto.org": {
        "port": 8885,
        "user": "rw",
        "psw": "readwrite",
        "cafile": "/home/atena/my_projects/iot_bind/.gitignores/mosquitto.org.crt",
        # "key": "",
        # "cert": "",
    },
    "localhost": {
        "port": 8883,
        "user": "iot_bind",
        "psw": "iot_bind",
        "cafile": "/etc/mosquitto/conf.d/custom_ca.crt",
        # "key": "/etc/mosquitto/conf.d/custom_client.key",
        # "cert": "/etc/mosquitto/conf.d/custom_client.crt",
    },
}
MQTT_HOST = "test.mosquitto.org"
MQTT_TOPIC = "test/topic/16011"
