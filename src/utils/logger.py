import logging
import os
from datetime import datetime
from src.config import LOG_DIRECTORY, APP_NAME

LOG_FILE = os.path.join(LOG_DIRECTORY, f'application_{datetime.now().strftime("%Y-%m-%d")}.log')


def setup_logger(name: str, log_file: str = LOG_FILE, level: int = logging.INFO):

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.hasHandlers():
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# Main application logger
app_logger = setup_logger(APP_NAME)
