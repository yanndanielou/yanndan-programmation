from enum import Enum, auto


class SeclabSide(Enum):
    BORD = auto
    SECLAB_ITSELF = auto
    SOL = auto


class CastType(Enum):
    UNICAST = auto
    MULTICAST = auto
    UNKNOWN = auto


ALL_USED_TRAINS_IDS = list(range(1, 131 + 1))
TO_IGNORE_TRAINS_IDS = [511, 2047]

OUTPUT_PARENT_DIRECTORY_NAME = "Output"
