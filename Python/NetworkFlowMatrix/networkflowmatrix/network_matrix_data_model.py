import inspect
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Self, Set, Tuple, cast

import pandas
from common import pandas_utils, string_utils
from logger import logger_config

from networkflowmatrix import (
    constants,
    equipments,
    network_entity_provider,
    reports_creation,
)

INVALID_IP_ADDRESS = "INVALID_IP_ADDRESS"
MISSING_IP_ADDRESS = "MISSING_IP_ADDRESS"


@dataclass
class TypeDefinedInFlowMatrix:
    name: str

    def __post_init__(self) -> None:
        self._all_matrix_lines_ids_containing_it: List[int] = []
        self._all_endpoints: List[FlowEndPoint] = []

    def add_endpoint(self, endpoint: "FlowEndPoint") -> None:
        self._all_endpoints.append(endpoint)
        if endpoint.matrix_line_identifier not in self._all_matrix_lines_ids_containing_it:
            self._all_matrix_lines_ids_containing_it.append(endpoint.matrix_line_identifier)

    def __hash__(self) -> int:
        return hash(self.name)

    @property
    def network_flow_matrix_equipments_detected(self) -> Set["EquipmentDefinedInFlowMatrix"]:
        all_network_flow_equipments_detected: Set[EquipmentDefinedInFlowMatrix] = set()
        for endpoint in self._all_endpoints:
            all_network_flow_equipments_detected.update(endpoint.network_flow_equipments_detected)
        return all_network_flow_equipments_detected

    @property
    def network_conf_files_equipments_detected(self) -> Set[equipments.NetworkConfFilesDefinedEquipment]:
        all_network_conf_files_equipments_detected: Set[equipments.NetworkConfFilesDefinedEquipment] = set()
        for endpoint in self._all_endpoints:
            all_network_conf_files_equipments_detected.update(endpoint.network_conf_files_equipments_detected)
        return all_network_conf_files_equipments_detected


class SubSystemDefinedInFlowMatrix:

    @staticmethod
    def is_existing_by_name(network_flow_matrix: "NetworkFlowMatrix", name: str) -> bool:
        return name in network_flow_matrix.all_matrix_flow_subsystems_definitions_instances_by_name

    @staticmethod
    def get_or_create_if_not_exist_by_name(network_flow_matrix: "NetworkFlowMatrix", name: str) -> "SubSystemDefinedInFlowMatrix":
        if SubSystemDefinedInFlowMatrix.is_existing_by_name(network_flow_matrix, name):
            return network_flow_matrix.all_matrix_flow_subsystems_definitions_instances_by_name[name]
        subsystem = SubSystemDefinedInFlowMatrix(network_flow_matrix=network_flow_matrix, name=name)
        network_flow_matrix.all_matrix_flow_subsystems_definitions_instances_by_name[name] = subsystem
        network_flow_matrix.all_matrix_flow_subsystems_definitions_instances.append(subsystem)

        return subsystem

    def __init__(self, name: str, network_flow_matrix: "NetworkFlowMatrix") -> None:
        self.all_equipments_detected_in_flow_matrix: List["EquipmentDefinedInFlowMatrix"] = []
        self.name = name
        self.network_flow_matrix = network_flow_matrix


class PortInFlowMatrix:
    def __init__(self, raw_port: Optional[str | int]) -> None:
        pass


