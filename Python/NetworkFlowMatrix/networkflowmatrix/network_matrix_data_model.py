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


def equipment_to_dict(equipment: "EquipmentInFlowMatrix", with_subsystem: bool) -> Dict:
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
    def get_or_create_if_not_exist_by_name(network_flow_matrix: "NetworkFlowMatrix", name: str) -> "SubSystemInFlowMatrix":
        if SubSystemInFlowMatrix.is_existing_by_name(network_flow_matrix, name):
            return network_flow_matrix.all_matrix_flow_subsystems_definitions_instances_by_name[name]
        subsystem = SubSystemInFlowMatrix(network_flow_matrix=network_flow_matrix, name=name)
        network_flow_matrix.all_matrix_flow_subsystems_definitions_instances_by_name[name] = subsystem
        network_flow_matrix.all_matrix_flow_subsystems_definitions_instances.append(subsystem)

        return subsystem

    def __init__(self, name: str, network_flow_matrix: "NetworkFlowMatrix") -> None:
        self.all_equipments_detected_in_flow_matrix: List["EquipmentInFlowMatrix"] = []
        self.name = name
        self.network_flow_matrix = network_flow_matrix


class PortInFlowMatrix:
    def __init__(self, raw_port: Optional[str | int]) -> None:
        pass


