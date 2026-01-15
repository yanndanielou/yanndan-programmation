from typing import TYPE_CHECKING
from networkflowmatrix.equipments import GroupDefinition

if TYPE_CHECKING:
    from networkflowmatrix.equipments import NetworkConfFilesEquipmentsLibrary


def construct_manual_groups(equipments_library: "NetworkConfFilesEquipmentsLibrary") -> None:
    eqpt_AP_TSW = [equipment for equipment in equipments_library.all_network_conf_files_defined_equipments if "AP_TSW" in equipment.equipment_types]
    group = equipments_library.get_or_create_group(GroupDefinition(name="AP_TSW", subnet_and_mask="10.203.0.0/16"))
    for eqpt in eqpt_AP_TSW:
        equipments_library.get_or_create_group_and_add_equipment(GroupDefinition(name="AP_TSW", subnet_and_mask="10.203.0.0/16"))
