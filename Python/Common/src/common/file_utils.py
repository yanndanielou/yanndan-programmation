# -*-coding:Utf-8 -*
import fnmatch
import os
import shutil
import tempfile
import time
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from typing import List, Tuple, cast

from logger import logger_config

from common import file_name_utils


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


def create_folder_if_not_exist(directory_path: str) -> bool:
    if not os.path.exists(directory_path):
        logger_config.print_and_log_info(f"Create folder {directory_path}")
        os.mkdir(directory_path)
        return True
    else:
        logger_config.print_and_log_info(f"Folder {directory_path} already exists")
        return False


def get_files_by_directory_and_file_name_mask(directory_path: str, filename_pattern: str) -> List[str]:
    files_paths: List[str] = []
    for file in os.listdir(directory_path):
        if fnmatch.fnmatch(file, filename_pattern):
            file_path = os.path.join(directory_path, file)
            files_paths.append(file_path)
    return files_paths


def get_files_modification_time(files_paths: List[str]) -> List[Tuple[str, datetime]]:
    files_and_modified_time: List[Tuple[str, datetime]] = []
    for file_path in files_paths:
        files_and_modified_time.append((file_path, datetime.fromtimestamp(os.path.getmtime(file_path))))
    return files_and_modified_time


def rename_file_and_wait_if_is_locked(origin_path: str, dest_path: str) -> str:

    success = False
    while not success:
        try:
            return cast(str, shutil.copy(origin_path, dest_path))
        except Exception as e:
            logger_config.print_and_log_exception(e)
            logger_config.print_and_log_error(f"Could not copy to :{dest_path}, must be used")
            time.sleep(1)
    assert False
