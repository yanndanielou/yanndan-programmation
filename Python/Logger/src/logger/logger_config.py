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
from collections import OrderedDict, defaultdict
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps

# from warnings import deprecated
from logging.handlers import RotatingFileHandler
from typing import ParamSpec, TypeVar, cast
from collections.abc import Callable
from warnings import deprecated

import humanize
import pandas
import psutil
from common import date_time_formats, file_name_utils

# pylint: enable=logging-not-lazy
# pylint: disable=logging-fstring-interpolation

DEFAULT_CALL_STACK_CONTEXT_VALUE = 1
DEFAULT_CALL_STACK_FRAME_VALUE = 2


log_counts_occurrences_per_level: dict[str, int] = defaultdict(int)
log_counts_warning_occurrences_per_file_and_line: dict[str, int] = defaultdict(int)
log_counts_errors_occurrences_per_file_and_line: dict[str, int] = defaultdict(int)
log_counts_exceptions_occurrences_per_file_and_line: dict[str, int] = defaultdict(int)


class RamUsageMonitor:

    @dataclass
    class Measure:
        timestamp: datetime.datetime | str
        ram_usage_int: int

        def __post_init__(self) -> None:
            self.ram_usage_human_readable = humanize.naturalsize(self.ram_usage_int)

    def __init__(self) -> None:
        self.output_file_path_with_extension = ""
        self.all_mesures_to_write: list[RamUsageMonitor.Measure] = []

    def set_output_file_name_without_extension(self, output_file_name_without_extension: str) -> None:
        self.output_file_path_with_extension = f"logs/{output_file_name_without_extension}"

        self.measure_now()

    def measure_now(self) -> "RamUsageMonitor.Measure":
        current_ram_int = cast(int, psutil.Process(os.getpid()).memory_info().rss)
        new_measure = RamUsageMonitor.Measure(
            timestamp=datetime.datetime.now(),  # noqa: DTZ005
            ram_usage_int=current_ram_int,
        )
        self.all_mesures_to_write.append(new_measure)
        return new_measure

    def append_pending_lines_to_file(self) -> None:
        print_and_log_info(
            f"Logger ram monitor usage: write {len(self.all_mesures_to_write)} pending lines to {self.output_file_path_with_extension}"
        )

        with pandas.ExcelWriter(self.output_file_path_with_extension + ".xlsx") as writer:
            pandas.DataFrame(
                [
                    OrderedDict(
                        {
                            "date": mesure_to_write.timestamp,
                            "As bytes": mesure_to_write.ram_usage_int,
                            "As human readable": mesure_to_write.ram_usage_human_readable,
                        }
                    )
                    for mesure_to_write in self.all_mesures_to_write
                ],
                index=None,
            ).to_excel(writer, sheet_name="RAM")

        self.all_mesures_to_write.clear()

    def save_and_close(self) -> None:
        self.measure_now()
        print_and_log_info(f"Logger ram monitor usage: save and close {self.output_file_path_with_extension}")
        self.append_pending_lines_to_file()
        print_and_log_info("Logger ram monitor usage: saved")


ram_usage_monitor = RamUsageMonitor()


class MessagesCounterHandler(logging.Handler):

    def __init__(self) -> None:
        super().__init__()
        self.disabled_for_unit_tests = False

    def emit(self, record: logging.LogRecord) -> None:
        if self.disabled_for_unit_tests:
            return
        if not record.message.startswith("create exception"):  # to avoid multiple entries for exceptions
            log_counts_occurrences_per_level[record.levelname] += 1
        if record.levelname == "ERROR":
            record_file_and_line = record.message.split(" \t")[0]
            log_counts_errors_occurrences_per_file_and_line[record_file_and_line] += 1
        if record.levelname == "WARNING":
            record_file_and_line = record.message.split(" \t")[0]
            log_counts_warning_occurrences_per_file_and_line[record_file_and_line] += 1


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
    to_print_and_log = "☠️ " + to_print_and_log

    # pylint: disable=line-too-long
    print(log_timestamp + "\t" + __get_calling_file_name_and_line_number() + "\t" + to_print_and_log)
    print(log_timestamp + "\t" + __get_calling_file_name_and_line_number() + "\t" + "Kill application")

    logging.critical(f"{__get_calling_file_name_and_line_number()} '\t' {to_print_and_log}")  # noqa: LOG015
    logging.critical(f"{__get_calling_file_name_and_line_number()} '\t' Kill application")  # noqa: LOG015
    sys.exit()


