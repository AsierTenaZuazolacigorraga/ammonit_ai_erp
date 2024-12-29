import logging
from typing import Callable

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion


def on_connect(
    mqttc, obj, flags, reason_code, properties
):  # Types not defined on porpouse
    logging.info(f"Connected: reason_code - {reason_code}")


def on_message(mqttc, obj, msg):  # Types not defined on porpouse
    logging.info(f"Received: {msg.topic} {msg.qos} {msg.payload}")


def on_subscribe(
    mqttc, obj, mid, reason_code_list, properties
):  # Types not defined on porpouse
    logging.info(f"Subscribed: {mid} {reason_code_list}")


def on_log(mqttc, obj, level, string):  # Types not defined on porpouse
    logging.info(f"Log: {string}")


def get_mqtt_client(
    mqtt_client_id: str,
    mqtt_user: str,
    mqtt_psw: str,
    is_use_log: bool = False,
    on_message: Callable = on_message,
) -> mqtt.Client:

    mqtt_client = mqtt.Client(
        callback_api_version=CallbackAPIVersion.VERSION2, client_id=mqtt_client_id
    )
    # mqtt_client.tls_set(
    #     ca_certs=MQTT_HOSTS[MQTT_HOST]["cafile"],
    #     # certfile=MQTT_HOSTS[MQTT_HOST]["cert"],
    #     # keyfile=MQTT_HOSTS[MQTT_HOST]["key"],
    # )
    mqtt_client.username_pw_set(mqtt_user, mqtt_psw)
    mqtt_client.on_message = on_message
    mqtt_client.on_connect = on_connect
    mqtt_client.on_subscribe = on_subscribe
    if is_use_log:
        mqtt_client.on_log = on_log
    return mqtt_client
