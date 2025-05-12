"""logger"""

import datetime
# To get line number for logs
# from inspect import currentframe, getframeinfo
import inspect
# -*-coding:Utf-8 -*
import logging
import os
import random
import sys
import time
from collections.abc import Generator
from contextlib import contextmanager
# from warnings import deprecated
from logging.handlers import RotatingFileHandler
from typing import Optional

# pylint: enable=logging-not-lazy
# pylint: disable=logging-fstring-interpolation

DEFAULT_CALL_STACK_CONTEXT_VALUE = 1
DEFAULT_CALL_STACK_FRAME_VALUE = 2


def __get_calling_file_name_and_line_number(
    call_stack_context: int = DEFAULT_CALL_STACK_CONTEXT_VALUE,
    call_stack_frame: int = DEFAULT_CALL_STACK_FRAME_VALUE,
) -> str:
    previous_stack = inspect.stack(call_stack_context)[call_stack_frame]
    file_name = previous_stack.filename
    line_number = previous_stack.lineno
    return file_name + ", line " + str(line_number)


def __get_calling_file_name() -> str:
    previous_stack = inspect.stack(1)[1]
    file_name = previous_stack.filename
    return file_name


def __get_calling_line_number() -> int:
    previous_stack = inspect.stack(1)[1]
    line_number = previous_stack.lineno
    return line_number


def print_and_log_critical_and_kill(to_print_and_log: str) -> None:
    """Print in standard output and log in file as info critical, then kill application"""
    log_timestamp = time.asctime(time.localtime(time.time()))

    # pylint: disable=line-too-long
    print(log_timestamp + "\t" + __get_calling_file_name_and_line_number() + "\t" + to_print_and_log)

    logging.critical(f"{__get_calling_file_name_and_line_number()} '\t' {to_print_and_log}")
    sys.exit()


def print_and_log_info_if(condition: bool, to_print_and_log: str) -> None:
    """Print in standard output and log in file as info level"""
    if condition:
        log_timestamp = time.asctime(time.localtime(time.time()))

        # pylint: disable=line-too-long
        print(log_timestamp + "\t" + __get_calling_file_name_and_line_number() + "\t" + to_print_and_log)
        logging.info(f"{__get_calling_file_name_and_line_number()} \t {to_print_and_log}")


def print_and_log_info(to_print_and_log: str) -> None:
    """Print in standard output and log in file as info level"""
    log_timestamp = time.asctime(time.localtime(time.time()))

    # pylint: disable=line-too-long
    print(log_timestamp + "\t" + __get_calling_file_name_and_line_number() + "\t" + to_print_and_log)
    logging.info(f"{__get_calling_file_name_and_line_number()} \t {to_print_and_log}")


def print_and_log_warning(to_print_and_log: str) -> None:
    """Print in standard output and log in file as info level"""
    log_timestamp = time.asctime(time.localtime(time.time()))

    # pylint: disable=line-too-long
    print(log_timestamp + "\t" + __get_calling_file_name_and_line_number() + "\t" + str() + to_print_and_log)
    logging.warning(f"{__get_calling_file_name_and_line_number()} \t {to_print_and_log}")


def print_and_log_exception(exception_to_print: Exception, additional_text: Optional[str] = None) -> None:
    if additional_text:
        to_print_and_log = f"Exception raised:{additional_text} "
        print_and_log_error(to_print_and_log, call_stack_frame=3)

    print_and_log_error(to_print_and_log=f"Exception raised, content:{str(exception_to_print)}", call_stack_frame=3)
    print_and_log_error(
        to_print_and_log=f"Exception raised, type:{exception_to_print.__class__.__name__}", call_stack_frame=3
    )

    log_timestamp = time.asctime(time.localtime(time.time()))
    print(log_timestamp + "\t" + __get_calling_file_name_and_line_number(call_stack_context=0) + "\t" + "!!ERROR!!")
    print(
        log_timestamp + "\t" + __get_calling_file_name_and_line_number(call_stack_context=0) + "\t !!EXCEPTION THROWN!!"
    )

    logging.exception(exception_to_print)


def print_and_log_error(
    to_print_and_log: str,
    call_stack_context: int = DEFAULT_CALL_STACK_CONTEXT_VALUE,
    call_stack_frame: int = DEFAULT_CALL_STACK_FRAME_VALUE,
) -> None:
    """Print in standard output and log in file as error level"""
    log_timestamp = time.asctime(time.localtime(time.time()))
    print(log_timestamp + "\t" + "!!ERROR!!")
    # pylint: disable=line-too-long
    print(
        log_timestamp
        + "\t"
        + __get_calling_file_name_and_line_number(
            call_stack_context=call_stack_context, call_stack_frame=call_stack_frame
        )
        + "\t"
        + str()
        + to_print_and_log
    )
    logging.error(f"{__get_calling_file_name_and_line_number()} \t {to_print_and_log}")