def print_and_log_info_if(condition: bool, to_print_and_log: str, do_not_print: bool = False) -> None:
    """Print in standard output and log in file as info level"""
    if condition:
        log_timestamp = time.asctime(time.localtime(time.time()))

        # pylint: disable=line-too-long
        if not do_not_print:
            print(log_timestamp + "\t" + __get_calling_file_name_and_line_number() + "\t" + to_print_and_log)
        logging.info(f"{__get_calling_file_name_and_line_number()} \t {to_print_and_log}")  # noqa: LOG015


def print_and_log_info(to_print_and_log: str, do_not_print: bool = False, print_ram_usage: bool = False) -> None:
    """Print in standard output and log in file as info level"""
    log_timestamp = time.asctime(time.localtime(time.time()))

    if print_ram_usage:
        measure = ram_usage_monitor.measure_now()
        to_print_and_log += f".Current ram usage: {measure.ram_usage_human_readable}"

    # pylint: disable=line-too-long
    if not do_not_print:
        print(log_timestamp + "\t" + __get_calling_file_name_and_line_number() + "\t" + to_print_and_log)
    logging.info(f"{__get_calling_file_name_and_line_number()} \t {to_print_and_log}")  # noqa: LOG015


def print_and_log_warning_if(condition: bool, to_print_and_log: str, do_not_print: bool = False) -> None:
    if condition:
        print_and_log_warning(
            to_print_and_log=to_print_and_log,
            do_not_print=do_not_print,
            call_stack_frame=3,
        )


def print_and_log_warning(
    to_print_and_log: str,
    do_not_print: bool = False,
    call_stack_frame: int = DEFAULT_CALL_STACK_FRAME_VALUE,
) -> None:
    """Print in standard output and log in file as info level"""
    log_timestamp = time.asctime(time.localtime(time.time()))

    # pylint: disable=line-too-long
    if not do_not_print:
        print(
            log_timestamp
            + "\t"
            + "⚠️"
            + "\t"
            + __get_calling_file_name_and_line_number(call_stack_frame=call_stack_frame)
            + "\t"
            + to_print_and_log
        )
    logging.warning(  # noqa: LOG015
        f"{__get_calling_file_name_and_line_number(call_stack_frame=call_stack_frame)} \t {to_print_and_log}"
    )


def print_and_log_exception(exception_to_print: Exception, additional_text: str | None = None) -> None:
    log_counts_exceptions_occurrences_per_file_and_line[
        __get_calling_file_name_and_line_number(call_stack_context=0)
    ] += 1

    if additional_text:
        to_print_and_log = f"Exception raised:{additional_text} "
        print_and_log_warning(to_print_and_log, call_stack_frame=3)

    print_and_log_error(to_print_and_log=f"Exception raised, content:{str(exception_to_print)}", call_stack_frame=3)
    print_and_log_warning(
        to_print_and_log=f"Exception raised, type:{exception_to_print.__class__.__name__}", call_stack_frame=3
    )

    log_timestamp = time.asctime(time.localtime(time.time()))
    print(log_timestamp + "\t" + __get_calling_file_name_and_line_number(call_stack_context=0) + "\t" + "!!ERROR!!")
    print(
        log_timestamp + "\t" + __get_calling_file_name_and_line_number(call_stack_context=0) + "\t !!EXCEPTION THROWN!!"
    )

    logging.exception(exception_to_print)  # noqa: LOG015


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
    to_print_and_log = "❌ " + to_print_and_log
    if not do_not_print:
        # print(log_timestamp + "\t" + "!!ERROR!!")
        # pylint: disable=line-too-long
        print(
            log_timestamp
            + "\t"
            + __get_calling_file_name_and_line_number(
                call_stack_context=call_stack_context, call_stack_frame=call_stack_frame
            )
            + "\t"
            + to_print_and_log
        )
    logging.error(f"{__get_calling_file_name_and_line_number(
                call_stack_context=call_stack_context, call_stack_frame=call_stack_frame
            )} \t {to_print_and_log}")


