import random
from typing import Callable, List, cast

from logger import logger_config

from networkflowmatrix import input_file_processing

if __name__ == "__main__":
    with logger_config.application_logger("networkflowmatrix"):

        input_file_processing.load_network_flow_matrix_excel_file("Input/Matrice_next.xlsm")
