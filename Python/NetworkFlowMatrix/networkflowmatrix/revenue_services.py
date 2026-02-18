import inspect

from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from networkflowmatrix.equipments import NetworkConfFilesDefinedEquipment


class RevenueService(Enum):
    ATS1 = auto()
    ATS2 = auto()
    ATS3 = auto()


class RevenueServiceToEquipmentMatchingStrategy(ABC):

    @abstractmethod
    def get_revenue_service_for_equipment(self, equipment: "NetworkConfFilesDefinedEquipment") -> RevenueService:
        """This method must be overridden in child classes."""


class DependingOnEquipmentTypeRevenueServiceToEquipmentMatchingStrategy(RevenueServiceToEquipmentMatchingStrategy):

    def get_revenue_service_for_equipment(self, equipment: "NetworkConfFilesDefinedEquipment") -> RevenueService:
        assert equipment.equipment_types
        assert len(equipment.equipment_types) == 0
        equipment_type = equipment.equipment_types[0]
        match equipment_type:
            case "a":
                return 1
            case _:
                assert False, f"{inspect.stack(0)[0].function} Type {equipment_type} not handled for equipment {equipment.name}"


class DependingOnEquipmentNameRevenueServiceToEquipmentMatchingStrategy(RevenueServiceToEquipmentMatchingStrategy):

    def get_revenue_service_for_equipment(self, equipment: "NetworkConfFilesDefinedEquipment") -> RevenueService:

        match equipment.name:
            case "a":
                return 1
            case _:
                assert False, f"{inspect.stack(0)[0].function} Name {equipment.name} not handled"


class AlwaysATS1RevenueService(RevenueServiceToEquipmentMatchingStrategy):

    def get_revenue_service_for_equipment(self, equipment: "NetworkConfFilesDefinedEquipment") -> RevenueService:
        return RevenueService.ATS1


class AlwaysATS2RevenueService(RevenueServiceToEquipmentMatchingStrategy):

    def get_revenue_service_for_equipment(self, equipment: "NetworkConfFilesDefinedEquipment") -> RevenueService:
        return RevenueService.ATS2


class AlwaysATS3RevenueService(RevenueServiceToEquipmentMatchingStrategy):

    def get_revenue_service_for_equipment(self, equipment: "NetworkConfFilesDefinedEquipment") -> RevenueService:
        return RevenueService.ATS3