class EquipmentDefinedInFlowMatrix:

    @staticmethod
    def is_existing_by_name(network_flow_matrix: "NetworkFlowMatrix", name: str) -> bool:
        return name in network_flow_matrix.all_matrix_flow_equipments_by_name

    @staticmethod
    def get_or_create_equipment_if_not_exist(
        network_flow_matrix: "NetworkFlowMatrix", name: str, subsystem_detected_in_flow_matrix: SubSystemDefinedInFlowMatrix, raw_ip_address: str
    ) -> "EquipmentDefinedInFlowMatrix":
        if EquipmentDefinedInFlowMatrix.is_existing_by_name(network_flow_matrix, name):
            equipment = network_flow_matrix.all_matrix_flow_equipments_by_name[name]
            equipment.raw_ip_addresses.add(raw_ip_address)
            return equipment
        equipment = EquipmentDefinedInFlowMatrix(name=name, network_flow_matrix=network_flow_matrix)
        equipment.raw_ip_addresses.add(raw_ip_address)
        network_flow_matrix.all_matrix_flow_equipments_by_name[name] = equipment
        network_flow_matrix.all_matrix_flow_equipments_definitions_instances.append(equipment)
        subsystem_detected_in_flow_matrix.all_equipments_detected_in_flow_matrix.append(equipment)
        return equipment

    def __init__(self, name: str, network_flow_matrix: "NetworkFlowMatrix") -> None:
        self.raw_ip_addresses: Set[str] = set()
        # self.ip_addresses: List[ipaddress.IPv4Address] = []
        self.all_subsystems_detected_in_flow_matrix: List[SubSystemDefinedInFlowMatrix] = []
        self.all_subsystems_detected_in_flow_matrix_with_lines_identifiers: Dict[SubSystemDefinedInFlowMatrix, List[int]] = {}

        self.all_types_detected_in_flow_matrix: Set[TypeDefinedInFlowMatrix] = set()
        self.all_types_detected_in_flow_matrix_with_lines_identifiers: Dict[TypeDefinedInFlowMatrix, List[int]] = {}

        self.name = name
        self.network_flow_matrix = network_flow_matrix

    @property
    def all_types_names_detected_in_flow_matrix(self) -> List[str]:
        return [type_it.name for type_it in self.all_types_detected_in_flow_matrix]

    def add_subsystem_detected_in_flow_matrix_with_lines_identifiers(self, subsystem_detected_in_flow_matrix: SubSystemDefinedInFlowMatrix, matrix_line_identifier: int) -> None:
        if subsystem_detected_in_flow_matrix not in self.all_subsystems_detected_in_flow_matrix_with_lines_identifiers:
            self.all_subsystems_detected_in_flow_matrix_with_lines_identifiers[subsystem_detected_in_flow_matrix] = []
        self.all_subsystems_detected_in_flow_matrix_with_lines_identifiers[subsystem_detected_in_flow_matrix].append(matrix_line_identifier)

        if subsystem_detected_in_flow_matrix not in self.all_subsystems_detected_in_flow_matrix:
            self.all_subsystems_detected_in_flow_matrix.append(subsystem_detected_in_flow_matrix)

        if self not in subsystem_detected_in_flow_matrix.all_equipments_detected_in_flow_matrix:
            subsystem_detected_in_flow_matrix.all_equipments_detected_in_flow_matrix.append(self)

    def add_type_detected_in_flow_matrix_with_lines_identifiers(self, type_detected_in_flow_matrix: TypeDefinedInFlowMatrix, matrix_line_identifier: int) -> None:
        if type_detected_in_flow_matrix not in self.all_types_detected_in_flow_matrix_with_lines_identifiers:
            self.all_types_detected_in_flow_matrix_with_lines_identifiers[type_detected_in_flow_matrix] = []
        self.all_types_detected_in_flow_matrix_with_lines_identifiers[type_detected_in_flow_matrix].append(matrix_line_identifier)

        self.all_types_detected_in_flow_matrix.add(type_detected_in_flow_matrix)


