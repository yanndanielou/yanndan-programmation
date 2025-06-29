# -*-coding:Utf-8 -*
import os

from logger import logger_config


def create_folder_if_not_exist(directory_path: str) -> bool:
    if not os.path.exists(directory_path):
        logger_config.print_and_log_info(f"Create folder {directory_path}")
        os.mkdir(directory_path)
        return True
    else:
        logger_config.print_and_log_info(f"Folder {directory_path} already exists")
        return False