@contextmanager
def application_logger(
    application_name: str | None = None,
    logger_level: int = logging.INFO,
    log_file_suffix_before_extension: str | None = None,
) -> Generator[float, None, None]:

    previous_stack = inspect.stack(0)[2]
    file_name = previous_stack.filename
    line_number = previous_stack.lineno

    if not application_name:
        application_name = os.path.basename(os.path.dirname(file_name))

    logger_created, counting_handler = configure_logger_with_timestamp_log_file_suffix(
        log_file_name_prefix=application_name,
        logger_level=logger_level,
        log_file_suffix_before_extension=log_file_suffix_before_extension,
    )
    application_start_time = time.time()

    calling_file_name_and_line_number = file_name + ":" + str(line_number)

    at_beginning_log_timestamp = time.asctime(time.localtime(time.time()))
    to_print_and_log = f"{application_name} : application begin. Ram usage: {ram_usage_monitor.measure_now()}"
    print(at_beginning_log_timestamp + "\t" + calling_file_name_and_line_number + "\t" + to_print_and_log)
    logging.info(f"{calling_file_name_and_line_number} \t {to_print_and_log}")

    yield 0.0

    application_end_time = time.time()
    application_end_timestamp = time.asctime(time.localtime(time.time()))

    elapsed_time = application_end_time - application_start_time

    to_print_and_log_lines: list[str] = []
    to_print_and_log_lines.append(
        f"\nWarning stats: \n{'\n'.join(str(item[0])+ ': ' + str(item[1]) + " warning raised" for item in list(dict(sorted(log_counts_warning_occurrences_per_file_and_line.items(), key=lambda item: item[1])).items()))}"
    )
    to_print_and_log_lines.append(
        f"\nErrors stats: \n{'\n'.join(str(item[0])+ ': ' + str(item[1]) + " errors raised" for item in list(dict(sorted(log_counts_errors_occurrences_per_file_and_line.items(), key=lambda item: item[1])).items()))}"
    )
    to_print_and_log_lines.append(
        f"{application_name} : application end. Elapsed: {date_time_formats.format_duration_to_string(elapsed_time)} s. Final ram usage: {ram_usage_monitor.measure_now().ram_usage_human_readable}."
    )
    to_print_and_log_lines.append(
        f"Logger stats: \t{'\t'.join(str(item[0])+ ':' + str(item[1]) for item in list(log_counts_occurrences_per_level.items()))}"
    )
    if log_counts_exceptions_occurrences_per_file_and_line:
        to_print_and_log_lines.append("Exceptions logged:")
        to_print_and_log_lines += [
            str(item[0]) + ": " + str(item[1]) + " exception logged"
            for item in list(
                dict(
                    sorted(log_counts_exceptions_occurrences_per_file_and_line.items(), key=lambda item: item[1])
                ).items()
            )
        ]
    for to_print_and_log in to_print_and_log_lines:
        print(application_end_timestamp + "\t" + calling_file_name_and_line_number + "\t" + to_print_and_log)
        logging.info(f"{calling_file_name_and_line_number} \t {to_print_and_log}")

    logger_created.removeHandler(counting_handler)
    logging.root.removeHandler(counting_handler)
    ram_usage_monitor.save_and_close()


def configure_logger_with_timestamp_log_file_suffix(
    log_file_name_prefix: str,
    log_file_extension: str = "log",
    logger_level: int = logging.INFO,
    log_file_suffix_before_extension: str | None = None,
) -> tuple[logging.Logger, MessagesCounterHandler]:

    log_file_suffix_before_extension = (
        "" if not log_file_suffix_before_extension else f"_{log_file_suffix_before_extension}"
    )
    log_file_name_without_extension = f"{log_file_name_prefix}{file_name_utils.get_file_suffix_with_current_datetime()}{log_file_suffix_before_extension}"
    log_file_name_with_extension = f"{log_file_name_without_extension}.{log_file_extension}"
    ram_usage_monitor.set_output_file_name_without_extension("log_file_name_with_extension")
    return configure_logger_with_exact_file_name(log_file_name_with_extension, logger_level)


@deprecated("Use application logger instead")
def configure_logger_with_random_log_file_suffix(
    log_file_name_prefix: str, log_file_extension: str = "log", logger_level: int = logging.INFO
) -> tuple[logging.Logger, MessagesCounterHandler]:
    """Configure the logger with_random_log_file_suffix"""
    log_file_name = f"{log_file_name_prefix}_{str(random.randrange(100000))}.{log_file_extension}"
    return configure_logger_with_exact_file_name(log_file_name, logger_level)


