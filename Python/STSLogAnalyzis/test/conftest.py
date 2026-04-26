import logging

from logger import logger_config


def pytest_configure(config):
    """Configure the shared logger before any tests run."""
    logger_config.configure_logger_with_exact_file_name("pytest_tests.log", logger_level=logging.INFO)
