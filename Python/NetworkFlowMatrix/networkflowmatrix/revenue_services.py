import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from networkflowmatrix.equipments import NetworkConfFilesDefinedEquipment


@dataclass
class RevenueService:
    name: str

    def __post_init__(self) -> None:
        self._all_network_conf_files_equipments_containing_it: List["NetworkConfFilesDefinedEquipment"] = []

    def add_network_conf_files_equipments_containing_it(self, equipment: "NetworkConfFilesDefinedEquipment") -> None:
        assert equipment not in self._all_network_conf_files_equipments_containing_it
        self._all_network_conf_files_equipments_containing_it.append(equipment)

    @property
    def all_network_conf_files_equipments_containing_it(self) -> List["NetworkConfFilesDefinedEquipment"]:
        return self._all_network_conf_files_equipments_containing_it


ATS1 = RevenueService("ATS1")
ATS2Plus = RevenueService("ATS2+")
ATS2 = RevenueService("ATS2")
ATS3 = RevenueService("ATS3")
TO_BE_DEFINED = RevenueService("TO_BE_DEFINED")
TO_BE_CANCELLED = RevenueService("TO_BE_CANCELLED")

ALL_REVENUES_SERVICES: List[RevenueService] = [ATS1, ATS2, ATS2Plus, ATS3]


class RevenueServiceToEquipmentMatchingStrategy(ABC):

    def get_revenue_service_for_equipment(self, equipment: "NetworkConfFilesDefinedEquipment") -> RevenueService:
        result = self._do_get_revenue_service_for_equipment(equipment)
        result.add_network_conf_files_equipments_containing_it(equipment)
        return result

    @abstractmethod
    def _do_get_revenue_service_for_equipment(self, equipment: "NetworkConfFilesDefinedEquipment") -> RevenueService:
        """This method must be overridden in child classes."""


class DependingOnEquipmentTypeRevenueServiceToEquipmentMatchingStrategy(RevenueServiceToEquipmentMatchingStrategy):

    def _do_get_revenue_service_for_equipment(self, equipment: "NetworkConfFilesDefinedEquipment") -> RevenueService:
        assert equipment.equipment_types, f"Equipment {equipment.name} from source {equipment.source_label} has no type"
        assert len(equipment.equipment_types) > 0, f"Equipment {equipment.name} from source {equipment.source_label} has no type"
        equipment_type = list(equipment.equipment_types)[0]
        match equipment_type.name:
            case "a":
                return None
            case _:
                assert False, f"{inspect.stack(0)[0].function} Type {equipment_type} not handled for equipment {equipment.name} from source {equipment.source_label}"


class DependingOnEquipmentNameRevenueServiceToEquipmentMatchingStrategy(RevenueServiceToEquipmentMatchingStrategy):

    def _do_get_revenue_service_for_equipment(self, equipment: "NetworkConfFilesDefinedEquipment") -> RevenueService:

        match equipment.name:
            case _:
                assert False, f"{inspect.stack(0)[0].function} Name {equipment.name} defined in {equipment.source_label} not handled"


class AlwaysATS1RevenueService(RevenueServiceToEquipmentMatchingStrategy):

    def _do_get_revenue_service_for_equipment(self, equipment: "NetworkConfFilesDefinedEquipment") -> RevenueService:
        return ATS1


class AlwaysATS2RevenueService(RevenueServiceToEquipmentMatchingStrategy):

    def _do_get_revenue_service_for_equipment(self, equipment: "NetworkConfFilesDefinedEquipment") -> RevenueService:
        return ATS2


class AlwaysATS3RevenueService(RevenueServiceToEquipmentMatchingStrategy):

    def _do_get_revenue_service_for_equipment(self, equipment: "NetworkConfFilesDefinedEquipment") -> RevenueService:
        return ATS3
