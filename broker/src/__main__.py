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

    logging.info("Start mqtt broker")


if __name__ == "__main__":
    main()
