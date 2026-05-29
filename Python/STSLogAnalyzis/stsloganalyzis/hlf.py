import datetime
from common import time_utils


def decode_hlf_to_datetime(time_field_value: int, time_offset_value: int, decade_field_value: int, day_on_decade_field_value: int) -> datetime.datetime:

    # Calculate the start year of the decade
    start_year = 2000 + (decade_field_value * 10)

    # Calculate the date by adding the day on decade to start of the decade
    decade_date = datetime.datetime(start_year, 1, 1) + datetime.timedelta(days=day_on_decade_field_value)

    # Calculate time in hours, minutes, and seconds from time_field_value
    total_seconds = time_field_value / 10  # tenths of a second to seconds
    hours, minutes, seconds = time_utils.get_hour_minute_seconds_from_total_seconds(total_seconds=total_seconds)

    # Calculate the time offset:
    offset_hours = time_offset_value // 36000
    offset_minutes = (time_offset_value % 36000) // 600

    # Apply the offset for local time
    local_time = decade_date + datetime.timedelta(hours=hours - offset_hours, minutes=minutes - offset_minutes, seconds=seconds)

    return local_time
