from dataclasses import dataclass

from common import file_utils
from logger import logger_config

from networkflowmatrix import constants, equipments, network_matrix_data_model


@dataclass
class NetworkFlowMatrixApplication:
    equipments_library_builder: equipments.NetworkConfFilesEquipmentsLibrary.Builder
    network_flow_matrix_builder: network_matrix_data_model.NetworkFlowMatrix.Builder

    def run(self) -> None:

        file_utils.remove_folder_and_recreate_it_empty(constants.OUTPUT_PARENT_DIRECTORY_NAME)
        with logger_config.stopwatch_with_label("Build equipment library", inform_beginning=True, monitor_ram_usage=True):
            equipments_library = self.equipments_library_builder.build()

        with logger_config.stopwatch_with_label("Build matrix", inform_beginning=True, monitor_ram_usage=True):
            network_flow_matrix = self.network_flow_matrix_builder.build()

        network_flow_matrix.match_equipments_with_network_conf_files(equipments_library)
