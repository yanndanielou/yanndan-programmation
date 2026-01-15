from typing import Dict

from common import file_utils, json_encoders
from logger import logger_config

from networkflowmatrix import network_conf_files_descriptions_data, network_matrix_data_model, equipments, constants

if __name__ == "__main__":
    with logger_config.application_logger("networkflowmatrix"):
        equipments_library = (
            equipments.NetworkConfFilesEquipmentsLibrary()
            .Builder()
            .add_ihm_programm(excel_file_full_path=network_conf_files_descriptions_data.INPUT_DOWNLOAD_FOLDER + "/" + "S2_P2_02 à 08_Ind14.xlsm")
            .add_manual_entries()
            .add_fdiff_clients(excel_file_full_path=network_conf_files_descriptions_data.INPUT_DOWNLOAD_FOLDER + "/" + "I3G-NEXT-2024-DT-PCM-1103.xlsm")
            .add_network_config_file_with_excel_description(excel_description=network_conf_files_descriptions_data.BordAddressPlanV9Description())
            .add_network_config_file_with_excel_description(excel_description=network_conf_files_descriptions_data.StdRadioNetworkConfV2Description())
            .add_network_config_file_with_excel_description(excel_description=network_conf_files_descriptions_data.SolStdNetworkConfV11Description())
            .add_network_config_file_with_excel_description(excel_description=network_conf_files_descriptions_data.RadioLayoutR841Description())
        ).build()

        with logger_config.stopwatch_with_label("Build matrix", inform_beginning=True, monitor_ram_usage=True):
            network_flow_matrix = network_matrix_data_model.NetworkFlowMatrix.Builder.build_with_excel_file(
                excel_file_full_path="Input_Downloaded/NExTEO-S-271000-02-0125-00_Matrice_de_Flux_V15-03Draft.xlsm", sheet_name="Matrice_de_Flux_SITE"
            )

        network_flow_matrix.match_equipments_with_network_conf_files(equipments_library)

        equipments_library.dump_to_json_file(f"{constants.OUTPUT_PARENT_DIRECTORY_NAME}/all_equipments_in_conf_files_after_matching_network_matrix.json")
        pass
