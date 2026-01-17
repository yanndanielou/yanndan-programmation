import ipaddress
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, cast

import pandas
from common import file_utils, json_encoders, string_utils
from logger import logger_config

from networkflowmatrix import constants, equipments

INVALID_IP_ADDRESS = "INVALID_IP_ADDRESS"
MISSING_IP_ADDRESS = "MISSING_IP_ADDRESS"


def subsystem_to_dict(subsystem: "SubSystemInFlowMatrix", with_equipment: bool) -> Dict:
    if with_equipment:
        return {
            "subsystem_name": subsystem.name,
            "subsystem_number_equipments": len(subsystem.all_equipments_detected_in_flow_matrix),
            "subsystem_all_equipments": [equipment_to_dict(eq, False) for eq in subsystem.all_equipments_detected_in_flow_matrix],
        }
    else:
        return {"subsystem_name": subsystem.name}


def equipment_to_dict(equipment: "EquipmentInFLowMatrix", with_subsystem: bool) -> Dict:
    if with_subsystem:
        new_var = {
            "equipment_name": equipment.name,
            "equipment_ip_addresses": [str(ip) for ip in equipment.raw_ip_addresses],
            "equipment_number_of_subsystems_detected_in_flow_matrix": len(equipment.all_subsystems_detected_in_flow_matrix),
            "equipment_all_subsystems_detected_in_flow_matrix": [subsystem_to_dict(subsys, False) for subsys in equipment.all_subsystems_detected_in_flow_matrix],
        }
    else:
        new_var = {"equipment_name": equipment.name, "equipment_ip_addresses": [str(ip) for ip in equipment.raw_ip_addresses]}

    return new_var


def dump_matrix_subsystems_to_json(network_flow_matrix_to_dump: "NetworkFlowMatrix", filepath: str) -> None:
    data = [
        subsystem_to_dict(subsystem, with_equipment=True) for subsystem in sorted(network_flow_matrix_to_dump.all_matrix_flow_subsystems_definitions_instances, key=lambda subsystem: subsystem.name)
    ]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def dump_matrix_equipments_to_json(network_flow_matrix_to_dump: "NetworkFlowMatrix", filepath: str) -> None:
    data = [
        equipment_to_dict(equipment, with_subsystem=True) for equipment in sorted(network_flow_matrix_to_dump.all_matrix_flow_equipments_definitions_instances, key=lambda subsystem: subsystem.name)
    ]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


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
    def get_or_create_if_not_exist_by_name_and_ip(
        network_flow_matrix: "NetworkFlowMatrix", name: str, subsystem_detected_in_flow_matrix: SubSystemInFlowMatrix, raw_ip_address: str
    ) -> "EquipmentInFLowMatrix":
        if EquipmentInFLowMatrix.is_existing_by_name(network_flow_matrix, name):
            equipment = network_flow_matrix.all_matrix_flow_equipments_by_name[name]
            if subsystem_detected_in_flow_matrix not in equipment.all_subsystems_detected_in_flow_matrix:
                equipment.all_subsystems_detected_in_flow_matrix.append(subsystem_detected_in_flow_matrix)

            if equipment not in subsystem_detected_in_flow_matrix.all_equipments_detected_in_flow_matrix:
                subsystem_detected_in_flow_matrix.all_equipments_detected_in_flow_matrix.append(equipment)

            equipment.raw_ip_addresses.add(raw_ip_address)
            return equipment
        equipment = EquipmentInFLowMatrix(name=name, subsystem_detected_in_flow_matrix=subsystem_detected_in_flow_matrix, network_flow_matrix=network_flow_matrix)
        equipment.raw_ip_addresses.add(raw_ip_address)
        network_flow_matrix.all_matrix_flow_equipments_by_name[name] = equipment
        network_flow_matrix.all_matrix_flow_equipments_definitions_instances.append(equipment)
        subsystem_detected_in_flow_matrix.all_equipments_detected_in_flow_matrix.append(equipment)
        return equipment

    def __init__(self, name: str, subsystem_detected_in_flow_matrix: SubSystemInFlowMatrix, network_flow_matrix: "NetworkFlowMatrix") -> None:
        self.raw_ip_addresses: Set[str] = set()
        # self.ip_addresses: List[ipaddress.IPv4Address] = []
        self.all_subsystems_detected_in_flow_matrix: List[SubSystemInFlowMatrix] = [subsystem_detected_in_flow_matrix]
        self.name = name
        self.network_flow_matrix = network_flow_matrix