@dataclass
class FlowEndPoint:
    matrix_line_identifier: int
    network_flow_matrix: "NetworkFlowMatrix"
    subsystem_raw: str
    type_raw: str
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

        self.type_raw = self.type_raw.strip() if isinstance(self.type_raw, str) else ""
        self.network_matrix_defined_type = self.network_flow_matrix.get_or_create_type_if_not_exist_by_name(self.type_raw)
        self.network_matrix_defined_type.add_endpoint(self)
        self.raw_ip_addresses: List[str] = []

        self.network_flow_equipments_detected: List[EquipmentDefinedInFlowMatrix] = []
        self.network_conf_files_equipments_detected: List[equipments.NetworkConfFilesDefinedEquipment] = []
        self.equipments_names: List[str] = [equipment_name.strip().upper() for equipment_name in self.equipment_cell_raw.split("\n") if equipment_name.strip() != ""]

        self.network_flow_matrix_line: "NetworkFlowMatrixLine" = cast("NetworkFlowMatrixLine", None)

        if not isinstance(self.ip_raw, str):
            self.ip_raw = None
        else:
            self.raw_ip_addresses = [raw_ip.strip() for raw_ip in self.ip_raw.split("\n")]

        self.subsystem_detected_in_flow_matrix = SubSystemDefinedInFlowMatrix.get_or_create_if_not_exist_by_name(network_flow_matrix=self.network_flow_matrix, name=self.subsystem_raw.strip().upper())

    def get_all_network_entity_providers(self) -> Set[network_entity_provider.NetworkEntityProvider]:
        return set([equipment.network_provider for equipment in self.network_conf_files_equipments_detected])

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
                    self.equipment_in_network_conf_file_by_name = equipments_library.get_existing_equipment_by_name(expected_equipment_name=equipment_name, allow_not_exact_name=True)
                    logger_config.print_and_log_error(
                        to_print_and_log=f"Error at line {self.matrix_line_identifier}: no IP found for {equipment_name} (not enough lines). In network conf, equipment {(self.equipment_in_network_conf_file_by_name.name+ ' with Ip: ' if self.equipment_in_network_conf_file_by_name else 'Not found')} {",".join([ip.ip_raw for ip in self.equipment_in_network_conf_file_by_name.ip_addresses]) if self.equipment_in_network_conf_file_by_name else 'found'}"
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

                self.equipment_in_network_conf_file_by_name = equipments_library.get_existing_equipment_by_name(expected_equipment_name=equipment_name, allow_not_exact_name=True)
                if self.equipment_in_network_conf_file_by_name:
                    self.network_conf_files_equipments_detected.append(self.equipment_in_network_conf_file_by_name)
                self.equipments_in_network_conf_file_matching_ip_address = equipments_library.get_existing_equipment_by_raw_ip_address(eqpt_ip_address_raw)

                self.equipments_in_network_conf_file_matching_group = equipments_library.get_existing_equipments_by_group(
                    expected_group_name=equipment_name, expected_group_subnet_and_mask=eqpt_ip_address_raw
                )
                self.network_conf_files_equipments_detected += self.equipments_in_network_conf_file_matching_ip_address + self.equipments_in_network_conf_file_matching_group

                if not self.equipment_in_network_conf_file_by_name and not self.equipments_in_network_conf_file_matching_group:
                    # Equipment not defined
                    equipments_library.add_not_found_equipment_but_defined_in_network_flow_matrix(
                        equipment_name=equipment_name,
                        eqpt_ip_address_raw=eqpt_ip_address_raw,
                        matrix_line_id_referencing=self.matrix_line_identifier,
                        equipments_in_network_conf_file_matching_ip_address=self.equipments_in_network_conf_file_matching_ip_address,
                    )

                elif self.equipment_in_network_conf_file_by_name and eqpt_ip_address_raw not in [ip.ip_raw for ip in self.equipment_in_network_conf_file_by_name.ip_addresses]:
                    # Equipment found but IP not found in this eqpt
                    logger_config.print_and_log_error(
                        to_print_and_log=f"At line {self.matrix_line_identifier}: equipment {equipment_name} defined with {eqpt_ip_address_raw}, but this IP is not defined for this equipment in network conf files. Known IP are {','.join([ip.ip_raw for ip in self.equipment_in_network_conf_file_by_name.ip_addresses])}. This IP is defined for {','.join([eqpt.name for eqpt in self.equipments_in_network_conf_file_matching_ip_address])}",
                        do_not_print=True,
                    )
                    equipments_library.add_wrong_or_unknown_ip_address_in_matrix_flow(
                        wrong_equipment_name_allocated_to_this_ip_by_mistake=equipment_name,
                        raw_ip_address=eqpt_ip_address_raw,
                        equipments_names_having_genuinely_this_ip_address=set([eqpt.name for eqpt in self.equipments_in_network_conf_file_matching_ip_address]),
                        matrix_line_id_referencing=self.matrix_line_identifier,
                    )

                equipment_detected_in_flow_matrix = EquipmentDefinedInFlowMatrix.get_or_create_equipment_if_not_exist(
                    network_flow_matrix=self.network_flow_matrix,
                    name=equipment_name,
                    subsystem_detected_in_flow_matrix=self.subsystem_detected_in_flow_matrix,
                    raw_ip_address=eqpt_ip_address_raw,
                )
                equipment_detected_in_flow_matrix.add_subsystem_detected_in_flow_matrix_with_lines_identifiers(
                    subsystem_detected_in_flow_matrix=self.subsystem_detected_in_flow_matrix, matrix_line_identifier=self.matrix_line_identifier
                )

                equipment_detected_in_flow_matrix.add_type_detected_in_flow_matrix_with_lines_identifiers(
                    type_detected_in_flow_matrix=self.network_matrix_defined_type, matrix_line_identifier=self.matrix_line_identifier
                )

                self.network_flow_equipments_detected.append(equipment_detected_in_flow_matrix)
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
            matrice_line_identifier = pandas_utils.element_as_casted_int(row, "ID")
            subsystem_raw = row["src \nss-système"]
            type_raw = row["src \nType"]
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
                type_raw=type_raw,
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
            matrice_line_identifier = pandas_utils.element_as_casted_int(row, "ID")
            subsystem_raw = row["dst \nss-système"]
            type_raw = row["dst\nType"]
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
                type_raw=type_raw,
            )

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.cast_type == constants.CastType.MULTICAST:
            assert isinstance(self.group_multicast_raw, str), f"{self.matrix_line_identifier} : empty group {self.group_multicast_raw} for multicast {self.cast_type}"


