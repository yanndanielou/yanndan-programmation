"""logger"""

import datetime
from warnings import deprecated


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
from typing import Optional, Tuple, cast, Dict

import humanize
import psutil
from collections import defaultdict

from common import date_time_formats, file_name_utils

# pylint: enable=logging-not-lazy
# pylint: disable=logging-fstring-interpolation

DEFAULT_CALL_STACK_CONTEXT_VALUE = 1
DEFAULT_CALL_STACK_FRAME_VALUE = 2

log_counts_occurences_per_level: Dict[str, int] = defaultdict(int)
log_counts_errors_occurences_per_file_and_line: Dict[str, int] = defaultdict(int)
log_counts_exceptions_occurences_per_file_and_line: Dict[str, int] = defaultdict(int)


class MessagesCounterHandler(logging.Handler):

    def __init__(self) -> None:
        super(MessagesCounterHandler, self).__init__()

    def emit(self, record: logging.LogRecord) -> None:
        log_counts_occurences_per_level[record.levelname] += 1
        if record.levelname == "ERROR":
            record_file_and_line = record.message.split(" \t")[0]
            log_counts_errors_occurences_per_file_and_line[record_file_and_line] += 1


def __get_calling_file_name_and_line_number(
    call_stack_context: int = DEFAULT_CALL_STACK_CONTEXT_VALUE,
    call_stack_frame: int = DEFAULT_CALL_STACK_FRAME_VALUE,
) -> str:
    previous_stack = inspect.stack(call_stack_context)[call_stack_frame]
    file_name = previous_stack.filename
    line_number = previous_stack.lineno
    return file_name + ":" + str(line_number)


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
    print(log_timestamp + "\t" + __get_calling_file_name_and_line_number() + "\t" + "Kill application")

    logging.critical(f"{__get_calling_file_name_and_line_number()} '\t' {to_print_and_log}")
    logging.critical(f"{__get_calling_file_name_and_line_number()} '\t' Kill application")
    sys.exit()


def print_and_log_info_if(condition: bool, to_print_and_log: str) -> None:
    """Print in standard output and log in file as info level"""
    if condition:
        log_timestamp = time.asctime(time.localtime(time.time()))

        # pylint: disable=line-too-long
        print(log_timestamp + "\t" + __get_calling_file_name_and_line_number() + "\t" + to_print_and_log)
        logging.info(f"{__get_calling_file_name_and_line_number()} \t {to_print_and_log}")


def print_and_log_info(to_print_and_log: str, do_not_print: bool = False) -> None:
    """Print in standard output and log in file as info level"""
    log_timestamp = time.asctime(time.localtime(time.time()))

    # pylint: disable=line-too-long
    if not do_not_print:
        print(log_timestamp + "\t" + __get_calling_file_name_and_line_number() + "\t" + to_print_and_log)
    logging.info(f"{__get_calling_file_name_and_line_number()} \t {to_print_and_log}")


def print_and_log_warning(to_print_and_log: str, do_not_print: bool = False) -> None:
    """Print in standard output and log in file as info level"""
    log_timestamp = time.asctime(time.localtime(time.time()))

    # pylint: disable=line-too-long
    if not do_not_print:
        print(log_timestamp + "\t" + __get_calling_file_name_and_line_number() + "\t" + str() + to_print_and_log)
    logging.warning(f"{__get_calling_file_name_and_line_number()} \t {to_print_and_log}")


def print_and_log_exception(exception_to_print: Exception, additional_text: Optional[str] = None) -> None:
    log_counts_exceptions_occurences_per_file_and_line[
        __get_calling_file_name_and_line_number(call_stack_context=0)
    ] += 1

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


def print_and_log_error_if(condition: bool, to_print_and_log: str, do_not_print: bool = False) -> None:
    if condition:
        print_and_log_error(
            to_print_and_log=to_print_and_log,
            do_not_print=do_not_print,
            call_stack_frame=3,
        )


