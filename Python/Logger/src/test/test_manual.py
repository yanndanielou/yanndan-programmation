# -*-coding:Utf-8 -*

import pytest
import os

from src.logger import logger_config


def test_basic_encryption_decryption() -> None:

    with logger_config.application_logger():
        logger_config.print_and_log_info("1")
        logger_config.print_and_log_warning("2")
        logger_config.print_and_log_warning_if(1 < 2, "2 bis")
        logger_config.print_and_log_error("3")
        logger_config.print_and_log_error_if(1 < 2, "3 bis")


def test_basic_encryption_decryption1() -> None:

    with logger_config.application_logger():
        logger_config.print_and_log_info("1")
        logger_config.print_and_log_warning("2")
        logger_config.print_and_log_warning_if(1 < 2, "2 bis")
        logger_config.print_and_log_error("3")
        logger_config.print_and_log_error_if(1 < 2, "3 bis")
