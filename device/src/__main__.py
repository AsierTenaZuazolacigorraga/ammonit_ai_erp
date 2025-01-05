import json
import logging
import os
import pickle
import random
import time
from datetime import datetime, timezone

import requests
from asyncua.sync import Client
from dotenv import load_dotenv

# Define the endpoints and parameters
if os.getenv("DOMAIN") == "localhost.tiangolo.com":
    IS_HTTPS = ""
else:
    IS_HTTPS = "s"
NO_AUTH_HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
}
AUTH_HEADERS = {
    "accept": "application/json",
    "Authorization": "Bearer {AUTH_TOKEN}",
}
LOGIN_URL = f"http{IS_HTTPS}://api.{os.getenv('DOMAIN')}/api/v1/login/access-token"
MACHINE_URL = f"http{IS_HTTPS}://api.{os.getenv('DOMAIN')}/api/v1/machines/{os.getenv('DEVICE_CUSTOMER_MACHINE_ID')}"
MEASUREMENT_URL = f"http{IS_HTTPS}://api.{os.getenv('DOMAIN')}/api/v1/measurements/{os.getenv('DEVICE_CUSTOMER_MACHINE_ID')}"

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_response(response: requests.Response) -> dict:

    # Check the response
    if response.status_code == 200:
        data = response.json()
        logger.info("Response JSON:")
        logger.info(data)
    else:
        data = {}
        logger.warning(f"Request failed with status code: {response.status_code}")
        logger.warning("Response text:")
        logger.warning(response.text)
    return data


def main():

    while True:

        # Get the access token
        while True:
            response = requests.post(
                LOGIN_URL,
                headers=NO_AUTH_HEADERS,
                data={
                    "username": os.getenv("DEVICE_CUSTOMER_USERNAME"),
                    "password": os.getenv("DEVICE_CUSTOMER_PASSWORD"),
                },
            )
            data = process_response(response)
            if data:
                AUTH_HEADERS["Authorization"] = AUTH_HEADERS["Authorization"].format(
                    AUTH_TOKEN=data["access_token"]
                )
                break
            time.sleep(1)

        # Get machine
        while True:
            response = requests.get(
                MACHINE_URL,
                headers=AUTH_HEADERS,
                params={"machine_id": os.getenv("DEVICE_CUSTOMER_MACHINE_ID")},
            )
            data = process_response(response)
            if data:
                machine = data
                break
            time.sleep(1)

        # Update machine
        loops = 0
        while True:

            # Obtain the value of the variable from the OPC UA server
            with Client(url=os.getenv("DEVICE_OPCUA_URL_CLIENT")) as client:
                # Find the namespace index
                nsidx = client.get_namespace_index(os.getenv("DEVICE_OPCUA_NAMESPACE"))
                print(
                    f"Namespace Index for '{os.getenv('DEVICE_OPCUA_NAMESPACE')}': {nsidx}"
                )

                # Get the variable node for read / write
                var = client.nodes.root.get_child(
                    f"0:Objects/{nsidx}:MyObject/{nsidx}:MyVariable"
                )
                value = var.read_value()
                print(f"Value of MyVariable ({var}): {value}")

                new_value = value + 0.1
                print(f"Setting value of MyVariable to {new_value} ...")
                var.write_value(new_value)

                # # Calling a method
                # res = client.nodes.objects.call_method(f"{nsidx}:ServerMethod", 5)
                # print(f"Calling ServerMethod returned {res}")

            # # Update oee if needed
            # loops += 1
            # if loops == 60:
            #     machine["oee"] = random.randint(1, 100)
            #     machine["oee_availability"] = random.randint(1, 100)
            #     machine["oee_performance"] = random.randint(1, 100)
            #     machine["oee_quality"] = random.randint(1, 100)
            #     response = requests.put(
            #         MACHINE_URL,
            #         headers=AUTH_HEADERS,
            #         json=machine,
            #     )
            #     process_response(response)
            #     loops = loops / 2

            # Create measurement
            response = requests.post(
                MEASUREMENT_URL,
                headers=AUTH_HEADERS,
                json={
                    "timestamp": datetime.now(
                        timezone.utc
                    ).isoformat(),  # Current UTC time in ISO 8601 format
                    "temperature": loops,  # Example temperature value
                    "power_usage": loops - 0.9,  # Example power usage value
                    "machine_id": os.getenv(
                        "DEVICE_CUSTOMER_MACHINE_ID"
                    ),  # Id of the machine
                },
            )
            data = process_response(response)
            time.sleep(1)


if __name__ == "__main__":
    main()