@dataclass
class NetworkFlowMatrix:
    network_flow_matrix_lines: List["NetworkFlowMatrixLine"] = field(default_factory=list)
    network_flow_matrix_lines_not_deleted: List["NetworkFlowMatrixLine"] = field(default_factory=list)
    network_flow_matrix_lines_by_identifier: Dict[int, "NetworkFlowMatrixLine"] = field(default_factory=dict)

    all_types_defined: List[TypeDefinedInFlowMatrix] = field(default_factory=list)

    all_equipments_names: Set[str] = field(default_factory=set)
    all_equipments_names_with_subsystem: set[Tuple[str, str]] = field(default_factory=set)

    all_matrix_flow_equipments_definitions_instances: List["EquipmentDefinedInFlowMatrix"] = field(default_factory=list)
    all_matrix_flow_equipments_by_name: Dict[str, "EquipmentDefinedInFlowMatrix"] = field(default_factory=dict)

    all_matrix_flow_subsystems_definitions_instances: List["SubSystemDefinedInFlowMatrix"] = field(default_factory=list)
    all_matrix_flow_subsystems_definitions_instances_by_name: Dict[str, "SubSystemDefinedInFlowMatrix"] = field(default_factory=dict)

    class Builder:
        def __init__(self) -> None:
            self.network_flow_matrix = NetworkFlowMatrix()

        def excel_file(self, excel_file_full_path: str, sheet_name: str = "Matrice_de_Flux_SITE") -> Self:
            main_data_frame = pandas.read_excel(excel_file_full_path, skiprows=[0, 1, 2, 3, 4], sheet_name=sheet_name)
            logger_config.print_and_log_info(to_print_and_log=f"Flow matrix {excel_file_full_path} has {len(main_data_frame)} items")
            logger_config.print_and_log_info(to_print_and_log=f"Flow matrix {excel_file_full_path} columns  {main_data_frame.columns[:4]} ...")

            for _, row in main_data_frame.iterrows():
                network_flow_matrix_line = NetworkFlowMatrixLine.Builder.build_with_row(row=row, network_flow_matrix=self.network_flow_matrix)
                if network_flow_matrix_line:
                    self.network_flow_matrix.network_flow_matrix_lines.append(network_flow_matrix_line)
                    self.network_flow_matrix.network_flow_matrix_lines_by_identifier[network_flow_matrix_line.identifier_int] = network_flow_matrix_line
                    if not network_flow_matrix_line.is_deleted:
                        self.network_flow_matrix.network_flow_matrix_lines_not_deleted.append(network_flow_matrix_line)

            return self

        def build(self) -> "NetworkFlowMatrix":
            assert self.network_flow_matrix.network_flow_matrix_lines, "matrix is empty"
            assert self.network_flow_matrix.network_flow_matrix_lines_by_identifier, "matrix is empty"
            return self.network_flow_matrix

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

        self.check_flow_are_correctly_tagged_on_sncf_network()

        reports_creation.create_reports_after_matching_network_conf_files_and_flow_matrix(self, equipments_library)

    def check_flow_are_correctly_tagged_on_sncf_network(self) -> bool:
        with logger_config.stopwatch_with_label({inspect.stack(0)[0].function}, inform_beginning=True):

            assert self.network_flow_matrix_lines_not_deleted
            for matrix_line in self.network_flow_matrix_lines_not_deleted:

                if matrix_line.is_sncf_network_detected() != matrix_line.declared_on_sncf_network_on_matrix:
                    logger_config.print_and_log_error(
                        f"{inspect.stack(0)[0].function}: Flow {matrix_line.identifier_int} {matrix_line.full_label_auto_one_line} defined as {matrix_line.declared_on_sncf_network_on_matrix_raw_str} but should be declared {matrix_line.is_sncf_network_detected()}"
                    )

            return False

    def check_consistency(self) -> None:

        with logger_config.stopwatch_with_label("check_consistency", inform_beginning=True):

            with logger_config.stopwatch_with_label("Check that all matrix lines have source and destination on a known network"):
                for matrix_line in self.network_flow_matrix_lines:
                    if not len(matrix_line.source.get_all_network_entity_providers()):
                        logger_config.print_and_log_error(f"Line {matrix_line.identifier_int}, {matrix_line.full_label_auto_one_line}: source does not have known network")
                    if not len(matrix_line.destination.get_all_network_entity_providers()):
                        logger_config.print_and_log_error(f"Line {matrix_line.identifier_int}, {matrix_line.full_label_auto_one_line}: destination does not have known network")

            with logger_config.stopwatch_with_label("Check that equipment in network matrix is always defined with the same subsystem"):
                for equipment in self.all_matrix_flow_equipments_definitions_instances:
                    all_subsystems = equipment.all_subsystems_detected_in_flow_matrix
                    if len(all_subsystems) > 1:
                        logger_config.print_and_log_error(f"Equipment {equipment.name} is defined with several subsystems {[subsystem.name for subsystem in all_subsystems]}")

            with logger_config.stopwatch_with_label("Check that equipment in network matrix is always defined with the same type"):
                for equipment in self.all_matrix_flow_equipments_definitions_instances:
                    all_types_names = equipment.all_types_names_detected_in_flow_matrix
                    if len(all_types_names) > 1:
                        logger_config.print_and_log_error(f"Equipment {equipment.name} is defined with several types {','.join(all_types_names)}")

    def get_or_create_type_if_not_exist_by_name(self, name: str) -> "TypeDefinedInFlowMatrix":
        existing_types = [type_found for type_found in self.all_types_defined if type_found.name == name]
        if existing_types:
            assert len(existing_types) == 1, f"Type {name} found {len(existing_types)} times"
            return existing_types[0]

        self.all_types_defined.append(TypeDefinedInFlowMatrix(name))
        return self.get_or_create_type_if_not_exist_by_name(name)


