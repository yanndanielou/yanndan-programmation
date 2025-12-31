from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, TYPE_CHECKING
from logger import logger_config

if TYPE_CHECKING:
    from networkflowmatrix.network_conf_files import (
        NetworkConfFilesDefinedIpAddress,
    )

NUMBER_OF_TRAINS = 131


@dataclass
class Equipment:
    eqpt_type: str
    relative_name: str
    unique_name: str
    train_single_unit: Optional["TrainUnbreakableSingleUnit"] = None


@dataclass
class TrainUnbreakableSingleUnit:
    cc_id: int
    emu_id: int
    equipments: List[Equipment] = field(default_factory=list)


@dataclass
class NetworkConfFilesDefinedEquipment:
    name: str
    library: "NetworkConfFilesEquipmentsLibrary"
    equipment_types: Set[str] = field(default_factory=set)
    alternative_identifiers: Set[str] = field(default_factory=set)
    ip_addresses: List["NetworkConfFilesDefinedIpAddress"] = field(default_factory=list)

    def __post_init__(self) -> None:
        assert self.name
        assert isinstance(self.name, str)

    def add_ip_address(self, ip_address: "NetworkConfFilesDefinedIpAddress") -> None:
        assert ip_address not in self.ip_addresses
        ip_address_raw = ip_address.ip_raw
        self.ip_addresses.append(ip_address)

        if ip_address_raw not in self.library.network_conf_files_defined_equipments_by_raw_ip_addresses:
            self.library.network_conf_files_defined_equipments_by_raw_ip_addresses[ip_address_raw] = []

        if self in self.library.network_conf_files_defined_equipments_by_raw_ip_addresses[ip_address_raw]:
            logger_config.print_and_log_error(f"IP address {ip_address_raw} already defined. {self.name} {self.equipment_types} Will exist twice")

        self.library.network_conf_files_defined_equipments_by_raw_ip_addresses[ip_address_raw].append(self)


class NetworkConfFilesEquipmentsLibrary:
    def __init__(self) -> None:
        self.all_network_conf_files_defined_equipments: List[NetworkConfFilesDefinedEquipment] = []
        self.network_conf_files_defined_equipments_by_id: Dict[str, NetworkConfFilesDefinedEquipment] = {}
        self.network_conf_files_defined_equipments_by_raw_ip_addresses: Dict[str, List[NetworkConfFilesDefinedEquipment]] = {}
        self.all_trains_unbreakable_units: List[TrainUnbreakableSingleUnit] = []
        self.all_trains_unbreakable_units_by_cc_id: Dict[int, TrainUnbreakableSingleUnit] = {}
        self.all_trains_unbreakable_units_by_emu_id: Dict[int, TrainUnbreakableSingleUnit] = {}
        self.not_found_equipment_names: Set[str] = set()
        self.not_found_equipment_names_and_raw_ip_address: Set[str] = set()
        self.create_train_unbreakable_units()

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
                    self.network_conf_files_defined_equipments_by_id[expected_equipment_name] = equipment
                    equipment.alternative_identifiers.add(expected_equipment_name)

                    return equipment
        return None

    def get_existing_equipment_by_raw_ip_address(self, expected_raw_ip_address: str) -> List["NetworkConfFilesDefinedEquipment"]:
        return (
            self.network_conf_files_defined_equipments_by_raw_ip_addresses[expected_raw_ip_address] if expected_raw_ip_address in self.network_conf_files_defined_equipments_by_raw_ip_addresses else []
        )

    def get_existing_network_conf_file_eqpt_by_name(self, name: str) -> Optional["NetworkConfFilesDefinedEquipment"]:
        if self.is_existing_network_conf_file_eqpt_by_name(name):
            return self.network_conf_files_defined_equipments_by_id[name]
        return None

    def get_or_create_network_conf_file_eqpt_if_not_exist_by_name(self, name: str) -> "NetworkConfFilesDefinedEquipment":
        if self.is_existing_network_conf_file_eqpt_by_name(name):
            return self.network_conf_files_defined_equipments_by_id[name]
        equipment = NetworkConfFilesDefinedEquipment(name=name, library=self)
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

    def create_train_unbreakable_units(self) -> None:
        for i in range(1, NUMBER_OF_TRAINS + 1):
            train_unbreakable_unit = TrainUnbreakableSingleUnit(cc_id=i, emu_id=4000 + i)
            self.all_trains_unbreakable_units.append(train_unbreakable_unit)
            self.all_trains_unbreakable_units_by_cc_id[train_unbreakable_unit.cc_id] = train_unbreakable_unit
            self.all_trains_unbreakable_units_by_emu_id[train_unbreakable_unit.emu_id] = train_unbreakable_unit
