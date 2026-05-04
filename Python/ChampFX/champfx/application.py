# Standard

import inspect
import logging
import os
import threading
import time
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Set

# Current program
import connexion_param
from common import download_utils, file_utils, web_driver_utils

# Other libraries
from logger import logger_config

# Third Party
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

CFX_FILES_DOWNLOADED_PATTERN_WITHOUT_EXTENSION = "QueryResult*"

DOWNLOADED_FILES_FINAL_DIRECTORY = "Input_Downloaded"
OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME = "output_save_cfx_request_results"
DEFAULT_DOWNLOAD_DIRECTORY = os.path.expandvars(r"%userprofile%\downloads")


EXCEL_FILE_EXTENSION = ".xlsx"
TEXT_FILE_EXTENSION = ".txt"


class QueryOutputFileType(Enum):
    EXCEL_EXPORT = auto()
    TXT_EXPORT = auto()

    def get_file_extension(self) -> str:
        return TEXT_FILE_EXTENSION if self == QueryOutputFileType.TXT_EXPORT else EXCEL_FILE_EXTENSION

    def get_file_download_dropdown_menu_option_text_french(self) -> str:
        return "Exporter vers un fichier texte" if self == QueryOutputFileType.TXT_EXPORT else "Exporter vers un tableur Excel"

    def get_file_download_dropdown_menu_option_text_english(self) -> str:
        return "Export to a Text File" if self == QueryOutputFileType.TXT_EXPORT else "Export to an Excel Spreadsheet"


@contextmanager
def stopwatch_with_label_and_surround_with_screenshots(label: str, remote_web_driver: ChromiumDriver, screenshots_directory_path: str) -> Generator[float, None, None]:
    """Décorateur de contexte pour mesurer le temps d'exécution d'une fonction :
    https://www.docstring.fr/glossaire/with/"""
    remote_web_driver.get_screenshot_as_file(f"{screenshots_directory_path}/before {label}.png")

    previous_stack = inspect.stack(0)[2]
    file_name = previous_stack.filename
    line_number = previous_stack.lineno
    calling_file_name_and_line_number = file_name + ":" + str(line_number)

    to_print_and_log = f"{label} begin"
    # pylint: disable=line-too-long
    log_timestamp = time.asctime(time.localtime(time.time()))

    print(log_timestamp + "\t" + calling_file_name_and_line_number + "\t" + to_print_and_log)
    logging.info(f"{calling_file_name_and_line_number} \t {to_print_and_log}")  # pylint: disable=logging-fstring-interpolation

    debut = time.perf_counter()
    yield time.perf_counter() - debut
    fin = time.perf_counter()
    remote_web_driver.get_screenshot_as_file(f"{screenshots_directory_path}/after {label}.png")

    duree = fin - debut
    to_print_and_log = f"{label} Elapsed: {duree:.2f} seconds"

    log_timestamp = time.asctime(time.localtime(time.time()))

    # pylint: disable=line-too-long
    print(log_timestamp + "\t" + calling_file_name_and_line_number + "\t" + to_print_and_log)

    logging.info(f"{calling_file_name_and_line_number} \t {to_print_and_log}")  # pylint: disable=logging-fstring-interpolation


@contextmanager
def surround_with_screenshots(label: str, remote_web_driver: ChromiumDriver, screenshots_directory_path: str) -> Generator[float, None, None]:
    remote_web_driver.get_screenshot_as_file(f"{screenshots_directory_path}/before {label}.png")
    yield 0.0
    remote_web_driver.get_screenshot_as_file(f"{screenshots_directory_path}/after {label}.png")


