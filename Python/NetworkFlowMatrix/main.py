from logger import logger_config
from common import json_encoders, file_utils

from typing import Dict

import json
from networkflowmatrix import data_model, network_conf_files

OUTPUT_PARENT_DIRECTORY_NAME = "Output"


def subsystem_to_dict(subsystem: data_model.SubSystemInFlowMatrix, with_equipment: bool) -> Dict:
    if with_equipment:
        return {
            "subsystem_name": subsystem.name,
            "subsystem_number_equipments": len(subsystem.all_equipments_detected_in_flow_matrix),
            "subsystem_all_equipments": [equipment_to_dict(eq, False) for eq in subsystem.all_equipments_detected_in_flow_matrix],
        }
    else:
        return {"subsystem_name": subsystem.name}


def equipment_to_dict(equipment: data_model.EquipmentInFLowMatrix, with_subsystem: bool) -> Dict:
    if with_subsystem:
        new_var = {
            "equipment_name": equipment.name,
            "equipment_ip_addresses": [str(ip) for ip in equipment.ip_addresses],
            "equipment_number_of_subsystems_detected_in_flow_matrix": len(equipment.all_subsystems_detected_in_flow_matrix),
            "equipment_all_subsystems_detected_in_flow_matrix": [subsystem_to_dict(subsys, False) for subsys in equipment.all_subsystems_detected_in_flow_matrix],
        }
    else:
        new_var = {"equipment_name": equipment.name, "equipment_ip_addresses": [str(ip) for ip in equipment.ip_addresses]}

    return new_var


def dump_subsystems_to_json(network_flow_matrix: data_model.NetworkFlowMatrix, filepath: str) -> None:
    data = [subsystem_to_dict(subsystem, with_equipment=True) for subsystem in sorted(network_flow_matrix.all_matrix_flow_subsystems_definitions_instances, key=lambda subsystem: subsystem.name)]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def dump_equipments_to_json(network_flow_matrix: data_model.NetworkFlowMatrix, filepath: str) -> None:
    data = [equipment_to_dict(equipment, with_subsystem=True) for equipment in sorted(network_flow_matrix.all_matrix_flow_equipments_definitions_instances, key=lambda subsystem: subsystem.name)]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    with logger_config.application_logger("networkflowmatrix"):
        equipments_library = network_conf_files.EquipmentsLibrary()

        radio_std_conf_file = network_conf_files.RadioStdNetworkConfFile.Builder.build_with_excel_file(
            equipments_library=equipments_library, excel_file_full_path="Input_Downloaded/NExTEO-S-273000-02-0125-01 Dossier de Configuration Réseau STD Radio - V02-00 Annexe A_diffa.xlsx"
        )

        sol_std_conf_file = network_conf_files.SolStdNetworkConfFile.Builder.build_with_excel_file(
            equipments_library=equipments_library,
            excel_file_full_path="Input_Downloaded/NExTEO-S-271000-02-0125-02  Dossier de Configuration Réseau Sol - V10-00 Annexe A.xlsb",
            equipment_definition_tabs=network_conf_files.SolStdNetworkConfV10Description().all_tabs_definition,
        )

        logger_config.print_and_log_info(f"After radio_std_conf_file, {len(equipments_library.network_conf_files_defined_equipments)} equipments")

        with logger_config.stopwatch_with_label("Build matrix", inform_beginning=True, monitor_ram_usage=True):
            network_flow_matrix = data_model.NetworkFlowMatrix.Builder.build_with_excel_file(excel_file_full_path="Input/Matrice_next.xlsm", sheet_name="Matrice_de_Flux_SITE")

        for directory_path in [OUTPUT_PARENT_DIRECTORY_NAME]:
            file_utils.create_folder_if_not_exist(directory_path)

        dump_subsystems_to_json(network_flow_matrix, f"{OUTPUT_PARENT_DIRECTORY_NAME}/all_subsystems_in_flow_matrix.json")
        dump_equipments_to_json(network_flow_matrix, f"{OUTPUT_PARENT_DIRECTORY_NAME}/all_equipments_in_flow_matrix.json")

        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(
            network_flow_matrix.all_equipments_names_with_subsystem, f"{OUTPUT_PARENT_DIRECTORY_NAME}/data_model.all_equipments_names_with_subsystem.json"
        )

        network_line = network_flow_matrix.get_line_by_identifier(1970)
        assert network_line