class EquipmentInFlowMatrix:

    @staticmethod
    def is_existing_by_name(network_flow_matrix: "NetworkFlowMatrix", name: str) -> bool:
        return name in network_flow_matrix.all_matrix_flow_equipments_by_name

    @staticmethod
    def get_or_create_equipment_if_not_exist(
        network_flow_matrix: "NetworkFlowMatrix", name: str, subsystem_detected_in_flow_matrix: SubSystemInFlowMatrix, raw_ip_address: str, matrix_line_identifier: int
    ) -> "EquipmentInFlowMatrix":
        if EquipmentInFlowMatrix.is_existing_by_name(network_flow_matrix, name):
            equipment = network_flow_matrix.all_matrix_flow_equipments_by_name[name]
            equipment.raw_ip_addresses.add(raw_ip_address)
            return equipment
        equipment = EquipmentInFlowMatrix(name=name, network_flow_matrix=network_flow_matrix)
        equipment.raw_ip_addresses.add(raw_ip_address)
        network_flow_matrix.all_matrix_flow_equipments_by_name[name] = equipment
        network_flow_matrix.all_matrix_flow_equipments_definitions_instances.append(equipment)
        subsystem_detected_in_flow_matrix.all_equipments_detected_in_flow_matrix.append(equipment)
        return equipment

    def __init__(self, name: str, network_flow_matrix: "NetworkFlowMatrix") -> None:
        self.raw_ip_addresses: Set[str] = set()
        # self.ip_addresses: List[ipaddress.IPv4Address] = []
        self.all_subsystems_detected_in_flow_matrix: List[SubSystemInFlowMatrix] = []
        self.all_subsystems_detected_in_flow_matrix_with_lines_identifiers: Dict[SubSystemInFlowMatrix, List[int]] = {}

        self.name = name
        self.network_flow_matrix = network_flow_matrix

    def add_subsystems_detected_in_flow_matrix_with_lines_identifiers(self, subsystem_detected_in_flow_matrix: SubSystemInFlowMatrix, matrix_line_identifier: int) -> None:
        if subsystem_detected_in_flow_matrix not in self.all_subsystems_detected_in_flow_matrix_with_lines_identifiers:
            self.all_subsystems_detected_in_flow_matrix_with_lines_identifiers[subsystem_detected_in_flow_matrix] = []
        self.all_subsystems_detected_in_flow_matrix_with_lines_identifiers[subsystem_detected_in_flow_matrix].append(matrix_line_identifier)

        if subsystem_detected_in_flow_matrix not in self.all_subsystems_detected_in_flow_matrix:
            self.all_subsystems_detected_in_flow_matrix.append(subsystem_detected_in_flow_matrix)

        if self not in subsystem_detected_in_flow_matrix.all_equipments_detected_in_flow_matrix:
            subsystem_detected_in_flow_matrix.all_equipments_detected_in_flow_matrix.append(self)


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

        self.equipments_detected_in_flow_matrix: List[EquipmentInFlowMatrix] = []
        self.equipments_names: List[str] = [equipment_name.strip().upper() for equipment_name in self.equipment_cell_raw.split("\n") if equipment_name.strip() != ""]

        self.network_flow_matrix_line: "NetworkFlowMatrixLine" = cast("NetworkFlowMatrixLine", None)

        if not isinstance(self.ip_raw, str):
            self.ip_raw = None
        else:
            self.raw_ip_addresses = [raw_ip.strip() for raw_ip in self.ip_raw.split("\n")]

        self.subsystem_detected_in_flow_matrix = SubSystemInFlowMatrix.get_or_create_if_not_exist_by_name(network_flow_matrix=self.network_flow_matrix, name=self.subsystem_raw.strip().upper())

    def match_equipments_with_network_conf_files(self, equipments_library: equipments.NetworkConfFilesEquipmentsLibrary) -> None:

        if len(self.equipments_names) > len(self.raw_ip_addresses) and len(self.raw_ip_addresses) > 1:
            logger_config.print_and_log_error(to_print_and_log=f"Error at line {self.matrix_line_identifier}: missing IP addresses for {self.equipments_names}, see {self.raw_ip_addresses}")

        index_ip_addr = -1
        index_eqpt = -1
        for index_eqpt, equipment_name in enumerate(self.equipments_names):
            is_first_time_equipment_line_is_used = True

            while is_first_time_equipment_line_is_used or (
                len(self.raw_ip_addresses) > index_ip_addr + 1  # There are more lines of IP addresses
                and len(self.raw_ip_addresses) > len(self.equipments_names)
                and (
                    [
                        same_eqpt
                        for same_eqpt in equipments_library.get_existing_equipment_by_raw_ip_address(expected_raw_ip_address=self.raw_ip_addresses[index_ip_addr + 1])
                        if same_eqpt.name == equipment_name or equipment_name in same_eqpt.alternative_identifiers
                    ]  # The next line of IP address is for the same eqpt (because its IP address)
                    or [
                        same_eqpt
                        for same_eqpt in equipments_library.get_existing_equipments_by_group(
                            expected_group_name=equipment_name, expected_group_subnet_and_mask=self.raw_ip_addresses[index_ip_addr + 1]
                        )
                        # The next line of IP address is for the same eqpt (found with the group)
                    ]
                )
                and not (
                    len(self.equipments_names) > index_eqpt + 1
                    and (
                        [
                            same_eqpt
                            for same_eqpt in equipments_library.get_existing_equipment_by_raw_ip_address(expected_raw_ip_address=self.raw_ip_addresses[index_ip_addr + 1])
                            if same_eqpt.name == self.equipments_names[index_eqpt + 1] or equipment_name in same_eqpt.alternative_identifiers
                        ]  # The next line of IP address is not for the next line equipment
                        or [
                            same_eqpt
                            for same_eqpt in equipments_library.get_existing_equipments_by_group(
                                expected_group_name=self.equipments_names[index_eqpt + 1], expected_group_subnet_and_mask=self.raw_ip_addresses[index_ip_addr + 1]
                            )
                            # The next line of IP address is not for the next line equipment
                        ]
                    )
                )
            ):
                if not is_first_time_equipment_line_is_used:
                    logger_config.print_and_log_info(
                        to_print_and_log=f"line {self.matrix_line_identifier}:also use next IP {self.raw_ip_addresses[index_ip_addr+1]} for equipment {equipment_name}. Previously used IP was {self.raw_ip_addresses[index_ip_addr]}"
                    )

                is_first_time_equipment_line_is_used = False

                index_ip_addr = index_ip_addr + 1
                assert index_ip_addr < 100, f"At line {self.matrix_line_identifier}: Stucked in infinite loop"
                assert equipment_name
                assert len(equipment_name.split()) > 0
                self.network_flow_matrix.all_equipments_names.add(equipment_name)

                if len(self.raw_ip_addresses) <= index_ip_addr and len(self.raw_ip_addresses) > 1:
                    equipment_in_network_conf_file_by_name = equipments_library.get_existing_equipment_by_name(expected_equipment_name=equipment_name, allow_not_exact_name=True)
                    logger_config.print_and_log_error(
                        to_print_and_log=f"Error at line {self.matrix_line_identifier}: no IP found for {equipment_name} (not enough lines). In network conf, equipment {(equipment_in_network_conf_file_by_name.name+ ' with Ip: ' if equipment_in_network_conf_file_by_name else 'Not found')} {",".join([ip.ip_raw for ip in equipment_in_network_conf_file_by_name.ip_addresses]) if equipment_in_network_conf_file_by_name else 'found'}"
                    )
                    eqpt_ip_address_raw = INVALID_IP_ADDRESS
                    equipments_library.add_wrong_or_unknown_ip_address_in_matrix_flow(
                        wrong_equipment_name_allocated_to_this_ip_by_mistake=equipment_name,
                        raw_ip_address=eqpt_ip_address_raw,
                        equipments_names_having_genuinely_this_ip_address=set(),
                        matrix_line_id_referencing=self.matrix_line_identifier,
                    )
                elif len(self.raw_ip_addresses) <= index_ip_addr and len(self.raw_ip_addresses) == 1 and self.allow_one_ip_for_several_equipments:
                    logger_config.print_and_log_info(
                        to_print_and_log=f"At line {self.matrix_line_identifier}: equipment {equipment_name} shared  ip {self.raw_ip_addresses[0]}: is shared with {self.equipments_names}",
                        do_not_print=True,
                    )
                    eqpt_ip_address_raw = self.raw_ip_addresses[0]
                else:
                    try:
                        eqpt_ip_address_raw = (
                            self.raw_ip_addresses[index_ip_addr] if len(self.raw_ip_addresses) > 1 else self.raw_ip_addresses[0] if len(self.raw_ip_addresses) == 1 else MISSING_IP_ADDRESS
                        )
                        if eqpt_ip_address_raw == MISSING_IP_ADDRESS:
                            logger_config.print_and_log_error(to_print_and_log=f"At line {self.matrix_line_identifier}: Missing IP address for {equipment_name}")
                            equipments_library.add_wrong_or_unknown_ip_address_in_matrix_flow(
                                wrong_equipment_name_allocated_to_this_ip_by_mistake=equipment_name,
                                raw_ip_address=eqpt_ip_address_raw,
                                equipments_names_having_genuinely_this_ip_address=set(),
                                matrix_line_id_referencing=self.matrix_line_identifier,
                            )
                    except IndexError:
                        eqpt_ip_address_raw = INVALID_IP_ADDRESS + "_Index_Error"
                        equipments_library.add_wrong_or_unknown_ip_address_in_matrix_flow(
                            wrong_equipment_name_allocated_to_this_ip_by_mistake=equipment_name,
                            raw_ip_address=eqpt_ip_address_raw,
                            equipments_names_having_genuinely_this_ip_address=set(),
                            matrix_line_id_referencing=self.matrix_line_identifier,
                        )

                equipment_in_network_conf_file_by_name = equipments_library.get_existing_equipment_by_name(expected_equipment_name=equipment_name, allow_not_exact_name=True)
                equipments_in_network_conf_file_matching_ip_address = equipments_library.get_existing_equipment_by_raw_ip_address(eqpt_ip_address_raw)
                equipments_in_network_conf_file_matching_group = equipments_library.get_existing_equipments_by_group(
                    expected_group_name=equipment_name, expected_group_subnet_and_mask=eqpt_ip_address_raw
                )

                if not equipment_in_network_conf_file_by_name and not equipments_in_network_conf_file_matching_group:
                    # Equipment not defined
                    equipments_library.add_not_found_equipment_but_defined_in_network_flow_matrix(
                        equipment_name=equipment_name,
                        eqpt_ip_address_raw=eqpt_ip_address_raw,
                        matrix_line_id_referencing=self.matrix_line_identifier,
                        equipments_in_network_conf_file_matching_ip_address=equipments_in_network_conf_file_matching_ip_address,
                    )

                elif equipment_in_network_conf_file_by_name and eqpt_ip_address_raw not in [ip.ip_raw for ip in equipment_in_network_conf_file_by_name.ip_addresses]:
                    # Equipment found but IP not found in this eqpt
                    logger_config.print_and_log_error(
                        to_print_and_log=f"At line {self.matrix_line_identifier}: equipment {equipment_name} defined with {eqpt_ip_address_raw}, but this IP is not defined for this equipment in network conf files. Known IP are {','.join([ip.ip_raw for ip in equipment_in_network_conf_file_by_name.ip_addresses])}. This IP is defined for {','.join([eqpt.name for eqpt in equipments_in_network_conf_file_matching_ip_address])}",
                        do_not_print=True,
                    )
                    equipments_library.add_wrong_or_unknown_ip_address_in_matrix_flow(
                        wrong_equipment_name_allocated_to_this_ip_by_mistake=equipment_name,
                        raw_ip_address=eqpt_ip_address_raw,
                        equipments_names_having_genuinely_this_ip_address=set([eqpt.name for eqpt in equipments_in_network_conf_file_matching_ip_address]),
                        matrix_line_id_referencing=self.matrix_line_identifier,
                    )

                equipment_detected_in_flow_matrix = EquipmentInFlowMatrix.get_or_create_equipment_if_not_exist(
                    network_flow_matrix=self.network_flow_matrix,
                    name=equipment_name,
                    subsystem_detected_in_flow_matrix=self.subsystem_detected_in_flow_matrix,
                    raw_ip_address=eqpt_ip_address_raw,
                    matrix_line_identifier=self.matrix_line_identifier,
                )
                equipment_detected_in_flow_matrix.add_subsystems_detected_in_flow_matrix_with_lines_identifiers(
                    subsystem_detected_in_flow_matrix=self.subsystem_detected_in_flow_matrix, matrix_line_identifier=self.matrix_line_identifier
                )
                self.equipments_detected_in_flow_matrix.append(equipment_detected_in_flow_matrix)
                self.network_flow_matrix.all_equipments_names_with_subsystem.add((equipment_name, self.subsystem_raw))

                assert equipment_detected_in_flow_matrix in self.subsystem_detected_in_flow_matrix.all_equipments_detected_in_flow_matrix

                assert self.subsystem_detected_in_flow_matrix in equipment_detected_in_flow_matrix.all_subsystems_detected_in_flow_matrix

        assert index_eqpt >= 0
        if (index_ip_addr + 1) < len(self.raw_ip_addresses):
            ip_addresses_without_equipment_name = self.raw_ip_addresses[index_eqpt:]
            logger_config.print_and_log_error(
                to_print_and_log=f"Error at line {self.matrix_line_identifier}: Too few equipment names {self.equipments_names} compared to {self.raw_ip_addresses}. ip_addresses_without_equipment_name:{ip_addresses_without_equipment_name}"
            )
            for ip_address_without_equipment_name in ip_addresses_without_equipment_name:
                logger_config.print_and_log_error(
                    to_print_and_log=f"Error at line {self.matrix_line_identifier}: missing equipment line for {ip_address_without_equipment_name} (this IP belongs to ({",".join([equipment.name for equipment in equipments_library.get_existing_equipment_by_raw_ip_address(ip_address_without_equipment_name)])}))",
                    do_not_print=True,
                )
                equipments_library.add_wrong_or_unknown_ip_address_in_matrix_flow(
                    wrong_equipment_name_allocated_to_this_ip_by_mistake="Missing equipment",
                    raw_ip_address=ip_address_without_equipment_name,
                    equipments_names_having_genuinely_this_ip_address=set([eqpt.name for eqpt in equipments_library.get_existing_equipment_by_raw_ip_address(ip_address_without_equipment_name)]),
                    matrix_line_id_referencing=self.matrix_line_identifier,
                )
            pass


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

    all_matrix_flow_equipments_definitions_instances: List["EquipmentInFlowMatrix"] = field(default_factory=list)
    all_matrix_flow_equipments_by_name: Dict[str, "EquipmentInFlowMatrix"] = field(default_factory=dict)

    all_matrix_flow_subsystems_definitions_instances: List["SubSystemInFlowMatrix"] = field(default_factory=list)
    all_matrix_flow_subsystems_definitions_instances_by_name: Dict[str, "SubSystemInFlowMatrix"] = field(default_factory=dict)

    class Builder:

        @staticmethod
        def build_with_excel_file(excel_file_full_path: str, sheet_name: str = "Matrice_de_Flux_SITE") -> "NetworkFlowMatrix":
            main_data_frame = pandas.read_excel(excel_file_full_path, skiprows=[0, 1, 2, 3, 4], sheet_name=sheet_name)
            logger_config.print_and_log_info(to_print_and_log=f"Flow matrix {excel_file_full_path} has {len(main_data_frame)} items")
            logger_config.print_and_log_info(to_print_and_log=f"Flow matrix {excel_file_full_path} columns  {main_data_frame.columns[:4]} ...")

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
                if line.is_deleted:
                    logger_config.print_and_log_info(f"Ignore line {line.identifier_int} because is deleted ({line.modif_raw_str})")
                else:
                    line.source.match_equipments_with_network_conf_files(equipments_library)
                    line.destination.match_equipments_with_network_conf_files(equipments_library)

        self.check_consistency()
        self.create_reports_after_matching_network_conf_files(equipments_library)

    def check_consistency(self) -> None:

        with logger_config.stopwatch_with_label("check_consistency", inform_beginning=True):

            with logger_config.stopwatch_with_label("Check that equipment in network matrix is defined with the same subsystem"):
                for equipment in self.all_matrix_flow_equipments_definitions_instances:
                    all_subsystems = equipment.all_subsystems_detected_in_flow_matrix
                    if len(all_subsystems) > 1:
                        logger_config.print_and_log_error(f"Equipment {equipment.name} is defined with several subsystems {[subsystem.name for subsystem in all_subsystems]}")

    def create_reports_after_matching_network_conf_files(self, equipments_library: equipments.NetworkConfFilesEquipmentsLibrary) -> None:
        logger_config.print_and_log_warning(f"After scanning network flow matrix, {len(equipments_library.wrong_equipment_name_allocated_to_this_ip_by_mistake)} wrong IP address definition")
        logger_config.print_and_log_warning(
            f"'\n'{'\nWrong IP:'.join([wrong_ip.wrong_equipment_name_allocated_to_this_ip_by_mistake + ";"+ wrong_ip.raw_ip_address+";"+ ",".join(wrong_ip.equipments_names_having_genuinely_this_ip_address) +";" +",".join([str(matrix_line) for matrix_line in wrong_ip.matrix_line_ids_referencing]) for wrong_ip in equipments_library.wrong_equipment_name_allocated_to_this_ip_by_mistake])}"
        )

        with open(f"{constants.OUTPUT_PARENT_DIRECTORY_NAME}/matrix_wrong_ip.txt", mode="w", encoding="utf-8") as matrix_wrong_ip_file:
            for wrong_ip in sorted(equipments_library.wrong_equipment_name_allocated_to_this_ip_by_mistake, key=lambda x: x.wrong_equipment_name_allocated_to_this_ip_by_mistake):
                matrix_wrong_ip_file.write(
                    "Wrong IP:"
                    + wrong_ip.wrong_equipment_name_allocated_to_this_ip_by_mistake
                    + ";"
                    + wrong_ip.raw_ip_address
                    + ";"
                    + ",".join(wrong_ip.equipments_names_having_genuinely_this_ip_address)
                    + ";"
                    + ",".join([str(matrix_line) for matrix_line in wrong_ip.matrix_line_ids_referencing])
                    + "\n"
                )

        for directory_path in [constants.OUTPUT_PARENT_DIRECTORY_NAME]:
            file_utils.create_folder_if_not_exist(directory_path)

        dump_matrix_subsystems_to_json(self, f"{constants.OUTPUT_PARENT_DIRECTORY_NAME}/matrix_all_subsystems_in_flow_matrix.json")
        dump_matrix_equipments_to_json(self, f"{constants.OUTPUT_PARENT_DIRECTORY_NAME}/matrix_all_equipments_in_flow_matrix.json")
        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(
            equipments_library.not_found_equipments_but_defined_in_flow_matrix, f"{constants.OUTPUT_PARENT_DIRECTORY_NAME}/matrix_all_unknown_equipments.json"
        )

        with open(f"{constants.OUTPUT_PARENT_DIRECTORY_NAME}/matrix_all_unknown_equipments.txt", mode="w", encoding="utf-8") as matrix_all_unknown_equipments_file:
            for not_found_eqpt in sorted(equipments_library.not_found_equipments_but_defined_in_flow_matrix, key=lambda x: x.name):
                matrix_all_unknown_equipments_file.write(
                    "Not Found;"
                    + not_found_eqpt.name
                    + ";IP address:"
                    + not_found_eqpt.raw_ip_address
                    + ";Other equipment matching:"
                    + ",".join(not_found_eqpt.alternative_names_matching_ip)
                    + ";"
                    + ",".join([str(matrix_line) for matrix_line in not_found_eqpt.matrix_line_ids_referencing])
                    + "\n"
                )
        with open(f"{constants.OUTPUT_PARENT_DIRECTORY_NAME}/matrix_all_equipments.txt", mode="w", encoding="utf-8") as matrix_all_unknown_equipments_file:
            for equipment in sorted(self.all_matrix_flow_equipments_definitions_instances, key=lambda x: x.name):
                matrix_all_unknown_equipments_file.write(
                    "Equipments;"
                    + equipment.name
                    + f";{len(equipment.all_subsystems_detected_in_flow_matrix)} subsystems found:"
                    + ",".join([subsystem.name for subsystem in equipment.all_subsystems_detected_in_flow_matrix])
                    + ";All subsystems found with number of line identifier:"
                    + "-".join([subsystem.name + ":" + str(len(line_identifiers)) for subsystem, line_identifiers in equipment.all_subsystems_detected_in_flow_matrix_with_lines_identifiers.items()])
                    + ";All subsystems found with line identifier:"
                    + "-".join(
                        [
                            subsystem.name + ":" + ",".join([str(line_identifier_int) for line_identifier_int in line_identifiers])
                            for subsystem, line_identifiers in equipment.all_subsystems_detected_in_flow_matrix_with_lines_identifiers.items()
                        ]
                    )
                    + "\n"
                )
        with open(f"{constants.OUTPUT_PARENT_DIRECTORY_NAME}/matrix_all_equipments_on_multiple_subsystems.txt", mode="w", encoding="utf-8") as matrix_all_unknown_equipments_file:
            for equipment in sorted(
                [equipment for equipment in self.all_matrix_flow_equipments_definitions_instances if len(equipment.all_subsystems_detected_in_flow_matrix) > 1], key=lambda x: x.name
            ):
                matrix_all_unknown_equipments_file.write(
                    ""
                    + equipment.name
                    + f";{len(equipment.all_subsystems_detected_in_flow_matrix)} subsystems:"
                    + ",".join([subsystem.name for subsystem in equipment.all_subsystems_detected_in_flow_matrix])
                    + ";Subsystems with number of occurences:"
                    + "-".join([subsystem.name + ":" + str(len(line_identifiers)) for subsystem, line_identifiers in equipment.all_subsystems_detected_in_flow_matrix_with_lines_identifiers.items()])
                    + ";Subsystems with line ids:"
                    + "-".join(
                        [
                            subsystem.name + ":" + ",".join([str(line_identifier_int) for line_identifier_int in line_identifiers])
                            for subsystem, line_identifiers in equipment.all_subsystems_detected_in_flow_matrix_with_lines_identifiers.items()
                        ]
                    )
                    + "\n"
                )

        with open(f"{constants.OUTPUT_PARENT_DIRECTORY_NAME}/matrix_all_subsystems_in_flow_matrix.txt", mode="w", encoding="utf-8") as matrix_all_unknown_equipments_file:
            for subsystem in sorted(self.all_matrix_flow_subsystems_definitions_instances, key=lambda x: x.name):
                matrix_all_unknown_equipments_file.write(
                    "All_subsystems;" + subsystem.name + ";All equipments found:" + ",".join([equipment.name for equipment in subsystem.all_equipments_detected_in_flow_matrix]) + "\n"
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
    is_deleted: bool
    modif_raw_str: str
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
            modif_raw_str = str(row["Modif"])
            is_deleted = str(modif_raw_str) == "D"
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
                modif_raw_str=modif_raw_str,
                is_deleted=is_deleted,
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