def print_and_log_error(
    to_print_and_log: str,
    do_not_print: bool = False,
    call_stack_context: int = DEFAULT_CALL_STACK_CONTEXT_VALUE,
    call_stack_frame: int = DEFAULT_CALL_STACK_FRAME_VALUE,
) -> None:
    """Print in standard output and log in file as error level"""
    log_timestamp = time.asctime(time.localtime(time.time()))
    if not do_not_print:
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
    logging.error(
        f"{__get_calling_file_name_and_line_number(
                call_stack_context=call_stack_context, call_stack_frame=call_stack_frame
            )} \t {to_print_and_log}"
    )


@contextmanager
def application_logger(application_name: str, logger_level: int = logging.INFO) -> Generator[float, None, None]:

    configure_logger_with_timestamp_log_file_suffix(log_file_name_prefix=application_name, logger_level=logger_level)
    previous_stack = inspect.stack(0)[2]
    file_name = previous_stack.filename
    line_number = previous_stack.lineno
    application_start_time = time.time()

    calling_file_name_and_line_number = file_name + ":" + str(line_number)

    at_beginning_log_timestamp = time.asctime(time.localtime(time.time()))
    to_print_and_log = f"{application_name} : application begin"
    print(at_beginning_log_timestamp + "\t" + calling_file_name_and_line_number + "\t" + to_print_and_log)
    logging.info(f"{calling_file_name_and_line_number} \t {to_print_and_log}")

    yield 0.0

    application_end_time = time.time()
    application_end_timestamp = time.asctime(time.localtime(time.time()))

    elapsed_time = application_end_time - application_start_time
    to_print_and_log = f"\nErrors stats: \n{'\n'.join(str(item[0])+ ': ' + str(item[1]) + " errors raised" for item in list(dict(sorted(log_counts_errors_occurences_per_file_and_line.items(), key=lambda item: item[1])).items()))}\n{application_name} : application end. Elapsed: {date_time_formats.format_duration_to_string(elapsed_time)} s.\nLogger stats: \t{'\t'.join(str(item[0])+ ':' + str(item[1]) for item in list(log_counts_occurences_per_level.items()))}"
    if log_counts_exceptions_occurences_per_file_and_line:
        to_print_and_log += f"\nExceptions logged\n  {
            "\n".join(
                str(item[0]) + ": " + str(item[1]) + " exception logged"
                for item in list(
                    dict(
                        sorted(log_counts_exceptions_occurences_per_file_and_line.items(), key=lambda item: item[1])
                    ).items()
                )
            )
        }"
    print(application_end_timestamp + "\t" + calling_file_name_and_line_number + "\t" + to_print_and_log)
    logging.info(f"{calling_file_name_and_line_number} \t {to_print_and_log}")


def configure_logger_with_timestamp_log_file_suffix(
    log_file_name_prefix: str, log_file_extension: str = "log", logger_level: int = logging.INFO
) -> None:
    log_file_name = (
        f"{log_file_name_prefix}_{file_name_utils.get_file_suffix_with_current_datetime()}.{log_file_extension}"
    )
    configure_logger_with_exact_file_name(log_file_name, logger_level)


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
    print(time.asctime(time.localtime(time.time())) + "\t" + "Log file name:" + log_file_name)

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

    # Create logger
    logger = logging.getLogger()

    # Add the custom handler
    counting_handler = MessagesCounterHandler()
    logger.addHandler(counting_handler)


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


