from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

from logger import logger_config

if TYPE_CHECKING:
    from networkflowmatrix.equipments import NetworkConfFilesDefinedEquipment


@dataclass
class GroupDefinition:
    name: str
    subnet_and_mask: str


@dataclass
class Group:
    definition: GroupDefinition
    equipments: List["NetworkConfFilesDefinedEquipment"] = field(default_factory=list)

    def add_equipment(self, equipment: "NetworkConfFilesDefinedEquipment") -> None:
        if self not in equipment.groups:
            equipment.groups.append(self)
            self.equipments.append(equipment)
        else:
            logger_config.print_and_log_warning(f"Group {self.definition} already in {equipment.name}")
