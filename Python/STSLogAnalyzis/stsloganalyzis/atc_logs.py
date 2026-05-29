from dataclasses import dataclass
from common import time_utils
from stsloganalyzis import hlf
import datetime


class Equipment:
    def __init__(self, raw_name: str) -> None:
        self.name = raw_name


@dataclass
class VariableState:
    equipment: Equipment
    variable_name: str
    variable_value: str | int | bool
    timestamp: datetime.datetime


def pert_variable_to_timestamp(c_heure: int, c_decalage: int, c_decenie: int, c_jour: int) -> datetime.datetime:
    """
    Heure de l horodate en milliseconde
    Decalage de l heure (GMT + été hiver) en milliseconde
    """

    # Calculate the start year of the decade
    start_year = 2000 + (c_decenie * 10)

    # Calculate the date by adding the day on decade to start of the decade
    decade_date = datetime.datetime(start_year, 1, 1) + datetime.timedelta(days=c_jour)

    # Calculate the time offset:
    c_decalage_seconds = c_decalage / 1000
    offset_hours = c_decalage_seconds // 3600
    offset_minutes = (c_decalage_seconds % 3600) // 60

    # timestamp = hlf.decode_hlf_to_datetime(time_field_value=c_heure / 10, time_offset_value=c_decalage, decade_field_value=c_decenie, day_on_decade_field_value=c_jour)
    total_milliseconds = c_heure + c_decalage

    hours, minutes, seconds, milliseconds = time_utils.get_hour_minute_seconds_milliseconds_from_total_milliseconds(total_milliseconds=total_milliseconds)

    # Apply the offset for local time
    local_time = decade_date + datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)

    return local_time
