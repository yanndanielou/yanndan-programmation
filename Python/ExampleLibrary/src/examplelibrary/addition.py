""" Example module that performs addition """

from logger import logger_config


def add_custom(a: int, b: int) -> int:
    """Returns the sum of two integers."""
    res = add_custom_without_log(a, b)
    logger_config.print_and_log_info(f"add_custom for {a} and {b} returns  {res} ")
    return res


def add_custom_without_log(a, b):
    """Returns the sum of two integers."""
    res = a + b
    return res


def no_return_type(a):
    return a + 1
