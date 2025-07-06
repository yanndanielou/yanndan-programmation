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

DML_FILE_DESTINATION_PATH = f"{DEFAULT_DOWNLOAD_DIRECTORY}/DML_NEXTEO_ATS+_V14.xlsm"

DOWNLOADED_FILES_FINAL_DIRECTORY = "Input"
OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME = "output_save_cfx_request_results"



EXCEL_FILE_EXTENSION = ".xlsx"


@contextmanager
def stopwatch_with_label_and_surround_with_screenshots(label: str, remote_web_driver: ChromiumDriver, screenshots_directory_path: str) -> Generator[float, None, None]:
    """Décorateur de contexte pour mesurer le temps d'exécution d'une fonction :
    https://www.docstring.fr/glossaire/with/"""
    remote_web_driver.get_screenshot_as_file(f"{screenshots_directory_path}/before {label}.png")
    debut = time.perf_counter()
    yield time.perf_counter() - debut
    fin = time.perf_counter()
    remote_web_driver.get_screenshot_as_file(f"{screenshots_directory_path}/after {label}.png")

    duree = fin - debut
    to_print_and_log = f"{label} Elapsed: {duree:.2f} seconds"

    log_timestamp = time.asctime(time.localtime(time.time()))

    previous_stack = inspect.stack(0)[2]
    file_name = previous_stack.filename
    line_number = previous_stack.lineno
    calling_file_name_and_line_number = file_name + ":" + str(line_number)

    # pylint: disable=line-too-long
    print(log_timestamp + "\t" + calling_file_name_and_line_number + "\t" + to_print_and_log)

    logging.info(f"{calling_file_name_and_line_number} \t {to_print_and_log}")


@contextmanager
def surround_with_screenshots(label: str, remote_web_driver: ChromiumDriver, screenshots_directory_path: str) -> Generator[float, None, None]:
    remote_web_driver.get_screenshot_as_file(f"{screenshots_directory_path}/before {label}.png")
    yield 0.0
    remote_web_driver.get_screenshot_as_file(f"{screenshots_directory_path}/after {label}.png")


@dataclass
class DownloadAndCleanDMLApplication:
    output_parent_directory_name: str = OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME
    output_downloaded_files_final_directory_path: str = DOWNLOADED_FILES_FINAL_DIRECTORY
    web_browser_download_directory = DEFAULT_DOWNLOAD_DIRECTORY

    driver: ChromiumDriver = field(init=False)

    def __post_init__(self) -> None:
        self.number_of_exceptions_caught = 0

    def run(self) -> None:

        self.create_webdriver()

        download_file_detector = download_utils.DownloadFileDetector(
            directory_path=self.web_browser_download_directory,
            filename_pattern=DML_FILE_DOWNLOADED_PATTERN,
            timeout_in_seconds=1000,
        )
        self.open_dml_url()

        file_downloaded_path: Optional[str] = download_file_detector.monitor_download()
        if not file_downloaded_path:
            logger_config.print_and_log_error(f"No downloaded file found for")
            return

        logger_config.print_and_log_info(f"File downloaded : {file_downloaded_path}")

        logger_config.print_and_log_info(
            f"File downloaded : {file_downloaded_path}, will be moved to {DML_FILE_DESTINATION_PATH}}"
        )
        shutil.move(file_downloaded_path, DML_FILE_DESTINATION_PATH)

    def open_dml_url(self) -> None:
        logger_config.print_and_log_info("login_champfx")

        dml_download_url = "https://rhapsody.siemens.net/livelink/livelink.exe?func=ll&objId=79329709&objAction=Download"

        self.driver.get(dml_download_url)

        time.sleep(0.5)

        wait = WebDriverWait(self.driver, 10)
        more_providers_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, "moreProviders")))
        more_providers_button.click()

        # Wait until the Azure option is visible and then click it
        azure_option = wait.until(expected_conditions.visibility_of_element_located((By.XPATH, "//li[@class='secondary-menu-item authprovider-choice' and @data-authhandler='Azure']")))
        azure_option.click()

    def create_webdriver_firefox(self) -> None:
        self.driver = webdriver.Firefox()

    def create_webdriver_chrome(self) -> None:
        logger_config.print_and_log_info("create_webdriver_chrome")
        # Path to the ChromeDriver
        chrome_driver_path = "C:\\Users\\fr232487\\Downloads\\chromedriver-win64\\chromedriver.exe"

        # Set up the Chrome options
        chrome_options = selenium.webdriver.chrome.options.Options()
        prefs = {
            "download.default_directory": OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME,
            "savefile.default_directory": OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        chrome_options.add_experimental_option("prefs", prefs)

        # Create a new instance of the Chrome self.driver
        driver_service = Service(chrome_driver_path)
        self.driver = webdriver.Chrome(service=driver_service, options=chrome_options)

        self.driver.command_executor.set_timeout(1000)

    def create_webdriver(self) -> None:
        # self.create_webdriver_chrome()
        self.create_webdriver_firefox()


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("DownloadAndCleanDML application"):
        logger_config.configure_logger_with_random_log_file_suffix("DownloadAndCleanDML")

        logger_config.print_and_log_info("Application start")

        application: DownloadAndCleanDMLApplication = DownloadAndCleanDMLApplication()
        application.run()


if __name__ == "__main__":
    main()
