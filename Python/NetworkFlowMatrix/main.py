import json
from typing import Dict

from common import file_utils, json_encoders
from logger import logger_config

from networkflowmatrix import network_conf_files, network_conf_files_descriptions_data, network_matrix_data_model, equipments, sith_equipments

OUTPUT_PARENT_DIRECTORY_NAME = "Output"


def subsystem_to_dict(subsystem: network_matrix_data_model.SubSystemInFlowMatrix, with_equipment: bool) -> Dict:
    if with_equipment:
        return {
            "subsystem_name": subsystem.name,
            "subsystem_number_equipments": len(subsystem.all_equipments_detected_in_flow_matrix),
            "subsystem_all_equipments": [equipment_to_dict(eq, False) for eq in subsystem.all_equipments_detected_in_flow_matrix],
        }
    else:
        return {"subsystem_name": subsystem.name}


def equipment_to_dict(equipment: network_matrix_data_model.EquipmentInFLowMatrix, with_subsystem: bool) -> Dict:
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


def dump_matrix_subsystems_to_json(network_flow_matrix_to_dump: network_matrix_data_model.NetworkFlowMatrix, filepath: str) -> None:
    data = [
        subsystem_to_dict(subsystem, with_equipment=True) for subsystem in sorted(network_flow_matrix_to_dump.all_matrix_flow_subsystems_definitions_instances, key=lambda subsystem: subsystem.name)
    ]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def dump_matrix_equipments_to_json(network_flow_matrix_to_dump: network_matrix_data_model.NetworkFlowMatrix, filepath: str) -> None:
    data = [
        equipment_to_dict(equipment, with_subsystem=True) for equipment in sorted(network_flow_matrix_to_dump.all_matrix_flow_equipments_definitions_instances, key=lambda subsystem: subsystem.name)
    ]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    with logger_config.application_logger("networkflowmatrix"):
        equipments_library = equipments.NetworkConfFilesEquipmentsLibrary()

        radio_std_conf_file = network_conf_files.NetworkConfFile.Builder.build_with_excel_description(
            equipments_library=equipments_library, excel_description=network_conf_files_descriptions_data.StdRadioNetworkConfV2Description()
        )

        sol_std_conf_file = network_conf_files.NetworkConfFile.Builder.build_with_excel_description(
            equipments_library=equipments_library, excel_description=network_conf_files_descriptions_data.SolStdNetworkConfV11Description()
        )

        airlink_radio_layout_conf_file = network_conf_files.NetworkConfFile.Builder.build_with_excel_description(
            equipments_library=equipments_library, excel_description=network_conf_files_descriptions_data.RadioLayoutR841Description()
        )

        sith_conf_file = sith_equipments.SithConfFile.Builder.build(equipments_library=equipments_library)

        equipments_library.print_stats()

        with logger_config.stopwatch_with_label("Build matrix", inform_beginning=True, monitor_ram_usage=True):
            network_flow_matrix = network_matrix_data_model.NetworkFlowMatrix.Builder.build_with_excel_file(
                excel_file_full_path="Input_Downloaded/NExTEO-S-271000-02-0125-00_Matrice_de_Flux_V15-01Draft.xlsm", sheet_name="Matrice_de_Flux_SITE"
            )

        network_flow_matrix.match_equipments_with_network_conf_files(equipments_library)

        for directory_path in [OUTPUT_PARENT_DIRECTORY_NAME]:
            file_utils.create_folder_if_not_exist(directory_path)

        dump_matrix_subsystems_to_json(network_flow_matrix, f"{OUTPUT_PARENT_DIRECTORY_NAME}/matrix_all_subsystems_in_flow_matrix.json")
        dump_matrix_equipments_to_json(network_flow_matrix, f"{OUTPUT_PARENT_DIRECTORY_NAME}/matrix_all_equipments_in_flow_matrix.json")

        equipments_library.dump_to_json_file(f"{OUTPUT_PARENT_DIRECTORY_NAME}/all_equipments_in_conf_files.json")

        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(
            network_flow_matrix.all_equipments_names_with_subsystem, f"{OUTPUT_PARENT_DIRECTORY_NAME}/matrix_all_equipments_names_with_subsystem.json"
        )

        network_line = network_flow_matrix.get_line_by_identifier(1970)
        assert network_line
