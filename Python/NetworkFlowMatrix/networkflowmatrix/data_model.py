import ipaddress
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple, cast, Dict

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
        self.all_equipments_detected_in_flow_matrix: List["EquipmentInFLowMatrix"] = []
        self.name = name


class PortInFLowMatrix:
    def __init__(self, raw_port: Optional[str | int]) -> None:
        pass


class EquipmentInFLowMatrix:
    all_instances: List["EquipmentInFLowMatrix"] = []
    all_instances_by_name: Dict[str, "EquipmentInFLowMatrix"] = {}

    @staticmethod
    def is_existing_by_name(name: str) -> bool:
        return name in EquipmentInFLowMatrix.all_instances_by_name

    @staticmethod
    def get_existing_by_name(name: str) -> Optional["EquipmentInFLowMatrix"]:
        if EquipmentInFLowMatrix.is_existing_by_name(name):
            return EquipmentInFLowMatrix.all_instances_by_name[name]
        return None

    @staticmethod
    def get_or_create_if_not_exist_by_name(name: str, subsystem_detected_in_flow_matrix: SubSystemInFlowMatrix) -> "EquipmentInFLowMatrix":
        if EquipmentInFLowMatrix.is_existing_by_name(name):
            equipment = EquipmentInFLowMatrix.all_instances_by_name[name]
            if subsystem_detected_in_flow_matrix not in equipment.all_subsystems_detected_in_flow_matrix:
                equipment.all_subsystems_detected_in_flow_matrix.append(subsystem_detected_in_flow_matrix)

            if equipment not in subsystem_detected_in_flow_matrix.all_equipments_detected_in_flow_matrix:
                subsystem_detected_in_flow_matrix.all_equipments_detected_in_flow_matrix.append(equipment)
            return equipment
        equipment = EquipmentInFLowMatrix(name=name, subsystem_detected_in_flow_matrix=subsystem_detected_in_flow_matrix)
        EquipmentInFLowMatrix.all_instances_by_name[name] = equipment
        EquipmentInFLowMatrix.all_instances.append(equipment)
        subsystem_detected_in_flow_matrix.all_equipments_detected_in_flow_matrix.append(equipment)
        return equipment

    def __init__(self, name: str, subsystem_detected_in_flow_matrix: SubSystemInFlowMatrix) -> None:
        self.ip_addresses: List[ipaddress.IPv4Address] = []
        self.all_subsystems_detected_in_flow_matrix: List[SubSystemInFlowMatrix] = [subsystem_detected_in_flow_matrix]

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

        self.subsystem_detected_in_flow_matrix = SubSystemInFlowMatrix.get_or_create_if_not_exist_by_name(self.subsystem_raw.strip().upper())
        self.equipments_detected_in_flow_matrix: List[EquipmentInFLowMatrix] = []

        self.equipments_names = [equipment_name.strip().upper() for equipment_name in self.equipment_cell_raw.split("\n") if equipment_name.strip() != ""]

        for equipment_name in self.equipments_names:
            assert equipment_name
            assert len(equipment_name.split()) > 0
            all_equipments_names.add(equipment_name)
            equipment_detected_in_flow_matrix = EquipmentInFLowMatrix.get_or_create_if_not_exist_by_name(name=equipment_name, subsystem_detected_in_flow_matrix=self.subsystem_detected_in_flow_matrix)
            self.equipments_detected_in_flow_matrix.append(equipment_detected_in_flow_matrix)
            all_equipments_names_with_subsystem.add((equipment_name, self.subsystem_raw))
            if equipment_detected_in_flow_matrix not in self.subsystem_detected_in_flow_matrix.all_equipments_detected_in_flow_matrix:
                pass
            assert equipment_detected_in_flow_matrix in self.subsystem_detected_in_flow_matrix.all_equipments_detected_in_flow_matrix
            if self.subsystem_detected_in_flow_matrix not in equipment_detected_in_flow_matrix.all_subsystems_detected_in_flow_matrix:
                pass
            assert self.subsystem_detected_in_flow_matrix in equipment_detected_in_flow_matrix.all_subsystems_detected_in_flow_matrix


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
    network_flow_matrix_lines_by_identifier: Dict[int, "NetworkFlowMatrixLine"]

    class Builder:

        @staticmethod
        def build_with_excel_file(excel_file_full_path: str, sheet_name: str = "Matrice_de_Flux_SITE") -> "NetworkFlowMatrix":
            main_data_frame = pandas.read_excel(excel_file_full_path, skiprows=[0, 1, 2, 3, 4], sheet_name=sheet_name)
            logger_config.print_and_log_info(f"Flow matrix {excel_file_full_path} has {len(main_data_frame)} items")
            logger_config.print_and_log_info(f"Flow matrix {excel_file_full_path} columns  {main_data_frame.columns[:4]} ...")

            network_flow_matrix_lines: List[NetworkFlowMatrixLine] = []
            network_flow_matrix_lines_by_identifier: Dict[int, "NetworkFlowMatrixLine"] = {}

            for _, row in main_data_frame.iterrows():
                network_flow_matrix_line = NetworkFlowMatrixLine.Builder.build_with_row(row=row)
                network_flow_matrix_lines.append(network_flow_matrix_line)
                network_flow_matrix_lines_by_identifier[network_flow_matrix_line.identifier] = network_flow_matrix_line

            return NetworkFlowMatrix(network_flow_matrix_lines=network_flow_matrix_lines, network_flow_matrix_lines_by_identifier=network_flow_matrix_lines_by_identifier)

    def get_line_by_identifier(self, identifier: int) -> Optional["NetworkFlowMatrixLine"]:
        return self.network_flow_matrix_lines_by_identifier[identifier]


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

    def __post_init__(self) -> None:
        self.identifier = int(self.identifier_raw)


class NetworkFlowMacro:
    def __init__(self) -> None:
        pass


class NetworkFlow:
    def __init__(self) -> None:
        pass
