from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple

from common import json_encoders
from logger import logger_config

from networkflowmatrix import constants

if TYPE_CHECKING:
    from networkflowmatrix.network_conf_files import (
        GenericConfFile,
        NetworkConfFilesDefinedIpAddress,
    )
    from networkflowmatrix.network_conf_files_descriptions_data import (
        ExcelInputFileDescription,
    )

from collections import defaultdict

from networkflowmatrix import (
    ihm_program_builder,
    manual_equipments_builder,
    manual_group_definitions,
    names_equivalences,
)
from networkflowmatrix.groups import Group, GroupDefinition
from networkflowmatrix.network_conf_files import NetworkConfFile

# @dataclass
# class Equipment:
#    eqpt_type: str
#    relative_name: str
#    unique_name: str
#    train_single_unit: Optional["TrainUnbreakableSingleUnit"] = None


@dataclass
class TrainUnbreakableSingleUnit:
    cc_id: int
    emu_id: int
    # equipments: List[Equipment] = field(default_factory=list)


@dataclass
class WrongOrUnknownIpAddressInMatrixFlow:
    wrong_equipment_name_allocated_to_this_ip_by_mistake: str
    raw_ip_address: str
    equipments_names_having_genuinely_this_ip_address: Set[str] = field(default_factory=set)
    matrix_line_ids_referencing: List[int] = field(default_factory=list)


@dataclass
class EquipmentWithWrongOrUnknownIpAddressInMatrixFlow:
    name: str
    wrong_or_unknown_ip_address: List[WrongOrUnknownIpAddressInMatrixFlow] = field(default_factory=list)
    raw_ip_addresses: List[str] = field(default_factory=list)
    matrix_line_ids_referencing: List[int] = field(default_factory=list)


@dataclass
class NotFoundEquipmentButDefinedInMatrixFlow:
    name: str
    raw_ip_address: str
    matrix_line_ids_referencing: List[int] = field(default_factory=list)
    alternative_names_matching_ip: Set[str] = field(default_factory=set)


@dataclass
class NetworkConfFilesDefinedEquipment:
    name: str
    source_label: str
    library: "NetworkConfFilesEquipmentsLibrary"
    _equipment_types: Set[str] = field(default_factory=set)
    _alternative_identifiers: Set[str] = field(default_factory=set)
    ip_addresses: List["NetworkConfFilesDefinedIpAddress"] = field(default_factory=list)
    groups: List[Group] = field(default_factory=list)

    def __post_init__(self) -> None:
        assert self.name
        assert "\n" not in self.name, f"Invalid name {self.name} from {self.source_label}"
        assert isinstance(self.name, str)
        if self.name in self.library.names_equivalences_manager.names_equivalences_data.values():
            alternative_names = [key for key, val in self.library.names_equivalences_manager.names_equivalences_data.items() if val == self.name]
            for alternative_name in alternative_names:
                self.add_alternative_identifier(alternative_name)

    @property
    def equipment_types(self) -> Set[str]:
        return self._equipment_types

    @property
    def alternative_identifiers(self) -> Set[str]:
        return self._alternative_identifiers

    def add_alternative_identifier(self, alternative_identifier: str) -> None:
        assert alternative_identifier
        assert isinstance(alternative_identifier, str)
        self._alternative_identifiers.add(alternative_identifier)
        self.library.network_conf_files_defined_equipments_by_id[alternative_identifier] = self

    def add_equipment_type(self, equipment_type: str) -> None:
        assert equipment_type
        assert isinstance(equipment_type, str)
        self._equipment_types.add(equipment_type)

        # logger_config.print_and_log_info(f"Equipment {self.name}: add type {equipment_type}")

        if equipment_type not in self.library.network_conf_files_defined_equipments_by_type:
            self.library.network_conf_files_defined_equipments_by_type[equipment_type] = []

        if self not in self.library.network_conf_files_defined_equipments_by_type[equipment_type]:
            self.library.network_conf_files_defined_equipments_by_type[equipment_type].append(self)

    def add_ip_address(self, ip_address: "NetworkConfFilesDefinedIpAddress") -> None:
        assert ip_address not in self.ip_addresses, f"{self.name} has already ip {ip_address}"

        if [existing_ip for existing_ip in self.ip_addresses if existing_ip.ip_raw == ip_address.ip_raw]:
            logger_config.print_and_log_error(f"Ip address {ip_address.ip_raw} already exists for {self.name}, could not add {ip_address} to the same equipment")

        else:
            ip_address_raw = ip_address.ip_raw
            self.ip_addresses.append(ip_address)

            if ip_address_raw not in self.library._network_conf_files_defined_equipments_by_raw_ip_addresses:
                self.library._network_conf_files_defined_equipments_by_raw_ip_addresses[ip_address_raw] = []

            if self in self.library._network_conf_files_defined_equipments_by_raw_ip_addresses[ip_address_raw]:
                logger_config.print_and_log_error(f"IP address {ip_address_raw} already defined. {self.name} {self._equipment_types} Will exist twice")

            self.library._network_conf_files_defined_equipments_by_raw_ip_addresses[ip_address_raw].append(self)

            # Check consistency
            seen_ids = set()
            for obj in self.library._network_conf_files_defined_equipments_by_raw_ip_addresses[ip_address_raw]:
                assert id(obj) not in seen_ids, f"{self.library._network_conf_files_defined_equipments_by_raw_ip_addresses[ip_address_raw]} is defined several times by {ip_address_raw} "
                seen_ids.add(id(obj))


