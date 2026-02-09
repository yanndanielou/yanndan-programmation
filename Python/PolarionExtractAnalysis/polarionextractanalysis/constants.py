from enum import Enum, auto


class PolarionWorkItemType(Enum):
    WORKITEMS = auto()


class PolarionAttributeType(Enum):
    STB = auto()


class PolarionSeverity(Enum):
    NON_BLOQUANTE = auto()


class PolarionStatus(Enum):
    DONE = auto()
