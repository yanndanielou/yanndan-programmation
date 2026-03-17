from enum import Enum, auto


class NetworkEntityProvider(Enum):
    STS = auto()
    INFRANET = auto()
    INFRACOM = auto()
    INFRACOM_OR_INFRANET = auto()


SNCF_NETWORKS = [NetworkEntityProvider.INFRACOM, NetworkEntityProvider.INFRACOM_OR_INFRANET, NetworkEntityProvider.INFRANET]
