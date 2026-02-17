from logger import logger_config

from networkflowmatrix import equipments, network_conf_files_descriptions_data, network_matrix_data_model, application

if __name__ == "__main__":
    with logger_config.application_logger("networkflowmatrix"):

        with logger_config.stopwatch_with_label("Create network conf files equipments builder", inform_beginning=True, monitor_ram_usage=True):
            equipments_library_builder = (
                equipments.NetworkConfFilesEquipmentsLibrary()
                .Builder()
                .add_ihm_programm(excel_file_full_path=network_conf_files_descriptions_data.INPUT_DOWNLOAD_FOLDER + "/" + "S2_P2_02 à 08_Ind14.xlsm")
                .add_fdiff_clients(excel_file_full_path=network_conf_files_descriptions_data.INPUT_DOWNLOAD_FOLDER + "/" + "I3G-NEXT-2024-DT-PCM-1103.xlsm")
                .add_network_config_file_with_excel_description(excel_description=network_conf_files_descriptions_data.BordAddressPlanV9Description())
                .add_network_config_file_with_excel_description(excel_description=network_conf_files_descriptions_data.StdRadioNetworkConfV2Description())
                .add_network_config_file_with_excel_description(excel_description=network_conf_files_descriptions_data.SolStdNetworkConfV11Description())
                .add_network_config_file_with_excel_description(excel_description=network_conf_files_descriptions_data.RadioLayoutR841Description())
                .add_manual_entries()
            )

        with logger_config.stopwatch_with_label("Create matrix builder", inform_beginning=True, monitor_ram_usage=True):
            network_flow_matrix_builder = network_matrix_data_model.NetworkFlowMatrix.Builder().excel_file(
                excel_file_full_path="Input_Downloaded/NExTEO-S-271000-02-0125-00_Matrice_de_Flux_V15-04.xlsm", sheet_name="Matrice_de_Flux_SITE"
            )

        application.NetworkFlowMatrixApplication(equipments_library_builder=equipments_library_builder, network_flow_matrix_builder=network_flow_matrix_builder)
