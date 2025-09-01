from typing import List, Optional, Any, cast

import ipaddress

from pandas import Series


class SubSystem:
    def __init__(self) -> None:
        pass


class Port:
    def __init__(self, raw_port: Optional[str | int]) -> None:
        pass


class Equipment:
    def __init__(self, subsystem: SubSystem) -> None:
        self.ip_addresses: List[ipaddress.IPv4Address] = []
        self.subsystem = subsystem


class EndPoint:
    def __init__(self) -> None:
        pass


class Source(EndPoint):

    class Builder:

        @staticmethod
        def build_with_row(row: Series) -> "NetworkFlowMatrixLine":
            subsystem_raw = row["src\nss-système"]
            equipment_raw = row["src\nÉquipement"]
            detail_raw = row["src Détail"]
            quantity_raw = row["src Qté	"]
            vlan_bord_raw = row["src VLAN Bord"]
            vlan_sol_raw = row["src VLAN Sol"]
            ip_raw = row["src IP"]
            nat_raw = row["src NAT	"]
            port_raw = row["src Port"]

            return NetworkFlowMatrixLine()

    def __init__(self) -> None:

        pass


class Destination(EndPoint):

    class Builder:

        @staticmethod
        def build_with_row(row: Series) -> "NetworkFlowMatrixLine":
            subsystem_raw = row["dst\nss-système"]
            equipment_raw = row["dst\nÉquipement"]
            detail_raw = row["dst Détail"]
            quantity_raw = row["dst Qté	"]
            vlan_bord_raw = row["dst VLAN Bord"]
            vlan_sol_raw = row["dst VLAN Sol"]
            ip_raw = row["dst IP"]
            nat_raw = row["dst NAT	"]
            port_raw = row["dst Port"]

            return NetworkFlowMatrixLine()

    def __init__(self) -> None:
        pass


class NetworkFlowMatrix:
    def __init__(self) -> None:
        self.lines: List[NetworkFlowMatrixLine] = []


class NetworkFlowMatrixLine:

    class Builder:

        @staticmethod
        def build_with_row(row: Series) -> "NetworkFlowMatrixLine":
            identifier_raw = cast(str, row["ID"])
            name_raw = cast(str, row["Lien de com."])
            sol_bord_raw = cast(str, row["S/B"])

            source = Source.Builder.build_with_row(row)
            destination = Destination.Builder.build_with_row(row)

            return NetworkFlowMatrixLine()

    def __init__(self) -> None:
        pass


class NetworkFlowMacro:
    def __init__(self) -> None:
        pass


class NetworkFlow:
    def __init__(self) -> None:
        pass
