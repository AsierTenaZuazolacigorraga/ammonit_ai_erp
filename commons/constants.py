import logging

LOGGER_FILE = "logs.txt"
LOGGER_MAX_BYTES = 5 * 1024 * 1024
LOGGER_BACKUP_COUNT = 5
LOGGER_LEVEL = logging.INFO
LOGGER_DATE_FMT = "%Y-%m-%d %H:%M:%S"
LOGGER_LINE_FMT = "%(asctime)s - %(levelname)s - %(message)s"
LOGGER_FORMATTER = logging.Formatter(LOGGER_LINE_FMT, LOGGER_DATE_FMT)
