# -*-coding:Utf-8 -*
import datetime
import time

import pytest

from logger import logger_config


def test_number_of_errors_is_correct_for_exceptions() -> None:
    # importlib.reload(logger_config)
    with logger_config.application_logger():
        try:
            assert False, "create exception"
        except AssertionError as ass_err:
            logger_config.print_and_log_exception(ass_err)

    assert logger_config.log_counts_occurrences_per_level["ERROR"] == 1


def test_number_of_errors_is_correct_for_errors() -> None:
    # importlib.reload(logger_config)
    time.sleep(2)
    time.sleep(2)
    with logger_config.application_logger():
        time.sleep(2)
        logger_config.print_and_log_error(f"Manual error {datetime.datetime.now()}")  # noqa: DTZ005

    assert logger_config.log_counts_occurrences_per_level["ERROR"] == 1
