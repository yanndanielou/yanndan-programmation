# -*-coding:Utf-8 -*
import os

from typing import List, Tuple
import fnmatch

from logger import logger_config


def create_folder_if_not_exist(directory_path: str) -> bool:
    if not os.path.exists(directory_path):
        logger_config.print_and_log_info(f"Create folder {directory_path}")
        os.mkdir(directory_path)
        return True
    else:
        logger_config.print_and_log_info(f"Folder {directory_path} already exists")
        return False


def get_files_by_directory_and_mask(directory_path: str, filename_pattern: str) -> List[str]:
    files_paths: List[str] = []
    for file in os.listdir(directory_path):
        if fnmatch.fnmatch(file, filename_pattern):
            file_path = os.path.join(directory_path, file)
            files_paths.append(file_path)
    return files_paths


def get_files_modification_time(files_paths: List[str]) -> List[Tuple[str, float]]:
    files_and_modified_time: List[Tuple[str, float]] = []
    for file_path in files_paths:
        files_and_modified_time.append((file_path, os.path.getmtime(file_path)))
    return files_and_modified_time
