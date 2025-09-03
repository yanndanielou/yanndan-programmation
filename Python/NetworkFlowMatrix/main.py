import random
from typing import Callable, List, cast

from logger import logger_config

from networkflowmatrix import data_model

if __name__ == "__main__":
    with logger_config.application_logger("networkflowmatrix"):

        network_flow_matrix = data_model.NetworkFlowMatrix.Builder.build_with_excel_file(excel_file_full_path="Input/Matrice_next.xlsm", sheet_name="Matrice_de_Flux_SITE")

    logger_config.print_and_log_info(f"all_equipments_names:{data_model.all_equipments_names_with_subsystem}")
