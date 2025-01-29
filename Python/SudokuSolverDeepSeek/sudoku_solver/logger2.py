import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    log_file = os.path.join(os.path.dirname(__file__), "..", "logs", "sudoku.log")
    handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=5)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
