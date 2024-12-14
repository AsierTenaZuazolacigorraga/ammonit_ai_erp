import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI

from commons_py.configs import *
from commons_py.constants import *

load_dotenv()
logging_config(os.path.dirname(os.path.abspath(__file__)))


app = FastAPI()


@app.get("/")
async def get():
    return [{"id": 0, "name": "None"}]


@app.get("/items")
async def get_items():
    return [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]


def main():

    logging.info("Start backend")


if __name__ == "__main__":
    main()
