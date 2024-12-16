import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from commons_py.configs import *
from commons_py.constants import *
from commons_py.database import get_influx_client

load_dotenv()
logging_config(os.path.dirname(os.path.abspath(__file__)))


class TemperatureResponse(BaseModel):
    temperature: float


app = FastAPI()
influx_client = get_influx_client()


@app.get("/")
async def get():
    return [{"id": 0, "name": "None"}]


@app.get("/api/temperature")
async def get_api_temperature():

    result = influx_client.query(
        database=INFLUXDB_DB,
        query="""
SELECT *
FROM "state"
WHERE
time >= now() - interval '10 seconds'
AND
("temperature" IS NOT NULL)
""",
    )

    if result:
        temperature = result["temperature"][0].as_py()
        return TemperatureResponse(temperature=temperature)
    else:
        return TemperatureResponse(temperature=0.0)  # or handle error appropriately


def main():

    logging.info("Start backend")


if __name__ == "__main__":
    main()
