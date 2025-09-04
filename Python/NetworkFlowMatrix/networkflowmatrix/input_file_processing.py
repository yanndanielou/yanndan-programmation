from typing import List, Optional

from networkflowmatrix import data_model
import ipaddress
import pandas

from logger import logger_config


def load_network_flow_matrix_excel_file(excel_file_full_path: str, sheet_name: str = "Matrice_de_Flux_SITE") -> None:
    main_data_frame = pandas.read_excel(excel_file_full_path, skiprows=[0, 1, 2, 3, 4], sheet_name=sheet_name)
    logger_config.print_and_log_info(f"Flow matrix {excel_file_full_path} has {len(main_data_frame)} items")
    logger_config.print_and_log_info(f"Flow matrix {excel_file_full_path} columns  {main_data_frame.columns[:4]} ...")

    network_flow_matrix_lines: List[data_model.NetworkFlowMatrixLine] = []

    for _, row in main_data_frame.iterrows():
        network_flow_matrix_line = data_model.NetworkFlowMatrixLine.Builder.build_with_row(row=row)
        network_flow_matrix_lines.append(network_flow_matrix_line)