@dataclass
class FlowEndPoint:
    matrix_line_identifier: int
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
    allow_one_ip_for_several_equipments: bool

    def __post_init__(self) -> None:

        self.raw_ip_addresses: List[str] = []

        self.equipments_detected_in_flow_matrix: List[EquipmentInFLowMatrix] = []
        self.equipments_names: List[str] = [equipment_name.strip().upper() for equipment_name in self.equipment_cell_raw.split("\n") if equipment_name.strip() != ""]

        self.network_flow_matrix_line: "NetworkFlowMatrixLine" = cast("NetworkFlowMatrixLine", None)

        if not isinstance(self.ip_raw, str):
            self.ip_raw = None
        else:
            self.raw_ip_addresses = self.ip_raw.split("\n")

        # self.ip_address = [ipaddress.IPv4Address(raw_ip_raw) for raw_ip_raw in self.raw_ip_addresses]

        self.subsystem_detected_in_flow_matrix = SubSystemInFlowMatrix.get_or_create_if_not_exist_by_name(network_flow_matrix=self.network_flow_matrix, name=self.subsystem_raw.strip().upper())

    def match_equipments_with_network_conf_files(self, equipments_library: equipments.NetworkConfFilesEquipmentsLibrary) -> None:

        if len(self.equipments_names) > len(self.raw_ip_addresses) and len(self.raw_ip_addresses) > 1:
            logger_config.print_and_log_error(f"Error at line {self.matrix_line_identifier}: missing IP addresses for {self.equipments_names}, see {self.raw_ip_addresses}")

        for index_eqpt, equipment_name in enumerate(self.equipments_names):
            assert equipment_name
            assert len(equipment_name.split()) > 0
            self.network_flow_matrix.all_equipments_names.add(equipment_name)

            if len(self.raw_ip_addresses) <= index_eqpt and len(self.raw_ip_addresses) > 1:
                equipment_in_network_conf_file_by_name = equipments_library.get_existing_equipment_by_name(expected_equipment_name=equipment_name, allow_not_exact_name=True)
                logger_config.print_and_log_error(
                    f"Error at line {self.matrix_line_identifier}: no IP found for {equipment_name} (not enough lines). In network conf, equipment {(equipment_in_network_conf_file_by_name.name+ ' with Ip: ' if equipment_in_network_conf_file_by_name else 'Not found')} {",".join([ip.ip_raw for ip in equipment_in_network_conf_file_by_name.ip_addresses]) if equipment_in_network_conf_file_by_name else 'found'}"
                )
                eqpt_ip_address_raw = INVALID_IP_ADDRESS
            elif len(self.raw_ip_addresses) <= index_eqpt and len(self.raw_ip_addresses) == 1 and self.allow_one_ip_for_several_equipments:
                logger_config.print_and_log_info(f"At line {self.matrix_line_identifier}: equipment {equipment_name} shared  ip {self.raw_ip_addresses[0]}: is shared with {self.equipments_names}")
                eqpt_ip_address_raw = self.raw_ip_addresses[0]
            else:
                try:
                    eqpt_ip_address_raw = self.raw_ip_addresses[index_eqpt] if len(self.raw_ip_addresses) > 1 else self.raw_ip_addresses[0] if len(self.raw_ip_addresses) == 1 else MISSING_IP_ADDRESS
                    if eqpt_ip_address_raw == MISSING_IP_ADDRESS:
                        logger_config.print_and_log_error(f"At line {self.matrix_line_identifier}: Missing IP address for {equipment_name}")
                except IndexError:
                    eqpt_ip_address_raw = INVALID_IP_ADDRESS

            equipment_in_network_conf_file_by_name = equipments_library.get_existing_equipment_by_name(expected_equipment_name=equipment_name, allow_not_exact_name=True)
            equipments_in_network_conf_file_matching_ip_address = equipments_library.get_existing_equipment_by_raw_ip_address(eqpt_ip_address_raw)

            if equipment_in_network_conf_file_by_name:
                if eqpt_ip_address_raw not in [ip.ip_raw for ip in equipment_in_network_conf_file_by_name.ip_addresses]:
                    logger_config.print_and_log_error(
                        f"At line {self.matrix_line_identifier}: equipment {equipment_name} defined with {eqpt_ip_address_raw}, but this IP is not defined for this equipment in network conf files. Known IP are {','.join([ip.ip_raw for ip in equipment_in_network_conf_file_by_name.ip_addresses])}"
                    )
                    if equipments_in_network_conf_file_matching_ip_address:
                        logger_config.print_and_log_error(
                            f"At line {self.matrix_line_identifier}: equipment {equipment_name} defined with {eqpt_ip_address_raw}, but this IP is not defined for this equipment in network conf files. This IP is defined for {','.join([eqpt.name for eqpt in equipments_in_network_conf_file_matching_ip_address])}"
                        )
                    wrong_ip = equipments_library.add_wrong_or_unknown_ip_address_in_matrix_flow(
                        wrong_equipment_name_allocated_to_this_ip_by_mistake=equipment_name,
                        raw_ip_address=eqpt_ip_address_raw,
                        equipments_names_having_genuinely_this_ip_address=set([eqpt.name for eqpt in equipments_in_network_conf_file_matching_ip_address]),
                        matrix_line_id_referencing=self.matrix_line_identifier,
                    )

            if equipment_in_network_conf_file_by_name is None:
                equipments_in_network_conf_file_matching_group = equipments_library.get_existing_equipments_by_group(
                    expected_group_name=equipment_name, expected_group_subnet_and_mask=eqpt_ip_address_raw
                )
                if equipments_in_network_conf_file_matching_group:
                    logger_config.print_and_log_info(
                        f"{self.matrix_line_identifier}: Found {len(equipments_in_network_conf_file_matching_group)} equipments in group {equipment_name} with subnet/mask {eqpt_ip_address_raw}"
                    )

                else:
                    equipment_not_found = equipments_library.add_not_found_equipment_but_defined_in_network_flow_matrix(
                        name=equipment_name, raw_ip_address=eqpt_ip_address_raw, matrix_line_id_referencing=self.matrix_line_identifier
                    )
                    logger_config.print_and_log_error(
                        f"{self.matrix_line_identifier}: Could not find equipment {equipment_name} in network conf files. Searching with IP {eqpt_ip_address_raw}, found {len(equipments_in_network_conf_file_matching_ip_address)} equipments {[eqpt.name for eqpt in equipments_in_network_conf_file_matching_ip_address]}"
                    )

                    if equipments_in_network_conf_file_matching_ip_address is None:
                        logger_config.print_and_log_error(f"{self.matrix_line_identifier}: {equipment_name}: Ip address {eqpt_ip_address_raw} not defined in any network conf file")

                        equipments_library.not_found_equipment_names.add(f"{equipment_name}. No alternative name found")
                        equipments_library.not_found_equipment_names_and_raw_ip_address.add(f"{equipment_name};{eqpt_ip_address_raw};. No alternative name found")

                    elif equipment_name not in [equipment.name for equipment in equipments_in_network_conf_file_matching_ip_address]:
                        for equipment_in_network_conf_file_matching_ip_address_it in equipments_in_network_conf_file_matching_ip_address:
                            if equipment_name in equipment_in_network_conf_file_matching_ip_address_it.name:
                                if equipments_in_network_conf_file_matching_ip_address is None:
                                    equipments_in_network_conf_file_matching_ip_address = []
                                logger_config.print_and_log_info(
                                    f"{self.matrix_line_identifier}: Re-allocate {equipment_name} to {equipment_in_network_conf_file_matching_ip_address_it.name} thanks to IP {eqpt_ip_address_raw}"
                                )
                                # equipments_in_network_conf_file_matching_ip_address.append(equipment_in_network_conf_file_matching_ip_address_it)
                                # Should we add the new name to the dictionnary here to find it by name?

                                equipments_library.not_found_equipment_names.add(equipment_name + f" - found {equipment_in_network_conf_file_matching_ip_address_it.name}")
                                equipments_library.not_found_equipment_names_and_raw_ip_address.add(
                                    f"{equipment_name};{eqpt_ip_address_raw} - found {equipment_in_network_conf_file_matching_ip_address_it.name}"
                                )
                                equipment_not_found.alternative_names_matching_ip.add(equipment_in_network_conf_file_matching_ip_address_it.name)

                                break
                        if equipments_in_network_conf_file_matching_ip_address:
                            logger_config.print_and_log_error(
                                f"{self.matrix_line_identifier}: Ip address {eqpt_ip_address_raw} not allocated to {equipment_name} in network files but in {[equipment.name for equipment in equipments_in_network_conf_file_matching_ip_address]}"
                            )
                            equipments_library.not_found_equipment_names.add(equipment_name + f" - found {[equipment.name for equipment in equipments_in_network_conf_file_matching_ip_address]}")
                            equipments_library.not_found_equipment_names_and_raw_ip_address.add(
                                f"{equipment_name};{eqpt_ip_address_raw} - found {[equipment.name for equipment in equipments_in_network_conf_file_matching_ip_address]}"
                            )
                            equipment_not_found.alternative_names_matching_ip.add(equipment_in_network_conf_file_matching_ip_address_it.name)

                    else:

                        equipments_library.not_found_equipment_names.add(equipment_name)
                        equipments_library.not_found_equipment_names_and_raw_ip_address.add(f"{equipment_name};{eqpt_ip_address_raw}")

            equipment_detected_in_flow_matrix = EquipmentInFLowMatrix.get_or_create_if_not_exist_by_name_and_ip(
                network_flow_matrix=self.network_flow_matrix, name=equipment_name, subsystem_detected_in_flow_matrix=self.subsystem_detected_in_flow_matrix, raw_ip_address=eqpt_ip_address_raw
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
            matrice_line_identifier_raw_str = cast(str, row["ID"])
            matrice_line_identifier = int(matrice_line_identifier_raw_str)
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
                matrix_line_identifier=matrice_line_identifier,
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
                allow_one_ip_for_several_equipments=False,
            )


