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

import pywintypes


import openpyxl
import xlwings


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
DML_FILE_WITHOUT_USELESS_SHEETS_PATH = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14_without_useless_sheets.xlsm"
DML_FILE_WITHOUT_LINKS = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14_without_links.xlsm"

DML_RAW_DOWNLOADED_FROM_RHAPSODY_FILE_PATH = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14_raw_from_rhapsody.xlsm"
DML_FILE_FINAL_DESTINATION_PATH = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14.xlsm"

ALLOWED_DML_SHEETS_NAMES = ["Database"]
EXCEL_INTERNAL_RESERVED_SHEETS_NAMES = ["Register"]

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

        # self.download_dml_file()
        # self.remove_useless_tabs_with_xlwings(DML_RAW_DOWNLOADED_FROM_RHAPSODY_FILE_PATH)
        self.remove_excel_external_links(DML_FILE_WITHOUT_USELESS_SHEETS_PATH)
        # self.remove_useless_columns(DML_FILE_WITHOUT_USELESS_SHEETS_PATH)

    def remove_useless_tabs_with_xlwings(self, dml_file_path: str) -> None:
        with logger_config.stopwatch_with_label(label=f"Open:{dml_file_path}", inform_beginning=True):
            workbook_dml = xlwings.Book(dml_file_path)

        logger_config.print_and_log_info("set formulas calculations to manual to improve speed")

        workbook_dml.app.calculation = "manual"
        sheets_names = workbook_dml.sheet_names
        logger_config.print_and_log_info(f"{len(sheets_names)} Sheets found: {sheets_names}")

        for sheet_name in sheets_names:
            if sheet_name in ALLOWED_DML_SHEETS_NAMES:
                logger_config.print_and_log_info(f"Allowed sheet:{sheet_name}")
            elif sheet_name in EXCEL_INTERNAL_RESERVED_SHEETS_NAMES:
                logger_config.print_and_log_info(f"ignore Excel internal reserved sheet:{sheet_name}")
            else:
                with logger_config.stopwatch_with_label(label=f"Removing sheet:{sheet_name}", inform_beginning=True):
                    # Accéder à la feuille que l'on veut supprimer
                    sheet_to_remove = xlwings.sheets[sheet_name]
                    # Supprimer la feuille
                    try:
                        sheet_to_remove.delete()
                    except Exception as exc:
                        logger_config.print_and_log_exception(exc)
            pass

        # Enregistrer et fermer le classeur
        workbook_dml.save(path=DML_FILE_WITHOUT_USELESS_SHEETS_PATH)
        workbook_dml.close()

    def remove_excel_external_links(self, dml_file_path: str) -> None:
        with logger_config.stopwatch_with_label(label=f"Open:{dml_file_path}", inform_beginning=True):
            workbook_dml = xlwings.Book(dml_file_path)

        logger_config.print_and_log_info("set formulas calculations to manual to improve speed")

        workbook_dml.app.calculation = "manual"
        external_links_sources = workbook_dml.api.LinkSources()

        logger_config.print_and_log_info(f"{len(external_links_sources)} links found: {external_links_sources}")

        for external_links_source_name in external_links_sources:
            with logger_config.stopwatch_with_label(label=f"Removing link:{external_links_source_name}", inform_beginning=True):
                workbook_dml.api.BreakLink(Name=external_links_source_name, Type=1)  # Type=1 pour les liaisons de type Excel

        # Enregistrer et fermer le classeur
        workbook_dml.save(path=DML_FILE_WITHOUT_LINKS)
        workbook_dml.close()

    def remove_useless_columns(self, dml_file_path: str) -> None:
        with logger_config.stopwatch_with_label(label=f"Open:{dml_file_path}", inform_beginning=True):
            workbook_dml = openpyxl.load_workbook(dml_file_path)

        sheets_names = workbook_dml.sheetnames
        logger_config.print_and_log_info(f"{len(sheets_names)} Sheets found: {sheets_names}")

    def remove_useless_tabs_with_openpyxl(self, dml_file_path: str) -> None:
        logger_config.print_and_log_info(f"Open:{dml_file_path}")
        workbook_dml = openpyxl.load_workbook(dml_file_path)
        sheets_names = workbook_dml.sheetnames
        logger_config.print_and_log_info(f"{len(sheets_names)} Sheets found: {sheets_names}")
        # print(workbook_dml.sheetnames)
        for sheet_name in sheets_names:
            if sheet_name in ALLOWED_DML_SHEETS_NAMES:
                logger_config.print_and_log_info(f"Allowed sheet:{sheet_name}")
            elif sheet_name in EXCEL_INTERNAL_RESERVED_SHEETS_NAMES:
                logger_config.print_and_log_info(f"ignore Excel internal reserved sheet:{sheet_name}")
            else:
                logger_config.print_and_log_info(f"Removing sheet:{sheet_name}")
                workbook_dml.remove(workbook_dml[sheet_name])
            pass

        logger_config.print_and_log_info(f"Save:{workbook_dml}")
        workbook_dml.save(DML_FILE_WITHOUT_USELESS_SHEETS_PATH)

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

        logger_config.print_and_log_info(f"File downloaded : {file_downloaded_path}, will be moved to {DML_RAW_DOWNLOADED_FROM_RHAPSODY_FILE_PATH}")

        time.sleep(5)

        shutil.move(file_downloaded_path, DML_RAW_DOWNLOADED_FROM_RHAPSODY_FILE_PATH)

        time.sleep(5)

        driver.quit()
        return DML_RAW_DOWNLOADED_FROM_RHAPSODY_FILE_PATH


def main() -> None:
    """Main function"""

    with logger_config.application_logger("DownloadAndCleanDML"):

        application: DownloadAndCleanDMLApplication = DownloadAndCleanDMLApplication()
        application.run()


if __name__ == "__main__":
    main()
