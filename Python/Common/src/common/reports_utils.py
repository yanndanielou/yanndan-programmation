import csv
import inspect
import textwrap
import time
from datetime import datetime
from typing import Any, Dict, List

import pandas
from logger import logger_config
from openpyxl import Workbook

from common import file_name_utils, file_utils, json_encoders

EXCEL_LIMIT_NUMBER_OF_LINES = 1000000


def _normalize_table_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, bytes, bytearray, int, float, bool, datetime)):
        return value
    if isinstance(value, (list, tuple, set)):
        return ", ".join(map(str, value))
    return str(value)


def _get_fieldnames(rows_as_list_dict: List[Dict[str, Any]]) -> List[str]:
    fieldnames: List[str] = []
    seen_fields: set[str] = set()
    for row in rows_as_list_dict:
        for field_name in row.keys():
            if field_name not in seen_fields:
                seen_fields.add(field_name)
                fieldnames.append(field_name)
    return fieldnames


def _write_delimited_file_improved(rows_as_list_dict: List[Dict[str, Any]], output_file_full_path: str, delimiter: str) -> None:
    with open(output_file_full_path, "w", newline="", encoding="utf-8") as output_file:
        if not rows_as_list_dict:
            return

        fieldnames = _get_fieldnames(rows_as_list_dict)
        writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()

        for row in rows_as_list_dict:
            writer.writerow({field: _normalize_table_value(row.get(field)) for field in fieldnames})


def _write_xlsx_file_improved(rows_as_list_dict: List[Dict[str, Any]], xlsx_file_full_path: str) -> None:
    workbook = Workbook(write_only=True)
    worksheet = workbook.active

    if rows_as_list_dict:
        fieldnames = _get_fieldnames(rows_as_list_dict)
        worksheet.append(fieldnames)

        for row in rows_as_list_dict:
            worksheet.append([_normalize_table_value(row.get(field)) for field in fieldnames])

    workbook.save(xlsx_file_full_path)
    workbook.close()


def save_rows_to_output_files(rows_as_list_dict: List[Dict[str, Any]], file_base_name: str, output_directory_path: str, suffix_file_name_by_date: bool = False) -> bool:
    if suffix_file_name_by_date:
        file_base_name += file_name_utils.get_file_suffix_with_current_datetime(include_underscore=True)

    with logger_config.stopwatch_with_label(f"{inspect.stack(0)[0].function} for {len(rows_as_list_dict)} lines to {file_base_name}", inform_beginning=True):
        file_utils.create_folder_if_not_exist(output_directory_path)
        file_path_without_suffix = f"{output_directory_path}/{file_base_name}"
        try:
            json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(rows_as_list_dict, f"{file_path_without_suffix}.json")
        except MemoryError as err:
            logger_config.print_and_log_exception(err)
        success = False
        while not success:
            try:
                if len(rows_as_list_dict) < EXCEL_LIMIT_NUMBER_OF_LINES:
                    pandas.DataFrame(rows_as_list_dict).to_excel(f"{file_path_without_suffix}.xlsx", index=False)
                pandas.DataFrame(rows_as_list_dict).to_csv(f"{file_path_without_suffix}.csv", index=False)
                pandas.DataFrame(rows_as_list_dict).to_csv(f"{file_path_without_suffix}.txt", index=False, sep="\t")
                # _write_xlsx_file(rows_as_list_dict, f"{file_path_without_suffix}.xlsx")
                # _write_delimited_file(rows_as_list_dict, f"{file_path_without_suffix}.csv", delimiter=",")
                # _write_delimited_file(rows_as_list_dict, f"{file_path_without_suffix}.txt", delimiter="\t")
                success = True
            except PermissionError:
                logger_config.print_and_log_error(f"One of the files {file_path_without_suffix} is used. Release it")
                time.sleep(1)
        return success
