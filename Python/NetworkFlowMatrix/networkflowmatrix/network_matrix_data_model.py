import ipaddress
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple, cast, Dict

import pandas
from logger import logger_config


INVALID_IP_ADDRESS = "INVALID_IP_ADDRESS"


class SubSystemInFlowMatrix:

    @staticmethod
    def is_existing_by_name(network_flow_matrix: "NetworkFlowMatrix", name: str) -> bool:
        return name in network_flow_matrix.all_matrix_flow_subsystems_definitions_instances_by_name

    @staticmethod
    def get_existing_by_name(network_flow_matrix: "NetworkFlowMatrix", name: str) -> Optional["SubSystemInFlowMatrix"]:
        if SubSystemInFlowMatrix.is_existing_by_name(network_flow_matrix, name):
            return network_flow_matrix.all_matrix_flow_subsystems_definitions_instances_by_name[name]
        return None

    @staticmethod
    def get_or_create_if_not_exist_by_name(network_flow_matrix: "NetworkFlowMatrix", name: str) -> "SubSystemInFlowMatrix":
        if SubSystemInFlowMatrix.is_existing_by_name(network_flow_matrix, name):
            return network_flow_matrix.all_matrix_flow_subsystems_definitions_instances_by_name[name]
        subsystem = SubSystemInFlowMatrix(network_flow_matrix=network_flow_matrix, name=name)
        network_flow_matrix.all_matrix_flow_subsystems_definitions_instances_by_name[name] = subsystem
        network_flow_matrix.all_matrix_flow_subsystems_definitions_instances.append(subsystem)

        return subsystem

    def __init__(self, name: str, network_flow_matrix: "NetworkFlowMatrix") -> None:
        self.all_equipments_detected_in_flow_matrix: List["EquipmentInFLowMatrix"] = []
        self.name = name
        self.network_flow_matrix = network_flow_matrix


class PortInFLowMatrix:
    def __init__(self, raw_port: Optional[str | int]) -> None:
        pass


class EquipmentInFLowMatrix:

    @staticmethod
    def is_existing_by_name(network_flow_matrix: "NetworkFlowMatrix", name: str) -> bool:
        return name in network_flow_matrix.all_matrix_flow_equipments_by_name

    @staticmethod
    def get_existing_by_name(network_flow_matrix: "NetworkFlowMatrix", name: str) -> Optional["EquipmentInFLowMatrix"]:
        if EquipmentInFLowMatrix.is_existing_by_name(network_flow_matrix, name):
            return network_flow_matrix.all_matrix_flow_equipments_by_name[name]
        return None

    @staticmethod
    def get_or_create_if_not_exist_by_name(network_flow_matrix: "NetworkFlowMatrix", name: str, subsystem_detected_in_flow_matrix: SubSystemInFlowMatrix) -> "EquipmentInFLowMatrix":
        if EquipmentInFLowMatrix.is_existing_by_name(network_flow_matrix, name):
            equipment = network_flow_matrix.all_matrix_flow_equipments_by_name[name]
            if subsystem_detected_in_flow_matrix not in equipment.all_subsystems_detected_in_flow_matrix:
                equipment.all_subsystems_detected_in_flow_matrix.append(subsystem_detected_in_flow_matrix)

            if equipment not in subsystem_detected_in_flow_matrix.all_equipments_detected_in_flow_matrix:
                subsystem_detected_in_flow_matrix.all_equipments_detected_in_flow_matrix.append(equipment)
            return equipment
        equipment = EquipmentInFLowMatrix(name=name, subsystem_detected_in_flow_matrix=subsystem_detected_in_flow_matrix, network_flow_matrix=network_flow_matrix)
        network_flow_matrix.all_matrix_flow_equipments_by_name[name] = equipment
        network_flow_matrix.all_matrix_flow_equipments_definitions_instances.append(equipment)
        subsystem_detected_in_flow_matrix.all_equipments_detected_in_flow_matrix.append(equipment)
        return equipment

    def __init__(self, name: str, subsystem_detected_in_flow_matrix: SubSystemInFlowMatrix, network_flow_matrix: "NetworkFlowMatrix") -> None:
        self.ip_addresses: List[ipaddress.IPv4Address] = []
        self.all_subsystems_detected_in_flow_matrix: List[SubSystemInFlowMatrix] = [subsystem_detected_in_flow_matrix]
        self.name = name
        self.network_flow_matrix = network_flow_matrix


