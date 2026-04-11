import inspect
import time
from typing import Any, Dict, List

import pandas
from logger import logger_config

from common import file_utils, json_encoders, file_name_utils


def save_rows_to_output_files(rows_as_list_dict: List[Dict[str, Any]], file_base_name: str, output_directory_path: str, suffix_file_name_by_date: bool = False) -> bool:
    if suffix_file_name_by_date:
        file_base_name += file_name_utils.get_file_suffix_with_current_datetime(include_underscore=True)

    with logger_config.stopwatch_with_label(f"{inspect.stack(0)[0].function} for {len(rows_as_list_dict)} lines to {file_base_name}", inform_beginning=True):
        file_utils.create_folder_if_not_exist(output_directory_path)
        file_path_without_suffix = f"{output_directory_path}/{file_base_name}"
        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(rows_as_list_dict, f"{file_path_without_suffix}.json")
        success = False
        while not success:
            try:
                pandas.DataFrame(rows_as_list_dict).to_excel(f"{file_path_without_suffix}.xlsx", index=False)
                pandas.DataFrame(rows_as_list_dict).to_csv(f"{file_path_without_suffix}.csv", index=False)
                pandas.DataFrame(rows_as_list_dict).to_csv(f"{file_path_without_suffix}.txt", index=False, sep="\t")
                success = True
            except PermissionError:
                logger_config.print_and_log_error(f"One of the files {file_path_without_suffix} is used. Release it")
                time.sleep(1)
        return success