class NetworkConfFilesEquipmentsLibrary:

    class Builder:
        def __init__(self) -> None:
            self.conf_files: List["GenericConfFile"] = []
            self.equipments_library_being_created = NetworkConfFilesEquipmentsLibrary()

        def add_network_config_file_with_excel_descriptions(self, excel_descriptions: List["ExcelInputFileDescription"]) -> "NetworkConfFilesEquipmentsLibrary.Builder":
            for excel_description in excel_descriptions:
                self.conf_files.append(NetworkConfFile.Builder.build_with_excel_description(self.equipments_library_being_created, excel_description))
            return self

        def add_network_config_file_with_excel_description(self, excel_description: "ExcelInputFileDescription") -> "NetworkConfFilesEquipmentsLibrary.Builder":
            self.conf_files.append(NetworkConfFile.Builder.build_with_excel_file(self.equipments_library_being_created, excel_description.excel_file_full_path, excel_description.all_tabs_definition))
            return self

        def add_ihm_programm(self, excel_file_full_path: str) -> "NetworkConfFilesEquipmentsLibrary.Builder":

            self.conf_files.append(
                ihm_program_builder.IhmProgrammConfFile.Builder.build_with_excel_file(equipments_library=self.equipments_library_being_created, excel_file_full_path=excel_file_full_path)
            )
            return self

        def add_fdiff_clients(self, excel_file_full_path: str) -> "NetworkConfFilesEquipmentsLibrary.Builder":

            self.conf_files.append(
                ihm_program_builder.FdiffClientsConfFile.Builder.build_with_excel_file(equipments_library=self.equipments_library_being_created, excel_file_full_path=excel_file_full_path)
            )
            return self

        def add_manual_entries(self) -> "NetworkConfFilesEquipmentsLibrary.Builder":
            self.conf_files.append(manual_equipments_builder.SithConfFile.Builder.build(equipments_library=self.equipments_library_being_created))
            self.conf_files.append(manual_equipments_builder.TrainsConfFile.Builder.build(equipments_library=self.equipments_library_being_created))
            self.conf_files.append(manual_equipments_builder.OtherManualIpAddresses.Builder.build(equipments_library=self.equipments_library_being_created))
            return self

        def build(self) -> "NetworkConfFilesEquipmentsLibrary":
            manual_group_definitions.construct_manual_groups(self.equipments_library_being_created)
            self.equipments_library_being_created.print_stats()
            self.equipments_library_being_created.check_consistency()
            self.equipments_library_being_created.dump_to_json_file(f"{constants.OUTPUT_PARENT_DIRECTORY_NAME}/all_equipments_in_conf_files_before_matching_network_matrix.json")

            return self.equipments_library_being_created

    def __init__(self) -> None:
        self.all_network_conf_files_defined_equipments: List[NetworkConfFilesDefinedEquipment] = []
        self.network_conf_files_defined_equipments_by_id: Dict[str, NetworkConfFilesDefinedEquipment] = {}
        self.network_conf_files_defined_equipments_by_type: Dict[str, List[NetworkConfFilesDefinedEquipment]] = defaultdict()
        self._network_conf_files_defined_equipments_by_raw_ip_addresses: Dict[str, List[NetworkConfFilesDefinedEquipment]] = {}
        self.all_trains_unbreakable_units: List[TrainUnbreakableSingleUnit] = []
        self.all_ignored_trains_unbreakable_units: List[TrainUnbreakableSingleUnit] = []
        self.all_trains_unbreakable_units_by_cc_id: Dict[int, TrainUnbreakableSingleUnit] = {}
        self.all_trains_unbreakable_units_by_emu_id: Dict[int, TrainUnbreakableSingleUnit] = {}
        self.not_found_equipments_but_defined_in_flow_matrix: List[NotFoundEquipmentButDefinedInMatrixFlow] = []
        self.all_groups: List[Group] = []
        self.create_train_unbreakable_units()
        self.names_equivalences_manager = names_equivalences.NamesEquivalences(manual_equipments_builder.names_equivalences_data)
        self.wrong_equipment_name_allocated_to_this_ip_by_mistake: List[WrongOrUnknownIpAddressInMatrixFlow] = []

    def add_wrong_or_unknown_ip_address_in_matrix_flow(
        self, wrong_equipment_name_allocated_to_this_ip_by_mistake: str, raw_ip_address: str, equipments_names_having_genuinely_this_ip_address: Set[str], matrix_line_id_referencing: int
    ) -> WrongOrUnknownIpAddressInMatrixFlow:
        logger_config.print_and_log_error(
            f"Error line {matrix_line_id_referencing}. Bad IP {raw_ip_address} for {wrong_equipment_name_allocated_to_this_ip_by_mistake}. This IP is allocated to {','.join(equipments_names_having_genuinely_this_ip_address)}",
        )

        wrong_eqpts = [
            wrong
            for wrong in self.wrong_equipment_name_allocated_to_this_ip_by_mistake
            if wrong.wrong_equipment_name_allocated_to_this_ip_by_mistake == wrong_equipment_name_allocated_to_this_ip_by_mistake and wrong.raw_ip_address == raw_ip_address
        ]
        if wrong_eqpts:
            wrong_ip_def = wrong_eqpts[0]
        else:
            wrong_ip_def = WrongOrUnknownIpAddressInMatrixFlow(
                wrong_equipment_name_allocated_to_this_ip_by_mistake=wrong_equipment_name_allocated_to_this_ip_by_mistake,
                raw_ip_address=raw_ip_address,
            )
            self.wrong_equipment_name_allocated_to_this_ip_by_mistake.append(wrong_ip_def)

        wrong_ip_def.equipments_names_having_genuinely_this_ip_address = wrong_ip_def.equipments_names_having_genuinely_this_ip_address.union(equipments_names_having_genuinely_this_ip_address)
        # assert (
        #    matrix_line_id_referencing not in wrong_ip_def.matrix_line_ids_referencing
        # ), f"{matrix_line_id_referencing} already defined in {wrong_equipment_name_allocated_to_this_ip_by_mistake} for {raw_ip_address} / {equipments_names_having_genuinely_this_ip_address}"
        wrong_ip_def.matrix_line_ids_referencing.append(matrix_line_id_referencing)

        return wrong_ip_def

    def check_consistency(self) -> None:
        # logger_config.print_and_log_info(f"The network conf files library contains {len(self.all_network_conf_files_defined_equipments)} equipments in total")
        with logger_config.stopwatch_with_label("Check that all groups have equipment"):
            for group in self.all_groups:
                assert group
                assert group.equipments, f"Group {group.definition} has no equipment"
                assert len(group.equipments) > 0, f"Group {group.definition} has no equipment"

        with logger_config.stopwatch_with_label("Check that all network_conf_files_defined_equipments_by_raw_ip_addresses are unique"):
            for items in self._network_conf_files_defined_equipments_by_raw_ip_addresses.values():
                seen_ids = set()

                for obj in items:
                    assert id(obj) not in seen_ids
                    seen_ids.add(id(obj))

    def print_stats(self) -> None:
        logger_config.print_and_log_info(f"The network conf files library contains {len(self.all_network_conf_files_defined_equipments)} equipments in total")

    def is_existing_network_conf_file_eqpt_by_name(self, name: str) -> bool:
        return name in self.network_conf_files_defined_equipments_by_id

    def get_existing_equipment_by_name(self, expected_equipment_name: str, allow_not_exact_name: bool) -> Optional["NetworkConfFilesDefinedEquipment"]:
        equipment_in_network_conf_file_by_name = (
            self.network_conf_files_defined_equipments_by_id[expected_equipment_name] if expected_equipment_name in self.network_conf_files_defined_equipments_by_id else None
        )
        if equipment_in_network_conf_file_by_name:
            return equipment_in_network_conf_file_by_name

        if allow_not_exact_name:
            for equipment in self.all_network_conf_files_defined_equipments:
                if equipment.name in expected_equipment_name:
                    logger_config.print_and_log_info(f"Add alternative name {expected_equipment_name} for {equipment.name}")
                    equipment.add_alternative_identifier(expected_equipment_name)

                    return equipment

        return None

    def get_existing_equipment_by_raw_ip_address(self, expected_raw_ip_address: str) -> List["NetworkConfFilesDefinedEquipment"]:
        found = (
            self._network_conf_files_defined_equipments_by_raw_ip_addresses[expected_raw_ip_address]
            if expected_raw_ip_address in self._network_conf_files_defined_equipments_by_raw_ip_addresses
            else []
        )

        # Check consitency
        seen_ids = set()
        for obj in found:
            assert id(obj) not in seen_ids, f"{obj.name} is defined several times by {expected_raw_ip_address} "
            seen_ids.add(id(obj))

        return found

    def get_existing_equipments_by_group(self, expected_group_name: str, expected_group_subnet_and_mask: str) -> List["NetworkConfFilesDefinedEquipment"]:

        group_found = [group for group in self.all_groups if group.definition.name == expected_group_name and group.definition.subnet_and_mask == expected_group_subnet_and_mask]
        if group_found:
            assert len(group_found) == 1
            return group_found[0].equipments
        return []

    def get_existing_network_conf_file_eqpt_by_name(self, name: str) -> Optional["NetworkConfFilesDefinedEquipment"]:
        if self.is_existing_network_conf_file_eqpt_by_name(name):
            return self.network_conf_files_defined_equipments_by_id[name]
        return None

    def get_or_create_network_conf_file_eqpt_if_not_exist_by_name(self, name: str, source_label_for_creation: str) -> "NetworkConfFilesDefinedEquipment":
        if self.is_existing_network_conf_file_eqpt_by_name(name):
            return self.network_conf_files_defined_equipments_by_id[name]
        equipment = NetworkConfFilesDefinedEquipment(name=name, library=self, source_label=source_label_for_creation)
        self.network_conf_files_defined_equipments_by_id[name] = equipment
        self.all_network_conf_files_defined_equipments.append(equipment)

        return equipment

    def is_existing_train_unbreakable_unit_by_cc_id(self, cc_id: int) -> bool:
        return cc_id in self.all_trains_unbreakable_units_by_cc_id

    def get_existing_train_unbreakable_unit_by_cc_id(self, cc_id: int) -> Optional["TrainUnbreakableSingleUnit"]:
        if self.is_existing_train_unbreakable_unit_by_cc_id(cc_id):
            return self.all_trains_unbreakable_units_by_cc_id[cc_id]
        return None

    def is_existing_train_unbreakable_unit_by_emu_id(self, emu_id: int) -> bool:
        return emu_id in self.all_trains_unbreakable_units_by_emu_id

    def get_existing_train_unbreakable_unit_by_emu_id(self, emu_id: int) -> Optional["TrainUnbreakableSingleUnit"]:
        if self.is_existing_train_unbreakable_unit_by_emu_id(emu_id):
            return self.all_trains_unbreakable_units_by_emu_id[emu_id]
        return None

    def get_or_create_group_and_add_equipment(self, group_definition: GroupDefinition, equipment: "NetworkConfFilesDefinedEquipment") -> None:
        group = self.get_or_create_group(group_definition=group_definition)
        group.add_equipment(equipment)

    def get_or_create_group(self, group_definition: GroupDefinition) -> Group:
        assert isinstance(group_definition, GroupDefinition), f"Group definition {group_definition} has bad type {type(group_definition)}"

        group_found = [group for group in self.all_groups if group.definition == group_definition]

        assert len(group_found) < 2
        if group_found:
            return group_found[0]

        else:
            group = Group(group_definition)
            self.all_groups.append(group)
            return group

    def create_train_unbreakable_units(self) -> None:
        for i in constants.ALL_USED_TRAINS_IDS:
            train_unbreakable_unit = TrainUnbreakableSingleUnit(cc_id=i, emu_id=4000 + i)
            self.all_trains_unbreakable_units.append(train_unbreakable_unit)
            self.all_trains_unbreakable_units_by_cc_id[train_unbreakable_unit.cc_id] = train_unbreakable_unit
            self.all_trains_unbreakable_units_by_emu_id[train_unbreakable_unit.emu_id] = train_unbreakable_unit

        for i in constants.TO_IGNORE_TRAINS_IDS:
            train_unbreakable_unit = TrainUnbreakableSingleUnit(cc_id=i, emu_id=4000 + i)
            self.all_ignored_trains_unbreakable_units.append(train_unbreakable_unit)

    def add_not_found_equipment_but_defined_in_network_flow_matrix(
        self, equipment_name: str, eqpt_ip_address_raw: str, matrix_line_id_referencing: int, equipments_in_network_conf_file_matching_ip_address: List["NetworkConfFilesDefinedEquipment"]
    ) -> NotFoundEquipmentButDefinedInMatrixFlow:
        logger_config.print_and_log_error(
            to_print_and_log=f"{matrix_line_id_referencing}: {equipment_name} not defined in any network conf file.Ip address {eqpt_ip_address_raw} defined for {[eqpt.name for eqpt in equipments_in_network_conf_file_matching_ip_address]}",
            do_not_print=True,
        )
        equipments = [
            not_found_equipment
            for not_found_equipment in self.not_found_equipments_but_defined_in_flow_matrix
            if not_found_equipment.name == equipment_name and not_found_equipment.raw_ip_address == eqpt_ip_address_raw
        ]
        assert len(equipments) < 2
        if equipments:
            equipment = equipments[0]
        else:
            equipment = NotFoundEquipmentButDefinedInMatrixFlow(name=equipment_name, raw_ip_address=eqpt_ip_address_raw)
            self.not_found_equipments_but_defined_in_flow_matrix.append(equipment)

        for equipment_in_network_conf_file_matching_ip_address in equipments_in_network_conf_file_matching_ip_address:
            equipment.alternative_names_matching_ip.add(equipment_in_network_conf_file_matching_ip_address.name)

        equipment.matrix_line_ids_referencing.append(matrix_line_id_referencing)

        return equipment

    def dump_to_json_file(self, output_json_file_full_path: str) -> None:
        data_to_dump: List[Tuple] = []
        for equipment in self.all_network_conf_files_defined_equipments:
            data_to_dump.append(
                (
                    f"name:{equipment.name}",
                    f"Source:{equipment.source_label}",
                    f"Types:{', '.join(list(equipment.equipment_types))}",
                    f"Alternative ids:{', '.join([str(alter) for alter in equipment.alternative_identifiers])}",
                    f"Ip:{', '.join([ip.ip_raw for ip in equipment.ip_addresses])}",
                    f"Groups:{', '.join([group.definition.name + ' ' + group.definition.subnet_and_mask for  group in equipment.groups])}",
                )
            )

        for group in self.all_groups:
            data_to_dump.append(
                (
                    group.definition,
                    "Equipments:"
                    + ",".join(
                        [equipment.name for equipment in group.equipments],
                    ),
                )
            )

        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(data_to_dump, output_json_file_full_path)
