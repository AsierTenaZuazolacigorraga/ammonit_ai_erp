import logging
import os
from logging.handlers import RotatingFileHandler

from .constants import *


def logging_config(logger_root: str) -> None:

    logger_folder = os.path.join(logger_root, "logs")

    # Configure basic settings with basicConfig
    logging.basicConfig(
        level=LOGGER_LEVEL,
        format=LOGGER_LINE_FMT,
        datefmt=LOGGER_DATE_FMT,
    )

    # Create the log directory if it doesn't exist
    os.makedirs(logger_folder, exist_ok=True)

    # Create a rotating file handler separately
    file_handler = RotatingFileHandler(
        os.path.join(logger_folder, LOGGER_FILE),
        maxBytes=LOGGER_MAX_BYTES,
        backupCount=LOGGER_BACKUP_COUNT,
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(LOGGER_FORMATTER)

    # Add the rotating file handler to the root logger
    logging.getLogger().addHandler(file_handler)
