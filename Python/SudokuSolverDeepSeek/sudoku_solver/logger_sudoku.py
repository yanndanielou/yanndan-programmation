from logger import logger_config
import logging
import os
from logging.handlers import RotatingFileHandler


def get_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    return logger_config.get_logger(name, "sudoku.log", level)
