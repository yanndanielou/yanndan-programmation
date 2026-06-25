# -*-coding:Utf-8 -*
"""Date time formats"""

from dateutil import parser
from datetime import timedelta


def format_duration_between_timestamps_str_to_string(start_timestamp_str: str, end_timestamp_str: str) -> str:
    start_timestamp = parser.parse(start_timestamp_str)
    end_timestamp = parser.parse(end_timestamp_str)
    duration_timedelta = end_timestamp - start_timestamp
    return format_duration_timedelta_to_string(duration_timedelta)


def format_duration_timedelta_to_string(duration_timedelta: timedelta) -> str:
    return format_duration_to_string(duration_timedelta.seconds + duration_timedelta.microseconds / 1000000)


def format_duration_to_string(duration_in_seconds_as_float: float) -> str:
    """Formatter for duration"""
    milliseconds = int(duration_in_seconds_as_float * 1000) % 1000

    duration_in_seconds_as_int = int(duration_in_seconds_as_float)

    hours, remainder = divmod(duration_in_seconds_as_int, 3600)
    minutes, seconds = divmod(remainder, 60)

    result = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{int(milliseconds):03}"

    return result
