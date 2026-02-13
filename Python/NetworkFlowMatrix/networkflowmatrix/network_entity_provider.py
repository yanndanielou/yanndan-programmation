from enum import Enum, auto
from typing import TYPE_CHECKING


class NetworkEntityProvider(Enum):
    STS = auto()
    INFRANET = auto()
    INFRACOM = auto()
    INFRACOM_OR_INFRANET = auto()
