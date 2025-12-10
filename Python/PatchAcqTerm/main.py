import json
from typing import Dict

from common import file_utils, json_encoders
from logger import logger_config

import pandas


OUTPUT_PARENT_DIRECTORY_NAME = "Output"


if __name__ == "__main__":
    with logger_config.application_logger("patchacqterm"):

        with open(file="Input_Downloaded/NEXT_acqTermes.csv", mode=("r"), encoding="ANSI") as input_acq_term_file:
            input_acq_term_file_content = input_acq_term_file
            input_acq_term_file_lines = input_acq_term_file_content.readlines()

        signal_zc_csv_file_path = "Input_Downloaded/SIGNAL_ZC.csv"
        with logger_config.stopwatch_with_label(f"Load {signal_zc_csv_file_path}", monitor_ram_usage=True, inform_beginning=True):
            signal_zc_csv_data_frame = pandas.read_csv(signal_zc_csv_file_path)

        dc_signal_pas_csv_file_path = "Input_Downloaded/dc_signal_pas.csv"
        with logger_config.stopwatch_with_label(f"Load {dc_signal_pas_csv_file_path}", monitor_ram_usage=True, inform_beginning=True):
            dc_signal_pas_data_frame = pandas.read_csv(dc_signal_pas_csv_file_path)

        for input_file_line in input_acq_term_file_lines:
            input_file_line_splitted = input_file_line.split(";")
            term_id = input_file_line_splitted[3]
            assert term_id

            if "RC_SIGNAL_OVERRIDE_STATUS" in term_id:
                signal_number_str = input_file_line_splitted[9]
                signal_number_int = int(signal_number_str)
                logger_config.print_and_log_info(f"{term_id}, current signal number in acq term: {signal_number_int}")
                pass

            if "ST_ANDREWS_CROSS_MAINT_SIGNAL_LIGHT" in term_id:
                signal_number_str = input_file_line_splitted[10]
                signal_number_int = int(signal_number_str)
                logger_config.print_and_log_info(f"{term_id}, current signal number in acq term: {signal_number_int}")
                pass
