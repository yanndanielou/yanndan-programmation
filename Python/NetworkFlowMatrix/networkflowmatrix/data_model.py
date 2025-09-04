import ipaddress
from dataclasses import dataclass, field
from typing import Any, List, Optional, Set, Tuple, cast, Dict

import pandas
from logger import logger_config

all_equipments_names: Set[str] = set()
all_equipments_names_with_subsystem: set[Tuple[str, str]] = set()


class SubSystemInFlowMatrix:
    all_instances: List["SubSystemInFlowMatrix"] = []
    all_instances_by_name: Dict[str, "SubSystemInFlowMatrix"] = {}

    @staticmethod
    def is_existing_by_name(name: str) -> bool:
        return name in SubSystemInFlowMatrix.all_instances_by_name

    @staticmethod
    def get_existing_by_name(name: str) -> Optional["SubSystemInFlowMatrix"]:
        if SubSystemInFlowMatrix.is_existing_by_name(name):
            return SubSystemInFlowMatrix.all_instances_by_name[name]
        return None

    @staticmethod
    def get_or_create_if_not_exist_by_name(name: str) -> "SubSystemInFlowMatrix":
        if SubSystemInFlowMatrix.is_existing_by_name(name):
            return SubSystemInFlowMatrix.all_instances_by_name[name]
        subsystem = SubSystemInFlowMatrix(name=name)
        SubSystemInFlowMatrix.all_instances_by_name[name] = subsystem
        SubSystemInFlowMatrix.all_instances.append(subsystem)

        return subsystem

    def __init__(self, name: str) -> None:
        self.all_equipments: List["EquipmentInFLoxMatrix"] = []
        self.name = name
        SubSystemInFlowMatrix.all_instances.append(self)


class PortInFLowMatrix:
    def __init__(self, raw_port: Optional[str | int]) -> None:
        pass


class EquipmentInFLoxMatrix:
    all_instances: List["EquipmentInFLoxMatrix"] = []
    all_instances_by_name: Dict[str, "EquipmentInFLoxMatrix"] = {}

    @staticmethod
    def is_existing_by_name(name: str) -> bool:
        return name in EquipmentInFLoxMatrix.all_instances_by_name

    @staticmethod
    def get_existing_by_name(name: str) -> Optional["EquipmentInFLoxMatrix"]:
        if EquipmentInFLoxMatrix.is_existing_by_name(name):
            return EquipmentInFLoxMatrix.all_instances_by_name[name]
        return None

    @staticmethod
    def get_or_create_if_not_exist_by_name(name: str) -> "EquipmentInFLoxMatrix":
        if EquipmentInFLoxMatrix.is_existing_by_name(name):
            return EquipmentInFLoxMatrix.all_instances_by_name[name]
        equipment = EquipmentInFLoxMatrix(name=name)
        EquipmentInFLoxMatrix.all_instances_by_name[name] = equipment
        EquipmentInFLoxMatrix.all_instances.append(equipment)
        return equipment

    def __init__(self, name: str) -> None:
        self.ip_addresses: List[ipaddress.IPv4Address] = []
        self.all_subsystems: List[SubSystemInFlowMatrix] = []
        self.name = name


@dataclass
class FlowEndPoint:
    subsystem_raw: str
    equipment_cell_raw: str
    detail_raw: str
    quantity_raw: str
    vlan_bord_raw: str
    vlan_sol_raw: str
    ip_raw: Optional[str]
    nat_raw: str
    port_raw: str

    def __post_init__(self) -> None:
        if not isinstance(self.ip_raw, str):
            self.ip_raw = None

        self.raw_ip_addresses = self.ip_raw.split("\n") if self.ip_raw else []
        # self.ip_address = [ipaddress.IPv4Address(raw_ip_raw) for raw_ip_raw in self.raw_ip_addresses]

        self.subsystem_detected_in_flow_matrix = SubSystemInFlowMatrix.get_or_create_if_not_exist_by_name(self.subsystem_raw)
        self.equipment_detected_in_flow_matrix: List[EquipmentInFLoxMatrix] = []

        self.equipments_names = self.equipment_cell_raw.split("\n")

        for equipments_name in self.equipments_names:
            all_equipments_names.add(equipments_name)
            self.equipment_detected_in_flow_matrix.append(EquipmentInFLoxMatrix.get_or_create_if_not_exist_by_name(name=equipments_name))
        self.equipments_names = [equipment_name.lstrip().rstrip() for equipment_name in self.equipment_cell_raw.split("\n") if equipment_name.lstrip().rstrip() != ""]
        # self.equipments_names.remove("\n")
        for equipment_name in self.equipments_names:
            all_equipments_names_with_subsystem.add((equipment_name, self.subsystem_raw))
            assert equipment_name
            assert len(equipment_name.split()) > 0


