# Standard

from enum import Enum, auto
import argparse
import fnmatch
import inspect
import logging
import os
import pickle
import queue
import shutil
import threading
import time
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

import openpyxl


import selenium.webdriver.chrome.options
import selenium.webdriver.firefox.options
from common import download_utils, file_utils

# Other libraries
from logger import logger_config

# Third Party
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select, WebDriverWait

DEFAULT_DOWNLOAD_DIRECTORY = os.path.expandvars(r"%userprofile%\downloads")

DML_FILE_DOWNLOADED_PATTERN = "DML_NEXTEO_ATS+_V*.xlsm"

DML_FILE_DESTINATION_PATH = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14.xlsm"

ALLOWED_DML_SHEETS_NAMES = ["Database"]

DOWNLOADED_FILES_FINAL_DIRECTORY = "Input"
OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME = "output_save_cfx_request_results"

EXCEL_FILE_EXTENSION = ".xlsx"


@dataclass
class DownloadAndCleanDMLApplication:
    output_parent_directory_name: str = OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME
    output_downloaded_files_final_directory_path: str = DOWNLOADED_FILES_FINAL_DIRECTORY
    web_browser_download_directory = DEFAULT_DOWNLOAD_DIRECTORY

    def __post_init__(self) -> None:
        self.number_of_exceptions_caught = 0

    def run(self) -> None:

        dml_file_path = self.download_dml_file()
        if dml_file_path:
            self.remove_useless_tabs(dml_file_path)

        pass

    def remove_useless_tabs(self, dml_file_path: str) -> None:
        logger_config.print_and_log_info(f"Open:{dml_file_path}")
        workbook_dml = openpyxl.load_workbook(dml_file_path)
        sheets_names = workbook_dml.sheetnames
        logger_config.print_and_log_info(f"Tabs found: {sheets_names}")
        print(workbook_dml.sheetnames)
        for sheet_name in sheets_names:
            if sheet_name in ALLOWED_DML_SHEETS_NAMES:
                logger_config.print_and_log_info(f"Allowed sheet:{sheet_name}")
            else:
                logger_config.print_and_log_info(f"Removing sheet:{sheet_name}")
                workbook_dml.remove(workbook_dml[sheet_name])
            pass

        logger_config.print_and_log_info(f"Save:{workbook_dml}")
        workbook_dml.save(DML_FILE_DESTINATION_PATH)

    def download_dml_file(self) -> Optional[str]:

        driver: ChromiumDriver = webdriver.Firefox()

        dml_download_url = "https://rhapsody.siemens.net/livelink/livelink.exe?func=ll&objId=79329709&objAction=Download"

        driver.get(dml_download_url)

        time.sleep(0.5)

        wait = WebDriverWait(driver, 10)
        more_providers_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, "moreProviders")))
        more_providers_button.click()

        # Wait until the Azure option is visible and then click it
        azure_option = wait.until(expected_conditions.visibility_of_element_located((By.XPATH, "//li[@class='secondary-menu-item authprovider-choice' and @data-authhandler='Azure']")))

        download_file_detector = download_utils.DownloadFileDetector(
            directory_path=self.web_browser_download_directory,
            filename_pattern=DML_FILE_DOWNLOADED_PATTERN,
            timeout_in_seconds=30,
        )

        azure_option.click()

        file_downloaded_path: Optional[str] = download_file_detector.monitor_download()
        if not file_downloaded_path:
            logger_config.print_and_log_error("No downloaded file found")
            return None

        logger_config.print_and_log_info(f"File downloaded : {file_downloaded_path}, will be moved to {DML_FILE_DESTINATION_PATH}")

        time.sleep(5)

        shutil.move(file_downloaded_path, DML_FILE_DESTINATION_PATH)

        time.sleep(5)

        driver.quit()
        return DML_FILE_DESTINATION_PATH


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("DownloadAndCleanDML application"):
        logger_config.configure_logger_with_random_log_file_suffix("DownloadAndCleanDML")

        logger_config.print_and_log_info("Application start")

        application: DownloadAndCleanDMLApplication = DownloadAndCleanDMLApplication()
        application.run()


if __name__ == "__main__":
    main()
