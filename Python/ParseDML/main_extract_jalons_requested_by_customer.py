from logger import logger_config
from parsedml import parse_dml
from common import json_encoders
import param

import logging
import math
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, cast, Any
from warnings import deprecated

import pandas
from common import excel_utils, string_utils, file_name_utils
from logger import logger_config

import param

INPUT_EXCEL_FILE = "Input/JALONS SIGNES_NExTEO-021100-01-0012-01 DML_NEXTEO_ATS+_V14_V41-00.xlsm"


class DocLine:
    def __init__(self, code_moe_ged_raw: str, jalons_raw: Any) -> None:
        self.code_ged_moe = code_moe_ged_raw
        self.jalons_raw = jalons_raw


class Jalon:
    def __init__(self, name: str) -> None:
        self.name = name
        self.docs_codes_ged_moe: Set[str] = set()
        logger_config.print_and_log_info(f"Create jalon {self.name}")


def main() -> None:
    all_jalons: List[Jalon] = []

    with logger_config.application_logger("extract_jalons_requested_by_customer"):

        with logger_config.stopwatch_with_label(f"Read excel {INPUT_EXCEL_FILE}", monitor_ram_usage=True, inform_beginning=True):
            main_data_frame: pandas.DataFrame = pandas.read_excel(INPUT_EXCEL_FILE, sheet_name="Database", skiprows=[0])

        with logger_config.stopwatch_with_label(f"Load and parse {len(main_data_frame)} DML lines"):
            for index, (_, row) in enumerate(main_data_frame.iterrows()):
                code_moe_ged_raw = row["Code GED MOE"]
                jalons_raw = row["Jalon fourniture"]

                assert isinstance(code_moe_ged_raw, str)

                doc_line = DocLine(code_moe_ged_raw, jalons_raw)

                if jalons_raw and str(jalons_raw) not in ["nan"]:
                    assert isinstance(jalons_raw, str)
                    jalons_in_current_line = jalons_raw.split("\n")
                    for jalon_name in jalons_in_current_line:
                        if not [jalon_found for jalon_found in all_jalons if jalon_found.name == jalon_name]:
                            jalon = Jalon(jalon_name)

                        else:
                            jalon = [jalon_found for jalon_found in all_jalons if jalon_found.name == jalon_name][0]

                        logger_config.print_and_log_info(f"Add doc {code_moe_ged_raw} to jalon {jalon_name}")


if __name__ == "__main__":
    main()
