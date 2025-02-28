""" Example module that performs addition """

from logger import logger_config


def add_custom(a: int, b: int) -> int:
    """Returns the sum of two integers."""
    res = a + b
    logger_config.print_and_log_info(f"add_custom for {a} and {b} returns  {res} ")
    return res


def no_return_type(a: int):
    return a + 1