@deprecated("Kept just in case")
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
    label: str,
    enable_print: bool = True,
    enable_log: bool = True,
    enabled: bool = True,
    inform_beginning: bool = False,
    monitor_ram_usage: bool = False,
) -> Generator[float, None, None]:
    """Décorateur de contexte pour mesurer le temps d'exécution d'une fonction :
    https://www.docstring.fr/glossaire/with/"""
    if enabled:
        initial_ram_rss = cast(int, psutil.Process(os.getpid()).memory_info().rss)

        previous_stack = inspect.stack(0)[2]
        file_name = previous_stack.filename
        line_number = previous_stack.lineno
        calling_file_name_and_line_number = file_name + ":" + str(line_number)

        if inform_beginning:
            at_beginning_log_timestamp = time.asctime(time.localtime(time.time()))

            if monitor_ram_usage:
                to_print_and_log = f"{label} : begin. Initial ram usage {humanize.naturalsize(initial_ram_rss)}"
            else:
                to_print_and_log = f"{label} : begin"

            if enable_print:
                print(at_beginning_log_timestamp + "\t" + calling_file_name_and_line_number + "\t" + to_print_and_log)

            if enable_log:
                logging.info(f"{calling_file_name_and_line_number} \t {to_print_and_log}")

        debut = time.perf_counter()
        yield time.perf_counter() - debut

        final_ram_rss = cast(int, psutil.Process(os.getpid()).memory_info().rss)
        delta_rss_since_reference = final_ram_rss - initial_ram_rss
        fin = time.perf_counter()
        elapsed_time_seconds = fin - debut
        if monitor_ram_usage:
            to_print_and_log = f"{label} Elapsed: {date_time_formats.format_duration_to_string(elapsed_time_seconds)}. Final ram {humanize.naturalsize(final_ram_rss)}. Delta ram : {humanize.naturalsize(delta_rss_since_reference)}"
        else:
            to_print_and_log = f"{label} Elapsed: {date_time_formats.format_duration_to_string(elapsed_time_seconds)}"

        end_log_timestamp = time.asctime(time.localtime(time.time()))

        # pylint: disable=line-too-long
        if enable_print:
            print(end_log_timestamp + "\t" + calling_file_name_and_line_number + "\t" + to_print_and_log)

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
        elapsed_time_seconds = end_time - start_time

        if elapsed_time_seconds >= duration_threshold_to_alert_info_in_s:
            to_print_and_log = f"{label} took: {date_time_formats.format_duration_to_string(elapsed_time_seconds)}"

            log_timestamp = time.asctime(time.localtime(time.time()))

            previous_stack = inspect.stack(0)[2]
            file_name = previous_stack.filename
            line_number = previous_stack.lineno
            calling_file_name_and_line_number = file_name + ":" + str(line_number)

            # pylint: disable=line-too-long
            if enable_print:

                severity_prefix = (
                    "!!! Critical !!\t"
                    if (
                        duration_threshold_to_alert_critical_in_s is not None
                        and elapsed_time_seconds > duration_threshold_to_alert_critical_in_s
                    )
                    else (
                        "!!! Error !!\t"
                        if (
                            duration_threshold_to_alert_error_in_s is not None
                            and elapsed_time_seconds > duration_threshold_to_alert_error_in_s
                        )
                        else (
                            "! Warning !\t"
                            if (
                                duration_threshold_to_alert_warning_in_s is not None
                                and elapsed_time_seconds > duration_threshold_to_alert_warning_in_s
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
                        and elapsed_time_seconds > duration_threshold_to_alert_critical_in_s
                    )
                    else (
                        logging.ERROR
                        if (
                            duration_threshold_to_alert_error_in_s is not None
                            and elapsed_time_seconds > duration_threshold_to_alert_error_in_s
                        )
                        else (
                            logging.WARNING
                            if (
                                duration_threshold_to_alert_warning_in_s is not None
                                and elapsed_time_seconds > duration_threshold_to_alert_warning_in_s
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


def print_and_log_current_ram_usage(
    prefix: str = "", suffix: str = "", previous_reference_rss_value_and_label: Optional[Tuple[int, str]] = None
) -> int:
    current_ram_rss = cast(int, psutil.Process(os.getpid()).memory_info().rss)

    comparison_text = ""
    if previous_reference_rss_value_and_label:
        previous_reference_rss_value = previous_reference_rss_value_and_label[0]
        previous_reference_rss_label = previous_reference_rss_value_and_label[1]
        delta_rss_since_reference = current_ram_rss - previous_reference_rss_value
        comparison_text = (
            f". Evolution since {previous_reference_rss_label} : {humanize.naturalsize(delta_rss_since_reference)}"
        )

    to_print_and_log = f"{prefix} current ram:{humanize.naturalsize(current_ram_rss)} {comparison_text} {suffix}"

    log_timestamp = time.asctime(time.localtime(time.time()))

    # pylint: disable=line-too-long
    print(log_timestamp + "\t" + __get_calling_file_name_and_line_number() + "\t" + to_print_and_log)
    logging.info(f"{__get_calling_file_name_and_line_number()} \t {to_print_and_log}")

    return current_ram_rss
