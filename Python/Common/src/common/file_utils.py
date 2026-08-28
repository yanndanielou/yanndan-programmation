# -*-coding:Utf-8 -*
import fnmatch
import os
import shutil
import tempfile
import time
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from typing import List, Tuple, cast

import natsort
from logger import logger_config

from common import file_name_utils


class FileSortOrder(Enum):
    ALPHABETICAL = "alphabetical"
    TIMESTAMP_OLDER_TO_NEWER = "timestamp_older_to_newer"
    NO_SORTING = "timestamp"


def get_temporary_copy_of_file(input_file_full_path: str) -> Tuple[str, str]:
    temp_dir_path = tempfile.mkdtemp()
    logger_config.print_and_log_info(f"temporary_copy_of_file, created temp_dir:{temp_dir_path}")
    input_file_name = file_name_utils.get_file_name_with_extension_from_full_path(input_file_full_path)
    temp_file_copy_path = os.path.join(temp_dir_path, input_file_name)
    logger_config.print_and_log_info(f"temporary_copy_of_file, temp copy of file created:{temp_file_copy_path}")
    shutil.copyfile(input_file_full_path, temp_file_copy_path)
    return temp_dir_path, temp_file_copy_path


@contextmanager
def temporary_copy_of_file(input_file_full_path: str) -> Generator[str, None, None]:
    temp_dir_path, temp_file_copy_path = get_temporary_copy_of_file(input_file_full_path)
    yield temp_file_copy_path

    logger_config.print_and_log_info(f"temporary_copy_of_file, remove (rmtree):{temp_dir_path}")
    shutil.rmtree(temp_dir_path)


def remove_folder_and_recreate_it_empty(directory_path: str) -> bool:
    remove_folder_even_if_not_empty(directory_path)
    return create_folder_if_not_exist(directory_path)


def remove_folder_even_if_not_empty(directory_path: str) -> bool:
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)
        return True
    else:
        logger_config.print_and_log_info(f"Folder {directory_path} did not exist")
        return False


def create_folder_if_not_exist(directory_path: str) -> bool:
    if not os.path.exists(directory_path):
        logger_config.print_and_log_info(f"Create folder {directory_path}")
        os.mkdir(directory_path)
        return True
    else:
        logger_config.print_and_log_info(f"Folder {directory_path} already exists")
        return False


def open_text_file_and_get_read_lines(file_full_path: str) -> list[str] | None:
    try:
        with open(file_full_path, "r", encoding="utf-8", errors="strict") as f:
            return f.readlines()
    except (UnicodeDecodeError, ValueError):
        with open(file_full_path, "r", encoding="ansi", errors="strict") as f:
            return f.readlines()

    return None


def get_files_by_directory_and_file_name_mask(
    directory_path: str,
    filename_pattern: str = "*",
    file_sort_order: FileSortOrder = FileSortOrder.NO_SORTING,
) -> List[str]:
    files_paths: List[str] = []
    for file in os.listdir(directory_path):
        if fnmatch.fnmatch(file, filename_pattern):
            file_path = os.path.join(directory_path, file)
            files_paths.append(file_path)

    if file_sort_order == FileSortOrder.ALPHABETICAL:
        return natsort.natsorted(files_paths)
    elif file_sort_order == FileSortOrder.TIMESTAMP_OLDER_TO_NEWER:
        return sorted(files_paths, key=os.path.getmtime)
    else:
        return files_paths


def get_files_modification_time(files_paths: List[str]) -> List[Tuple[str, datetime]]:
    files_and_modified_time: List[Tuple[str, datetime]] = []
    for file_path in files_paths:
        files_and_modified_time.append((file_path, datetime.fromtimestamp(os.path.getmtime(file_path))))
    return files_and_modified_time


def rename_file_and_wait_if_is_locked(origin_path: str, dest_path: str, constant_retry_interval: bool = True, max_number_of_retry: int | None = None, additional_label: str = "") -> str:

    move_success = False
    number_of_retried_performed = 0
    while not move_success and (max_number_of_retry is None or max_number_of_retry > number_of_retried_performed):
        try:
            shutil.move(origin_path, dest_path)
            logger_config.print_and_log_info(f"{origin_path} moved to {dest_path}")
            move_success = True
            return dest_path
        except PermissionError:
            # logger_config.print_and_log_exception(permErr)
            logger_config.print_and_log_error(f"{additional_label}File {origin_path} is used. Release it. Will wait {number_of_retried_performed} seconds")
            number_of_retried_performed += 1
            if constant_retry_interval:
                time.sleep(1)
            else:
                time.sleep(number_of_retried_performed)
    assert False