@dataclass
class FlowSource(FlowEndPoint):

    class Builder:

        @staticmethod
        def build_with_row(row: pandas.Series) -> "FlowSource":
            subsystem_raw = row["src \nss-système"]
            equipment_raw = row["src \nÉquipement"]
            detail_raw = row["src Détail"]
            quantity_raw = row["src Qté"]
            vlan_bord_raw = row["src \nVLAN Bord"]
            vlan_sol_raw = row["src \nVLAN Sol"]
            ip_raw = row["src \nIP"]
            nat_raw = row["src NAT"]
            port_raw = row["src Port"]

            return FlowSource(
                detail_raw=detail_raw,
                equipment_cell_raw=equipment_raw,
                ip_raw=ip_raw,
                nat_raw=nat_raw,
                port_raw=port_raw,
                quantity_raw=quantity_raw,
                subsystem_raw=subsystem_raw,
                vlan_bord_raw=vlan_bord_raw,
                vlan_sol_raw=vlan_sol_raw,
            )


@dataclass
class FlowDestination(FlowEndPoint):

    group_multicast_raw: str
    cast_raw: str

    class Builder:

        @staticmethod
        def build_with_row(row: pandas.Series) -> "FlowDestination":
            subsystem_raw = row["dst \nss-système"]
            equipments_raw = row["dst \nÉquipement"]
            detail_raw = row["dst\nDétail"]
            quantity_raw = row["dst \nQté"]
            vlan_bord_raw = row["dst \nVLAN Bord"]
            vlan_sol_raw = row["dst \nVLAN Sol"]
            ip_raw = row["Dst \nIP"]
            nat_raw = row["dst NAT"]
            group_multicast_raw = row["dst Groupe\nMCast"]
            port_raw = row["dst\nPort"]
            cast_raw = row["dst\ncast"]

            return FlowDestination(
                detail_raw=detail_raw,
                equipment_cell_raw=equipments_raw,
                ip_raw=ip_raw,
                nat_raw=nat_raw,
                port_raw=port_raw,
                quantity_raw=quantity_raw,
                subsystem_raw=subsystem_raw,
                vlan_bord_raw=vlan_bord_raw,
                vlan_sol_raw=vlan_sol_raw,
                group_multicast_raw=group_multicast_raw,
                cast_raw=cast_raw,
            )


@dataclass
class NetworkFlowMatrix:
    network_flow_matrix_lines: List["NetworkFlowMatrixLine"]

    class Builder:

        @staticmethod
        def build_with_excel_file(excel_file_full_path: str, sheet_name: str = "Matrice_de_Flux_SITE") -> "NetworkFlowMatrix":
            main_data_frame = pandas.read_excel(excel_file_full_path, skiprows=[0, 1, 2, 3, 4], sheet_name=sheet_name)
            logger_config.print_and_log_info(f"Flow matrix {excel_file_full_path} has {len(main_data_frame)} items")
            logger_config.print_and_log_info(f"Flow matrix {excel_file_full_path} columns  {main_data_frame.columns[:4]} ...")

            network_flow_matrix_lines: List[NetworkFlowMatrixLine] = []

            for _, row in main_data_frame.iterrows():
                network_flow_matrix_line = NetworkFlowMatrixLine.Builder.build_with_row(row=row)
                network_flow_matrix_lines.append(network_flow_matrix_line)

            return NetworkFlowMatrix(network_flow_matrix_lines)


@dataclass
class NetworkFlowMatrixLine:
    identifier_raw: str
    name_raw: str
    sol_bord_raw: str
    seclab_raw: str
    traffic_direction_raw: str
    type_raw: str
    protocole_applicative_raw: str
    protocole_transport_raw: str

    source: FlowSource
    destination: FlowDestination

    class Builder:

        @staticmethod
        def build_with_row(row: pandas.Series) -> "NetworkFlowMatrixLine":
            identifier_raw = cast(str, row["ID"])
            name_raw = cast(str, row["Lien de com."])
            sol_bord_raw = cast(str, row["S/B"])

            protocole_applicative_raw = row["Protocole\nApplicatif"]
            protocole_transport_raw = row["Protocole \nde Transport"]
            type_raw = row["Type flux\n(Fonc/Admin)"]
            traffic_direction_raw = row["Sens du Trafic\n(uni, bidir)"]
            seclab_raw = row["Seclab"]

            source = FlowSource.Builder.build_with_row(row)
            destination = FlowDestination.Builder.build_with_row(row)

            network_flow_matrix_line = NetworkFlowMatrixLine(
                destination=destination,
                identifier_raw=identifier_raw,
                name_raw=name_raw,
                sol_bord_raw=sol_bord_raw,
                source=source,
                seclab_raw=seclab_raw,
                protocole_applicative_raw=protocole_applicative_raw,
                protocole_transport_raw=protocole_transport_raw,
                traffic_direction_raw=traffic_direction_raw,
                type_raw=type_raw,
            )

            return network_flow_matrix_line


class NetworkFlowMacro:
    def __init__(self) -> None:
        pass


class NetworkFlow:
    def __init__(self) -> None:
        pass
