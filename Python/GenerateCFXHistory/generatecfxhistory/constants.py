from enum import auto

from typing import cast
from common import enums_utils


class State(enums_utils.NameBasedIntEnum):
    NOT_CREATED_YET = cast("State", auto())
    NO_VALUE = cast("State", auto())
    SUBMITTED = cast("State", auto())
    ANALYSED = cast("State", auto())
    ASSIGNED = cast("State", auto())
    RESOLVED = cast("State", auto())
    REJECTED = cast("State", auto())
    POSTPONED = cast("State", auto())
    VERIFIED = cast("State", auto())
    VALIDATED = cast("State", auto())
    UNKNOWN = cast("State", auto())
    CLOSED = cast("State", auto())
