from typing import List

FIELD_FULL_NAMES_TO_EXCLUDE_IN_REPORTS = [
    "Time",
    "TimeOffset",
    "Decade",
    "DayOnDecade",
    "id",
]
FIELD_NAMES_PREFIXES_TO_EXCLUDE_IN_REPORTS = ["Padding_"]
FIELD_NAMES_POSTFIXES_TO_EXCLUDE_IN_REPORTS = ["raw"]

STATE_FIELD_NAME = "State"

HUMAN_READABLE_FIELD_TYPE = float | int | bool | str

FIELD_TYPE = HUMAN_READABLE_FIELD_TYPE | List[int] | List[str] | List[bool]
