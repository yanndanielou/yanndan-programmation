from enum import Enum, auto


class SeclabSide(Enum):
    BORD = auto
    SECLAB_ITSELF = auto
    SOL = auto


class CastType(Enum):
    UNICAST = auto
    MULTICAST = auto
    UNKNOWN = auto
