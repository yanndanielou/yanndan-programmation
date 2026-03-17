from enum import Enum, auto


class CastType(Enum):
    UNICAST = auto()
    MULTICAST = auto()
    UNKNOWN = auto()


class MatrixFlowModificationType(Enum):
    D = "DELETED"
    A = "ADDED"
    M = "MODIFIED"


class ProdMigrationEssai(Enum):
    P = "PRODUCTION"
    M = "MIGRATION"
    ET = "ESSAIS_TEMPORAIRE"


ALL_USED_TRAINS_IDS = list(range(1, 131 + 1))
TO_IGNORE_TRAINS_IDS = [511, 2047]

OUTPUT_PARENT_DIRECTORY_NAME = "Output"
