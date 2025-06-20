from enum import auto, Enum

from common import enums_utils


class State(enums_utils.NameBasedIntEnum):
    NOT_CREATED_YET = auto()
    NO_VALUE = auto()
    SUBMITTED = auto()
    ANALYSED = auto()
    ASSIGNED = auto()
    RESOLVED = auto()
    REJECTED = auto()
    POSTPONED = auto()
    VERIFIED = auto()
    VALIDATED = auto()
    CLOSED = auto()