@dataclass
class NetworkFlowMatrixLine:
    network_flow_matrix: NetworkFlowMatrix
    identifier_int: int
    modif_raw_str: str
    full_label_auto_multiline: str
    sol_bord_raw: str
    seclab_raw: str
    traffic_direction_raw: str
    type_raw: str
    protocole_applicative_raw: str
    protocole_transport_raw: str
    mes_raw: Optional[str]
    prod_mig_essais: Optional[constants.ProdMigrationEssai]
    modification_type: Optional[constants.MatrixFlowModificationType]
    declared_on_sncf_network_on_matrix: bool
    declared_on_sncf_network_on_matrix_raw_str: str

    source: FlowSource
    destination: FlowDestination

    class Builder:

        @staticmethod
        def build_with_row(row: pandas.Series, network_flow_matrix: NetworkFlowMatrix) -> Optional["NetworkFlowMatrixLine"]:
            identifier_raw_str = pandas_utils.optional_element_as_optional_string(row, "ID")
            if identifier_raw_str is None:
                logger_config.print_and_log_warning(f"Empty row with identifier {identifier_raw_str}")
                return None
            if identifier_raw_str in ["nan", "%%%"]:
                logger_config.print_and_log_warning(f"Invalid row with identifier {identifier_raw_str}")
                return None

            identifier_int = pandas_utils.element_as_casted_int(row, "ID")

            modif_raw_str = pandas_utils.optional_element_as_optional_string(row, "Modif")
            modification_type = constants.MatrixFlowModificationType[modif_raw_str.upper()] if modif_raw_str else None
            mes_raw = pandas_utils.optional_element_as_optional_string(row, "MES")
            prod_mig_essais_raw = pandas_utils.optional_element_as_optional_string(row, "Prod/Migration/EssaisTemporaire")
            prod_mig_essais = constants.ProdMigrationEssai[prod_mig_essais_raw] if prod_mig_essais_raw else None
            declared_on_sncf_network_on_matrix_raw_str = pandas_utils.optional_element_as_optional_string(row, "Sur Réseau SNCF")
            declared_on_sncf_network_on_matrix = True if pandas_utils.optional_element_as_optional_string(row, "Sur Réseau SNCF") else False

            full_label_auto = cast(str, row["Lien de com. complet\n(Auto)"])
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
                destination=destination,
                identifier_int=identifier_int,
                full_label_auto_multiline=full_label_auto,
                sol_bord_raw=sol_bord_raw,
                source=source,
                seclab_raw=seclab_raw,
                protocole_applicative_raw=protocole_applicative_raw,
                protocole_transport_raw=protocole_transport_raw,
                traffic_direction_raw=traffic_direction_raw,
                type_raw=type_raw,
                modification_type=modification_type,
                mes_raw=mes_raw,
                declared_on_sncf_network_on_matrix=declared_on_sncf_network_on_matrix,
                declared_on_sncf_network_on_matrix_raw_str=declared_on_sncf_network_on_matrix_raw_str,
                prod_mig_essais=prod_mig_essais,
            )
            source.network_flow_matrix_line = network_flow_matrix_line
            destination.network_flow_matrix_line = network_flow_matrix_line

            return network_flow_matrix_line

    def __post_init__(self) -> None:
        self.is_deleted = self.modification_type == constants.MatrixFlowModificationType.D
        self.full_label_auto_one_line = self.full_label_auto_multiline.replace("\n", "\t")

    def get_all_network_entity_providers(self) -> Set[network_entity_provider.NetworkEntityProvider]:
        all_providers = self.source.get_all_network_entity_providers().union(self.destination.get_all_network_entity_providers())
        # assert self.is_deleted or all_providers, f"Line {self.identifier_int}, no network detected"
        return all_providers

    def is_sncf_network_detected(self) -> bool:
        sncf_networks_detected = self.get_all_network_entity_providers().intersection(set(network_entity_provider.SNCF_NETWORKS))
        return len(sncf_networks_detected) > 0