@dataclass
class FlowDestination(FlowEndPoint):

    group_multicast_raw: str
    cast_raw: str
    cast_type: constants.CastType

    class Builder:

        @staticmethod
        def build_with_row(row: pandas.Series, network_flow_matrix: "NetworkFlowMatrix") -> "FlowDestination":
            matrice_line_identifier_raw_str = cast(str, row["ID"])
            matrice_line_identifier = int(matrice_line_identifier_raw_str)

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
            cast_type = constants.CastType[string_utils.text_to_valid_enum_value_text(cast_raw)] if str(cast_raw).lower() != "nan" else constants.CastType.UNKNOWN

            return FlowDestination(
                matrix_line_identifier=matrice_line_identifier,
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
                cast_type=cast_type,
                allow_one_ip_for_several_equipments=(cast_type == constants.CastType.MULTICAST),
            )

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.cast_type == constants.CastType.MULTICAST:
            assert isinstance(self.group_multicast_raw, str), f"{self.matrix_line_identifier} : empty group {self.group_multicast_raw} for multicast {self.cast_type}"


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
                    network_flow_matrix_lines_by_identifier[network_flow_matrix_line.identifier_int] = network_flow_matrix_line

            network_flow_matrix.network_flow_matrix_lines = network_flow_matrix_lines
            network_flow_matrix.network_flow_matrix_lines_by_identifier = network_flow_matrix_lines_by_identifier

            assert network_flow_matrix.network_flow_matrix_lines, "matrix is empty"
            assert network_flow_matrix.network_flow_matrix_lines_by_identifier, "matrix is empty"

            return network_flow_matrix

    def get_line_by_identifier(self, identifier: int) -> Optional["NetworkFlowMatrixLine"]:
        return self.network_flow_matrix_lines_by_identifier[identifier]

    def match_equipments_with_network_conf_files(self, equipments_library: equipments.NetworkConfFilesEquipmentsLibrary) -> None:

        with logger_config.stopwatch_with_label("match_equipments_with_network_conf_files"):
            for line in self.network_flow_matrix_lines:
                line.source.match_equipments_with_network_conf_files(equipments_library)
                line.destination.match_equipments_with_network_conf_files(equipments_library)

        logger_config.print_and_log_warning(
            f"After scanning network flow matrix, {len(equipments_library.not_found_equipment_names)} unknown equipments (not found in network conf files) names are {equipments_library.not_found_equipment_names}"
        )
        logger_config.print_and_log_warning(f"'\n'{'\n'.join(sorted(list(equipments_library.not_found_equipment_names)))}")

        logger_config.print_and_log_warning(
            f"After scanning network flow matrix, {len(equipments_library.not_found_equipment_names_and_raw_ip_address)} unknown equipments (not found in network conf files) names and IP addresses are {equipments_library.not_found_equipment_names}"
        )
        logger_config.print_and_log_warning(f"'\n'{'\n'.join(sorted(list(equipments_library.not_found_equipment_names_and_raw_ip_address)))}")

        logger_config.print_and_log_warning(f"After scanning network flow matrix, {len(equipments_library.wrong_equipment_name_allocated_to_this_ip_by_mistake)} wrong IP address definition")
        logger_config.print_and_log_warning(
            f"'\n'{'\n'.join([wrong_ip.wrong_equipment_name_allocated_to_this_ip_by_mistake + ";"+ wrong_ip.raw_ip_address+";"+ ",".join(wrong_ip.equipments_names_having_genuinely_this_ip_address) for wrong_ip in equipments_library.wrong_equipment_name_allocated_to_this_ip_by_mistake])}"
        )

        for directory_path in [constants.OUTPUT_PARENT_DIRECTORY_NAME]:
            file_utils.create_folder_if_not_exist(directory_path)

        dump_matrix_subsystems_to_json(self, f"{constants.OUTPUT_PARENT_DIRECTORY_NAME}/matrix_all_subsystems_in_flow_matrix.json")
        dump_matrix_equipments_to_json(self, f"{constants.OUTPUT_PARENT_DIRECTORY_NAME}/matrix_all_equipments_in_flow_matrix.json")
        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(
            equipments_library.not_found_equipments_but_defined_in_flow_matrix, f"{constants.OUTPUT_PARENT_DIRECTORY_NAME}/matrix_all_unknown_equipments.json"
        )
        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(
            equipments_library.wrong_equipment_name_allocated_to_this_ip_by_mistake, f"{constants.OUTPUT_PARENT_DIRECTORY_NAME}/matrix_wrong_ip.json"
        )

        equipments_library.dump_to_json_file(f"{constants.OUTPUT_PARENT_DIRECTORY_NAME}/all_equipments_in_conf_files.json")


@dataclass
class NetworkFlowMatrixLine:
    network_flow_matrix: NetworkFlowMatrix
    identifier_int: int
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
            if str(identifier_raw_str) in ["nan"]:
                logger_config.print_and_log_warning(f"Empty row with identifier {identifier_raw_str}")
                return None
            identifier_raw_str = cast(str, row["ID"])
            if str(identifier_raw_str) in ["nan", "%%%"]:
                logger_config.print_and_log_warning(f"Invalid row with identifier {identifier_raw_str}")
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
                identifier_int=identifier_int,
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
        self.identifier_int = int(self.identifier_raw)


class NetworkFlowMacro:
    def __init__(self) -> None:
        pass


class NetworkFlow:
    def __init__(self) -> None:
        pass
