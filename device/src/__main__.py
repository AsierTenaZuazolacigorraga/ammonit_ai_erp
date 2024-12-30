import json
import logging
import os
import pickle
import random
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

# Define the endpoints and parameters
NO_AUTH_HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
}
AUTH_HEADERS = {
    "accept": "application/json",
    "Authorization": "Bearer {AUTH_TOKEN}",
}
LOGIN_URL = f"http://api.{os.getenv('DOMAIN')}/api/v1/login/access-token/"
LOGIN_DATA_POST = {
    "username": os.getenv("DEVICE_USERNAME"),
    "password": os.getenv("DEVICE_PASSWORD"),
}
MEASUREMENT_URL = f"http://api.{os.getenv('DOMAIN')}/api/v1/measurements/{os.getenv('DEVICE_MACHINE_ID')}"

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
                LOGIN_URL, headers=NO_AUTH_HEADERS, data=LOGIN_DATA_POST
            )
            data = process_response(response)
            if data:
                AUTH_HEADERS["Authorization"] = AUTH_HEADERS["Authorization"].format(
                    AUTH_TOKEN=data["access_token"]
                )
                break
            time.sleep(1)

        # Update machine
        loops = 0
        while True:

            loops += 1

            # # Update oee if needed
            # if loops == 10:
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
                    "machine_id": os.getenv("DEVICE_MACHINE_ID"),  # Id of the machine
                },
            )
            data = process_response(response)
            time.sleep(1)


if __name__ == "__main__":
    main()