@dataclass
class ChampFxApplication:
    output_parent_directory_name: str = OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME
    errors_output_sub_directory_name = "errors"
    screenshots_output_sub_directory_name = "screenshots"
    driver: ChromiumDriver = field(init=False)

    def __post_init__(self) -> None:
        self.lock = threading.Lock()
        self.errors_output_relative_path = f"{self.output_parent_directory_name}/{self.errors_output_sub_directory_name}"
        self.screenshots_output_relative_path = f"{self.output_parent_directory_name}/{self.screenshots_output_sub_directory_name}"
        self.number_of_exceptions_caught = 0

    @contextmanager
    def stopwatch_with_label_and_surround_with_screenshots(self, label: str) -> Generator[float, None, None]:
        """Décorateur de contexte pour mesurer le temps d'exécution d'une fonction :
        https://www.docstring.fr/glossaire/with/"""
        self.driver.get_screenshot_as_file(f"{self.screenshots_output_relative_path}/before {label}.png")
        debut = time.perf_counter()
        yield time.perf_counter() - debut
        fin = time.perf_counter()
        self.driver.get_screenshot_as_file(f"{self.screenshots_output_relative_path}/after {label}.png")

        duree = fin - debut
        to_print_and_log = f"{label} Elapsed: {duree:.2f} seconds"

        log_timestamp = time.asctime(time.localtime(time.time()))

        previous_stack = inspect.stack(0)[2]
        file_name = previous_stack.filename
        line_number = previous_stack.lineno
        calling_file_name_and_line_number = file_name + ":" + str(line_number)

        # pylint: disable=line-too-long
        print(log_timestamp + "\t" + calling_file_name_and_line_number + "\t" + to_print_and_log)

        logging.info(f"{calling_file_name_and_line_number} \t {to_print_and_log}")  # pylint: disable=logging-fstring-interpolation

    def create_webdriver_chrome(self) -> None:
        self.driver = web_driver_utils.create_webdriver_chrome(
            browser_visibility_type=web_driver_utils.BrowserVisibilityType.NOT_VISIBLE_AKA_HEADLESS, download_directory_path=DEFAULT_DOWNLOAD_DIRECTORY, global_timeout_in_seconds=1000
        )

    def create_webdriver_firefox(self) -> None:
        self.driver = web_driver_utils.create_webdriver_firefox(browser_visibility_type=web_driver_utils.BrowserVisibilityType.NOT_VISIBLE_AKA_HEADLESS)

    def create_webdriver_and_login(self) -> None:
        # Use Chrome by default, switch to Firefox if you want
        # self.create_webdriver_chrome()
        self.create_webdriver_firefox()
        self.login_champfx()

    def reset_driver(self) -> None:
        self.driver.quit()
        self.create_webdriver_and_login()

    def login_champfx(self) -> None:
        logger_config.print_and_log_info("login_champfx")

        login_url = f"https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX?format=HTML&loginId={connexion_param.champfx_login}&password={connexion_param.champfx_password}"

        with stopwatch_with_label_and_surround_with_screenshots(
            label=f"Driver get login url {login_url}", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path
        ):
            self.driver.get(login_url)

        with stopwatch_with_label_and_surround_with_screenshots(label="Waited page is loaded", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
            with surround_with_screenshots(label="login_champfx - title_contains ok", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
                WebDriverWait(self.driver, 100).until(expected_conditions.title_contains("01_CHAMP/CFX - IBM Rational ClearQuest"))

            with surround_with_screenshots(label="login_champfx - document.readyState complete", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
                WebDriverWait(self.driver, 40).until(lambda driver: self.driver.execute_script("return document.readyState") == "complete")
            try:
                with surround_with_screenshots(
                    label="login_champfx - text_to_be_present_in_element welcomeMsg", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path
                ):
                    WebDriverWait(self.driver, 100).until(expected_conditions.text_to_be_present_in_element((By.ID, "welcomeMsg"), "AD001\\fr232487"))
            except TimeoutException as e:
                logger_config.print_and_log_exception(e)

        with stopwatch_with_label_and_surround_with_screenshots(
            label="login_champfx - Additional waiting time", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path
        ):
            time.sleep(0.5)

    def open_request_url(self, request_full_path: int) -> None:
        request_url = f"https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/QUERY/{request_full_path}?format=HTML&loginId={connexion_param.champfx_login}&password={connexion_param.champfx_password}&noframes=true"

        with stopwatch_with_label_and_surround_with_screenshots(label=f"Driver get url {request_url}", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
            self.driver.get(request_url)

        with stopwatch_with_label_and_surround_with_screenshots(label="Waited Title is now good", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
            WebDriverWait(self.driver, 10).until(expected_conditions.title_contains("01_CHAMP/CFX - IBM Rational ClearQuest"))

        with stopwatch_with_label_and_surround_with_screenshots(
            label="Wait for the page to be fully loaded (JavaScript):: document.readyState now good", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path
        ):
            WebDriverWait(self.driver, 10).until(lambda driver: self.driver.execute_script("return document.readyState") == "complete")  # mypy: disable=disallow-untyped-calls

        with stopwatch_with_label_and_surround_with_screenshots(label="Additional waiting time", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
            time.sleep(0.8)