def configure_logger_with_exact_file_name(
    log_file_name: str, logger_level: int = logging.INFO
) -> tuple[logging.Logger, MessagesCounterHandler]:
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

    return logger, counting_handler


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
    call_stack_context: int = DEFAULT_CALL_STACK_CONTEXT_VALUE,
    call_stack_frame: int = DEFAULT_CALL_STACK_FRAME_VALUE,
) -> Generator[float, None, None]:
    """Décorateur de contexte pour mesurer le temps d'exécution d'une fonction :
    https://www.docstring.fr/glossaire/with/"""
    if enabled:
        initial_ram = ram_usage_monitor.measure_now()

        previous_stack = inspect.stack(call_stack_context)[call_stack_frame]
        file_name = previous_stack.filename
        line_number = previous_stack.lineno
        calling_file_name_and_line_number = file_name + ":" + str(line_number)

        if inform_beginning:
            at_beginning_log_timestamp = time.asctime(time.localtime(time.time()))

            if monitor_ram_usage:
                to_print_and_log = f"{label} : begin. Initial ram usage {initial_ram.ram_usage_human_readable}"
            else:
                to_print_and_log = f"{label} : begin"

            if enable_print:
                print(at_beginning_log_timestamp + "\t" + calling_file_name_and_line_number + "\t" + to_print_and_log)

            if enable_log:
                logging.info(f"{calling_file_name_and_line_number} \t {to_print_and_log}")

        debut = time.perf_counter()
        yield time.perf_counter() - debut

        final_ram = ram_usage_monitor.measure_now()
        delta_rss_since_reference = final_ram.ram_usage_int - initial_ram.ram_usage_int
        fin = time.perf_counter()
        elapsed_time_seconds = fin - debut
        end_log_timestamp = time.asctime(time.localtime(time.time()))

        if monitor_ram_usage:
            to_print_and_log = f"{label} Elapsed: {date_time_formats.format_duration_to_string(elapsed_time_seconds)}. Final ram {final_ram.ram_usage_human_readable}. Delta ram : {humanize.naturalsize(delta_rss_since_reference)}"
        else:
            to_print_and_log = f"{label} Elapsed: {date_time_formats.format_duration_to_string(elapsed_time_seconds)}"

        # pylint: disable=line-too-long
        if enable_print:
            print(end_log_timestamp + "\t" + calling_file_name_and_line_number + "\t" + to_print_and_log)

        if enable_log:
            logging.info(f"{calling_file_name_and_line_number} \t {to_print_and_log}")
    else:
        yield 0.0


P = ParamSpec("P")
R = TypeVar("R")


def stopwatch_decorator(
    label: str | None = None,
    enable_print: bool = True,
    enable_log: bool = True,
    enabled: bool = True,
    inform_beginning: bool = False,
    monitor_ram_usage: bool = False,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            effective_label = label if label else func.__qualname__
            with stopwatch_with_label(
                label=effective_label,
                enable_print=enable_print,
                enable_log=enable_log,
                enabled=enabled,
                inform_beginning=inform_beginning,
                monitor_ram_usage=monitor_ram_usage,
                call_stack_frame=3,
            ):
                return func(*args, **kwargs)

        return wrapper

    return decorator


@contextmanager
def stopwatch_alert_if_exceeds_duration(
    label: str,
    duration_threshold_to_alert_info_in_s: float,
    duration_threshold_to_alert_warning_in_s: float | None = None,
    duration_threshold_to_alert_error_in_s: float | None = None,
    duration_threshold_to_alert_critical_in_s: float | None = None,
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
                    "☠️\t"
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
    prefix: str = "", suffix: str = "", previous_reference_rss_value_and_label: tuple[int, str] | None = None
) -> RamUsageMonitor.Measure:
    current_ram = ram_usage_monitor.measure_now()

    comparison_text = ""
    if previous_reference_rss_value_and_label:
        previous_reference_rss_value = previous_reference_rss_value_and_label[0]
        previous_reference_rss_label = previous_reference_rss_value_and_label[1]
        delta_rss_since_reference = current_ram.ram_usage_int - previous_reference_rss_value
        comparison_text = (
            f". Evolution since {previous_reference_rss_label} : {humanize.naturalsize(delta_rss_since_reference)}"
        )

    to_print_and_log = f"{prefix} current ram:{current_ram.ram_usage_human_readable} {comparison_text} {suffix}"

    log_timestamp = time.asctime(time.localtime(time.time()))

    # pylint: disable=line-too-long
    print(log_timestamp + "\t" + __get_calling_file_name_and_line_number() + "\t" + to_print_and_log)
    logging.info(f"{__get_calling_file_name_and_line_number()} \t {to_print_and_log}")

    return current_ram
