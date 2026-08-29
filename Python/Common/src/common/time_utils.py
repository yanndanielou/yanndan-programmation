from typing import Tuple


def get_hour_minute_seconds_from_total_seconds(total_seconds: int) -> Tuple[int, int, int]:
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = total_seconds % 60

    return (hours, minutes, seconds)


def get_hour_minute_seconds_milliseconds_from_total_milliseconds(total_milliseconds: int) -> Tuple[int, int, int, int]:
    total_seconds = total_milliseconds // 1000

    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = total_seconds % 60
    milliseconds = total_milliseconds % 1000

    return (hours, minutes, seconds, milliseconds)