def configure_logger_with_random_log_file_suffix(
    log_file_name_prefix: str, log_file_extension: str = "log", logger_level: int = logging.INFO
) -> None:
    """Configure the logger with_random_log_file_suffix"""
    log_file_name = f"{log_file_name_prefix}_{str(random.randrange(100000))}.{log_file_extension}"
    configure_logger_with_exact_file_name(log_file_name, logger_level)


def configure_logger_not_working(logger_level: int = logging.INFO) -> None:
    """Configure the logger with_random_log_file_suffix"""
    previous_stack = inspect.stack(1)[2]
    calling_script_file_name = previous_stack.filename
    log_file_extension: str = "log"
    log_file_name_prefix = calling_script_file_name
    log_file_name = f"{log_file_name_prefix}_{str(random.randrange(100000))}.{log_file_extension}"
    configure_logger_with_exact_file_name(log_file_name, logger_level)


def configure_logger_with_exact_file_name(log_file_name: str, logger_level: int = logging.INFO) -> None:
    """Configure the logger"""
    logger_directory = "logs"

    if not os.path.exists(logger_directory):
        os.makedirs(logger_directory)

    print(time.asctime(time.localtime(time.time())) + "\t" + "Logger level:" + str(logger_level))

    logging.basicConfig(
        level=logger_level,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S",
        filename=logger_directory + "\\" + log_file_name,
        filemode="w",
    )
    # logging.debug
    # logging.info
    # logging.warning
    # logging.error
    # logging.critical


class ExecutionTime(object):
    """Print execution time of a function"""

    def __init__(self, f):  # type: ignore
        self.f = f

    def __call__(self, *args):  # type: ignore
        # pylint: enable=logging-not-lazy
        # pylint: disable=logging-fstring-interpolation
        logging.info(f"Entering {self.f.__name__}")
        logging.debug(f"Arguments passed to {self.f.__name__} : {str(locals())}")
        start_time = time.time()

        # Call method
        ret = self.f(*args)

        elapsed_time = time.time() - start_time
        # pylint: disable=line-too-long
        logging.info(f"Exited {  self.f.__name__} . Elapsed: {format(elapsed_time, '.2f')} s")
        return ret


class PrintOutput(object):
    """print output of function"""

    def __init__(self, f) -> None:  # type: ignore
        self.f = f

    def __call__(self, *args):  # type: ignore

        # Call method
        ret = self.f(*args)

        # pylint: disable=logging-fstring-interpolation
        logging.debug(f"self.f.__name__  returns: {str(ret)}")
        return ret


class PrintInputAndOutput(object):
    """print input and output of function"""

    def __init__(self, f):  # type: ignore
        self.f = f

    def __call__(self, *args):  # type: ignore

        # Call method
        ret = self.f(*args)

        # pylint: enable=logging-not-lazy
        # pylint: disable=logging-fstring-interpolation
        # pylint: disable=line-too-long
        logging.debug(f"Arguments passed to {self.f.__name__ } called with: {str(args)} returns: {str(ret)}")
        return ret


def get_logger(name: str, rotating_file_name_without_extension: str, level: int = logging.DEBUG) -> logging.Logger:
    """Create and configure a logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Create a rotating file handler
    handler = RotatingFileHandler(
        f"logs/{rotating_file_name_without_extension}.log", maxBytes=1024 * 1024, backupCount=5
    )
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


@contextmanager
def stopwatch_with_label(
    label: str, enable_print: bool = True, enable_log: bool = True, enabled: bool = True
) -> Generator[float, None, None]:
    """Décorateur de contexte pour mesurer le temps d'exécution d'une fonction :
    https://www.docstring.fr/glossaire/with/"""
    if enabled:
        debut = time.perf_counter()
        yield time.perf_counter() - debut
        fin = time.perf_counter()
        duree = fin - debut
        to_print_and_log = f"{label} Elapsed: {duree:.2f} seconds"

        log_timestamp = time.asctime(time.localtime(time.time()))

        previous_stack = inspect.stack(0)[2]
        file_name = previous_stack.filename
        line_number = previous_stack.lineno
        calling_file_name_and_line_number = file_name + ", line " + str(line_number)

        # pylint: disable=line-too-long
        if enable_print:
            print(log_timestamp + "\t" + calling_file_name_and_line_number + "\t" + to_print_and_log)

        if enable_log:
            logging.info(f"{calling_file_name_and_line_number} \t {to_print_and_log}")

    else:
        yield 0.0


