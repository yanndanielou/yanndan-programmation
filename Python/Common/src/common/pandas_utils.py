import time
from typing import Optional

import pandas
from logger import logger_config

from common import file_name_utils


def optional_element_as_optional_string(row: pandas.Series, column_name: str) -> Optional[str]:
    raw_value = row[column_name]
    value_as_str = str(raw_value)
    if value_as_str not in ["nan"]:
        return value_as_str
    else:
        return None


def element_as_casted_int(row: pandas.Series, column_name: str) -> int:
    raw_value = row[column_name]
    if isinstance(raw_value, int):
        return raw_value
    else:
        as_int = int(raw_value)
        return as_int


def is_string_element_at_value(row: pandas.Series, column_name: str, tested_value: str) -> bool:
    raw_value = row[column_name]
    if isinstance(raw_value, str):
        return str(raw_value) == tested_value
    return False


def string_element(row: pandas.Series, column_name: str) -> str:
    raw_value = str(row[column_name])
    assert isinstance(raw_value, str)
    return raw_value


def to_excel_wait_if_file_is_locked(data_per_sheet_name: dict[str, pandas.DataFrame], output_excel_file_without_extension: str, suffix_file_name_by_date: bool = False) -> None:
    if suffix_file_name_by_date:
        output_excel_file_without_extension += file_name_utils.get_file_suffix_with_current_datetime(include_underscore=True)

    output_excel_file_without_extension += ".xlsx"

    # Save DataFrame to Excel
    success = False
    while success is False:
        try:
            with pandas.ExcelWriter(output_excel_file_without_extension) as writer:
                for sheet_name, data_frame in data_per_sheet_name.items():
                    data_frame.to_excel(writer, sheet_name=sheet_name)
                success = True
                return

        except PermissionError:
            logger_config.print_and_log_error(f"File {output_excel_file_without_extension} is used. Release it")
            time.sleep(1)
