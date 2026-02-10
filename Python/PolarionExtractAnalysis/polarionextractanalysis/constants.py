from enum import Enum, auto


class PolarionWorkItemType(Enum):
    WORKITEMS = auto()


class PolarionAttributeType(Enum):
    STB = auto()
    SECONDREGARD = auto()
    FNC = auto()
    FAN_TITULAIRE = auto()
    FAN = auto()
    SCNRTEST = auto()
    CONSTAT = auto()
    SDT = auto()
    HEADING = auto()
    SFT = auto()


class PolarionSeverity(Enum):
    NON_BLOQUANTE = auto()
    BLOQUANTE_SANS_IMPACT_SECURITE = auto()
    BLOQUANTE_IMPACT_SECURITE = auto()


class PolarionStatus(Enum):
    DONE = auto()