@dataclass
class FlowEndPoint:
    network_flow_matrix: "NetworkFlowMatrix"
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

        self.network_flow_matrix_line: "NetworkFlowMatrixLine" = cast("NetworkFlowMatrixLine", None)

        if not isinstance(self.ip_raw, str):
            self.ip_raw = None

        self.raw_ip_addresses = self.ip_raw.split("\n") if self.ip_raw else []
        # self.ip_address = [ipaddress.IPv4Address(raw_ip_raw) for raw_ip_raw in self.raw_ip_addresses]

        self.subsystem_detected_in_flow_matrix = SubSystemInFlowMatrix.get_or_create_if_not_exist_by_name(network_flow_matrix=self.network_flow_matrix, name=self.subsystem_raw.strip().upper())
        self.equipments_detected_in_flow_matrix: List[EquipmentInFLowMatrix] = []

        self.equipments_names = [equipment_name.strip().upper() for equipment_name in self.equipment_cell_raw.split("\n") if equipment_name.strip() != ""]

        if len(self.equipments_names) > len(self.raw_ip_addresses):
            logger_config.print_and_log_error(f"Missing IP addresses for {self.equipments_names}, see {self.raw_ip_addresses}")

        for index_eqpt, equipment_name in enumerate(self.equipments_names):
            assert equipment_name
            assert len(equipment_name.split()) > 0
            self.network_flow_matrix.all_equipments_names.add(equipment_name)
            if len(self.raw_ip_addresses) <= index_eqpt:
                logger_config.print_and_log_error(f"Error: no IP found for {equipment_name} (not enough lines)")
                self.ip_address_raw = INVALID_IP_ADDRESS
            else:
                try:
                    self.ip_address_raw = self.raw_ip_addresses[index_eqpt] if len(self.raw_ip_addresses) > 1 else self.raw_ip_addresses[0] if self.equipments_detected_in_flow_matrix else None
                except IndexError:
                    self.ip_address_raw = INVALID_IP_ADDRESS
            equipment_detected_in_flow_matrix = EquipmentInFLowMatrix.get_or_create_if_not_exist_by_name(
                network_flow_matrix=self.network_flow_matrix, name=equipment_name, subsystem_detected_in_flow_matrix=self.subsystem_detected_in_flow_matrix
            )
            self.equipments_detected_in_flow_matrix.append(equipment_detected_in_flow_matrix)
            self.network_flow_matrix.all_equipments_names_with_subsystem.add((equipment_name, self.subsystem_raw))

            assert equipment_detected_in_flow_matrix in self.subsystem_detected_in_flow_matrix.all_equipments_detected_in_flow_matrix

            assert self.subsystem_detected_in_flow_matrix in equipment_detected_in_flow_matrix.all_subsystems_detected_in_flow_matrix


