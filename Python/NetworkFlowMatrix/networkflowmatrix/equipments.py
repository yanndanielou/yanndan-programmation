from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, TYPE_CHECKING

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
    equipment_types: Set[str] = field(default_factory=set)
    alternative_identifiers: Set[str] = field(default_factory=set)
    ip_addresses: List["NetworkConfFilesDefinedIpAddress"] = field(default_factory=list)


class NetworkConfFilesEquipmentsLibrary:
    def __init__(self) -> None:
        self.network_conf_files_defined_equipments: List[NetworkConfFilesDefinedEquipment] = []
        self.network_conf_files_defined_equipments_by_id: Dict[str, NetworkConfFilesDefinedEquipment] = {}
        self.all_trains_unbreakable_units: List[TrainUnbreakableSingleUnit] = []
        self.all_trains_unbreakable_units_by_cc_id: Dict[int, TrainUnbreakableSingleUnit] = {}
        self.all_trains_unbreakable_units_by_emu_id: Dict[int, TrainUnbreakableSingleUnit] = {}
        self.create_train_unbreakable_units()

    def is_existingnetwork_conf_file_eqpt_by_name(self, name: str) -> bool:
        return name in self.network_conf_files_defined_equipments_by_id

    def get_existing_network_conf_file_eqpt_by_name(self, name: str) -> Optional["NetworkConfFilesDefinedEquipment"]:
        if self.is_existingnetwork_conf_file_eqpt_by_name(name):
            return self.network_conf_files_defined_equipments_by_id[name]
        return None

    def get_or_create_network_conf_file_eqpt_if_not_exist_by_name(self, name: str) -> "NetworkConfFilesDefinedEquipment":
        if self.is_existingnetwork_conf_file_eqpt_by_name(name):
            return self.network_conf_files_defined_equipments_by_id[name]
        equipment = NetworkConfFilesDefinedEquipment(name=name)
        self.network_conf_files_defined_equipments_by_id[name] = equipment
        self.network_conf_files_defined_equipments.append(equipment)

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
