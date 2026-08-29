import pandas
import time
from typing import Optional
from logger import logger_config


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


def to_excel_wait_if_file_is_locked(sheet_name: str, output_excel_file: str, data_for_excel: pandas.DataFrame) -> None:
    # Save DataFrame to Excel
    success = False
    while success is False:
        try:
            with pandas.ExcelWriter(output_excel_file) as writer:
                data_for_excel.to_excel(writer, sheet_name="CFX State Counts")
                success = True
                return

        except PermissionError:
            logger_config.print_and_log_error(f"File {output_excel_file} is used. Release it")
            time.sleep(1)