@contextmanager
def stopwatch_with_label(
    label: str, enable_print: bool = True, enable_log: bool = True, enabled: bool = True
) -> Generator[float, None, None]:
    """Décorateur de contexte pour mesurer le temps d'exécution d'une fonction :
    https://www.docstring.fr/glossaire/with/"""
    if enabled:
        debut = time.perf_counter()
        yield time.perf_counter() - debut
        fin = time.perf_counter()
        duree = fin - debut
        to_print_and_log = f"{label} Elapsed: {duree:.2f} seconds"

        log_timestamp = time.asctime(time.localtime(time.time()))

        previous_stack = inspect.stack(0)[2]
        file_name = previous_stack.filename
        line_number = previous_stack.lineno
        calling_file_name_and_line_number = file_name + ", line " + str(line_number)

        # pylint: disable=line-too-long
        if enable_print:
            print(log_timestamp + "\t" + calling_file_name_and_line_number + "\t" + to_print_and_log)

        if enable_log:
            logging.info(f"{calling_file_name_and_line_number} \t {to_print_and_log}")

    else:
        yield 0.0


@contextmanager
def stopwatch_alert_if_exceeds_duration(
    label: str,
    duration_threshold_to_alert_info_in_s: float,
    duration_threshold_to_alert_warning_in_s: Optional[float] = None,
    duration_threshold_to_alert_error_in_s: Optional[float] = None,
    duration_threshold_to_alert_critical_in_s: Optional[float] = None,
    enable_print: bool = True,
    enable_log: bool = True,
    enabled: bool = True,
) -> Generator[float, None, None]:
    """Décorateur de contexte pour mesurer le temps d'exécution d'une fonction :
    https://www.docstring.fr/glossaire/with/"""
    if enabled:
        start_time = time.perf_counter()
        yield time.perf_counter() - start_time
        end_time = time.perf_counter()
        elapsed_time_conds = end_time - start_time

        if elapsed_time_conds >= duration_threshold_to_alert_info_in_s:
            to_print_and_log = f"{label} took: {elapsed_time_conds:.2f} seconds"

            log_timestamp = time.asctime(time.localtime(time.time()))

            previous_stack = inspect.stack(0)[2]
            file_name = previous_stack.filename
            line_number = previous_stack.lineno
            calling_file_name_and_line_number = file_name + ", line " + str(line_number)

            # pylint: disable=line-too-long
            if enable_print:

                severity_prefix = (
                    "!!! Critical !!\t"
                    if (
                        duration_threshold_to_alert_critical_in_s is not None
                        and elapsed_time_conds > duration_threshold_to_alert_critical_in_s
                    )
                    else (
                        "!!! Error !!\t"
                        if (
                            duration_threshold_to_alert_error_in_s is not None
                            and elapsed_time_conds > duration_threshold_to_alert_error_in_s
                        )
                        else (
                            "! Warning !\t"
                            if (
                                duration_threshold_to_alert_warning_in_s is not None
                                and elapsed_time_conds > duration_threshold_to_alert_warning_in_s
                            )
                            else ""
                        )
                    )
                )
                print(
                    log_timestamp + "\t" + calling_file_name_and_line_number + "\t" + severity_prefix + to_print_and_log
                )

            if enable_log:
                log_level = (
                    logging.CRITICAL
                    if (
                        duration_threshold_to_alert_critical_in_s is not None
                        and elapsed_time_conds > duration_threshold_to_alert_critical_in_s
                    )
                    else (
                        logging.ERROR
                        if (
                            duration_threshold_to_alert_error_in_s is not None
                            and elapsed_time_conds > duration_threshold_to_alert_error_in_s
                        )
                        else (
                            logging.WARNING
                            if (
                                duration_threshold_to_alert_warning_in_s is not None
                                and elapsed_time_conds > duration_threshold_to_alert_warning_in_s
                            )
                            else logging.INFO
                        )
                    )
                )
                logging.log(log_level, f"{calling_file_name_and_line_number} \t {to_print_and_log}")

    else:
        yield 0.0


def datetime_convenient_log_format(datetime_to_log: datetime.datetime, number_of_caracters_to_keep: int = 22) -> str:
    return str(datetime_to_log)[:number_of_caracters_to_keep]
