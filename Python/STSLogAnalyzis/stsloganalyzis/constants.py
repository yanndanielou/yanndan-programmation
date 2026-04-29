from typing import List

FIELD_FULL_NAMES_TO_EXCLUDE_IN_REPORTS = ["Time", "TimeOffset", "Decade", "DayOnDecade"]
FIELD_NAMES_PREFIXES_TO_EXCLUDE_IN_REPORTS = ["Padding_"]

STATE_FIELD_NAME = "State"

FIELD_TYPE = float | int | bool | str | List[int] | List[str] | List[bool]