@dataclass
class FlowSource(FlowEndPoint):

    class Builder:

        @staticmethod
        def build_with_row(row: pandas.Series, network_flow_matrix: "NetworkFlowMatrix") -> "FlowSource":
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
                network_flow_matrix=network_flow_matrix,
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
        def build_with_row(row: pandas.Series, network_flow_matrix: "NetworkFlowMatrix") -> "FlowDestination":
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
                network_flow_matrix=network_flow_matrix,
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
    network_flow_matrix_lines: List["NetworkFlowMatrixLine"] = field(default_factory=list)
    network_flow_matrix_lines_by_identifier: Dict[int, "NetworkFlowMatrixLine"] = field(default_factory=dict)

    all_equipments_names: Set[str] = field(default_factory=set)
    all_equipments_names_with_subsystem: set[Tuple[str, str]] = field(default_factory=set)

    all_matrix_flow_equipments_definitions_instances: List["EquipmentInFLowMatrix"] = field(default_factory=list)
    all_matrix_flow_equipments_by_name: Dict[str, "EquipmentInFLowMatrix"] = field(default_factory=dict)

    all_matrix_flow_subsystems_definitions_instances: List["SubSystemInFlowMatrix"] = field(default_factory=list)
    all_matrix_flow_subsystems_definitions_instances_by_name: Dict[str, "SubSystemInFlowMatrix"] = field(default_factory=dict)

    class Builder:

        @staticmethod
        def build_with_excel_file(excel_file_full_path: str, sheet_name: str = "Matrice_de_Flux_SITE") -> "NetworkFlowMatrix":
            main_data_frame = pandas.read_excel(excel_file_full_path, skiprows=[0, 1, 2, 3, 4], sheet_name=sheet_name)
            logger_config.print_and_log_info(f"Flow matrix {excel_file_full_path} has {len(main_data_frame)} items")
            logger_config.print_and_log_info(f"Flow matrix {excel_file_full_path} columns  {main_data_frame.columns[:4]} ...")

            network_flow_matrix_lines: List[NetworkFlowMatrixLine] = []
            network_flow_matrix_lines_by_identifier: Dict[int, "NetworkFlowMatrixLine"] = {}

            network_flow_matrix = NetworkFlowMatrix()

            for _, row in main_data_frame.iterrows():
                network_flow_matrix_line = NetworkFlowMatrixLine.Builder.build_with_row(row=row, network_flow_matrix=network_flow_matrix)
                if network_flow_matrix_line:
                    network_flow_matrix_lines.append(network_flow_matrix_line)
                    network_flow_matrix_lines_by_identifier[network_flow_matrix_line.identifier] = network_flow_matrix_line

            network_flow_matrix.network_flow_matrix_lines = network_flow_matrix_lines
            network_flow_matrix.network_flow_matrix_lines_by_identifier = network_flow_matrix_lines_by_identifier
            return network_flow_matrix

    def get_line_by_identifier(self, identifier: int) -> Optional["NetworkFlowMatrixLine"]:
        return self.network_flow_matrix_lines_by_identifier[identifier]


@dataclass
class NetworkFlowMatrixLine:
    network_flow_matrix: NetworkFlowMatrix
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
        def build_with_row(row: pandas.Series, network_flow_matrix: NetworkFlowMatrix) -> Optional["NetworkFlowMatrixLine"]:
            identifier_raw_str = cast(str, row["ID"])
            if str(identifier_raw_str) == "nan":
                logger_config.print_and_log_warning(f"Invalid row {row}")
                return None
            identifier_int = int(identifier_raw_str)
            name_raw = cast(str, row["Lien de com. complet\n(Auto)"])
            sol_bord_raw = cast(str, row["S/B"])

            protocole_applicative_raw = row["Protocole\nApplicatif"]
            protocole_transport_raw = row["Protocole \nde Transport"]
            type_raw = row["Type flux\n(Fonc/Admin)"]
            traffic_direction_raw = row["Sens du Trafic\n(uni, bidir)"]
            seclab_raw = row["Seclab"]

            source = FlowSource.Builder.build_with_row(row, network_flow_matrix)
            destination = FlowDestination.Builder.build_with_row(row, network_flow_matrix)

            network_flow_matrix_line = NetworkFlowMatrixLine(
                network_flow_matrix=network_flow_matrix,
                destination=destination,
                identifier_raw=identifier_raw_str,
                name_raw=name_raw,
                sol_bord_raw=sol_bord_raw,
                source=source,
                seclab_raw=seclab_raw,
                protocole_applicative_raw=protocole_applicative_raw,
                protocole_transport_raw=protocole_transport_raw,
                traffic_direction_raw=traffic_direction_raw,
                type_raw=type_raw,
            )
            source.network_flow_matrix_line = network_flow_matrix_line
            destination.network_flow_matrix_line = network_flow_matrix_line

            return network_flow_matrix_line

    def __post_init__(self) -> None:
        self.identifier = int(self.identifier_raw)


class NetworkFlowMacro:
    def __init__(self) -> None:
        pass


class NetworkFlow:
    def __init__(self) -> None:
        pass
