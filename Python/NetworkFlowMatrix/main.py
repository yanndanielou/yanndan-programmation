from logger import logger_config
from common import json_encoders, file_utils


from networkflowmatrix import data_model

OUTPUT_PARENT_DIRECTORY_NAME = "Output"

if __name__ == "__main__":
    with logger_config.application_logger("networkflowmatrix"):

        with logger_config.stopwatch_with_label("Build matrix", inform_beginning=True, monitor_ram_usage=True):
            network_flow_matrix = data_model.NetworkFlowMatrix.Builder.build_with_excel_file(excel_file_full_path="Input/Matrice_next.xlsm", sheet_name="Matrice_de_Flux_SITE")

        for directory_path in [OUTPUT_PARENT_DIRECTORY_NAME]:
            file_utils.create_folder_if_not_exist(directory_path)

        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(
            sorted(data_model.EquipmentInFLoxMatrix.all_instances, key=lambda equipment: equipment.name), f"{OUTPUT_PARENT_DIRECTORY_NAME}/all_equipments_in_flow_matrix.json"
        )
        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(
            sorted(data_model.SubSystemInFlowMatrix.all_instances, key=lambda subsystem: subsystem.name), f"{OUTPUT_PARENT_DIRECTORY_NAME}/all_subsystems_in_flow_matrix.json"
        )
        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(
            data_model.all_equipments_names_with_subsystem, f"{OUTPUT_PARENT_DIRECTORY_NAME}/data_model.all_equipments_names_with_subsystem.json"
        )
