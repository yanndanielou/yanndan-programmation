# Standard
import argparse
import fnmatch
import inspect
import os
import pickle
import queue
import threading
import time
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from selenium.webdriver.common.by import By

import selenium.webdriver.chrome.options
import selenium.webdriver.firefox.options
from common import download_utils, file_utils

import shutil

import logging

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

# Current programm
import connexion_param

CFX_EXCEL_FILES_DOWNLOADED_PATTERN = "QueryResult*.xlsx"

DOWNLOADED_FILES_FINAL_DIRECTORY = "Input"
OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME = "output_save_cfx_request_results"

DEFAULT_DOWNLOAD_DIRECTORY = os.path.expandvars(r"%userprofile%\downloads")

CREATE_PARSED_EXTENDED_HISTORY_FILES = False

CREATE_PARSED_CURRENT_OWNNER_MODIFICATIONS_JSON_FILES = False

DEFAULT_DO_NOT_OPEN_WEBSITE_AND_TREAT_PREVIOUS_RESULTS = False
# DEFAULT_DO_NOT_OPEN_WEBSITE_AND_TREAT_PREVIOUS_RESULTS = True

DEFAULT_NUMBER_OF_THREADS = 2

BIGGEST_PROJECTS_NAMES: List[str] = [
    "SA_RMP_COM",
    "SA_RMP_REL",
    "ESBO",
    "SA_RMP_SIG_Site",
    "TrashCan",
    "DK_S-bane",
    "Cargo",
    "Sicas Tools",
    "Op_LT_D_901",
    "Simis_Basis",
    "OC501",
    "OC100",
    "ESF",
    "TGMT R3",
    "AU_BHPBIO",
    "GB_Crossrail_CRL",
    "Simis_W_Basis",
    "TGMT R1",
    "BE_ETCS_L2_IXL_RO",
    "LZB80E - LZB-STM",
    "EPOS",
    "Entegro",
    "Controlguide",
    "ATSP",
    "FI_ESKO",
    "US_NYCT_CBTC-Queens-Blvd_61OP-00025",
    "NL_EBS_PLUS",
    "TGMT R2",
    "PTC_OBU",
    "FR_CS_Op_and_Maint",
    "ML_Projektierungstools",
    "ES_AVE_S10x",
    "LT_Siauliai_Klaipeda",
    "HK_Signalling_SCL",
    "BE_ETCS_L2_IXL",
    "TCR3_CBTC",
    "CH_CHP_ETCS",
    "GCP5000",
    "FR_PAR4",
    "US_PATH_CBTC-Phase2-STS-F_61OP-70051",
    "iVIU_PTC_Console",
    "MY_KVLRT3-SIG",
    "LZB8016",
    "SA_RMP_CIS",
    "SA_RMP_SIG",
    "FR_PL14",
    "NO_NOR_TRA",
    "Stage",
    "SA_RMP_PSD",
    "STAC",
    "Engineering_Tools",
    "BAI",
    "DE_FPTS",
    "Simis_W_Logic_International",
    "IN_CMRP1",
    "FR_NEXTEO",
]


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
class SaveCfxRequestMultipagesResultsApplication:
    output_parent_directory_name: str = OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME
    output_downloaded_files_final_directory_path: str = DOWNLOADED_FILES_FINAL_DIRECTORY
    web_browser_download_directory = DEFAULT_DOWNLOAD_DIRECTORY

    errors_output_sub_directory_name = "errors"
    screenshots_output_sub_directory_name = "screenshots"
    driver: ChromiumDriver = field(init=False)

    def __post_init__(self) -> None:
        self.lock = threading.Lock()
        self.errors_output_relative_path = f"{self.output_parent_directory_name}/{self.errors_output_sub_directory_name}"
        self.screenshots_output_relative_path = f"{self.output_parent_directory_name}/{self.screenshots_output_sub_directory_name}"

    def run(self) -> None:

        for directory_path in [self.output_parent_directory_name, self.errors_output_relative_path, self.screenshots_output_relative_path, self.output_downloaded_files_final_directory_path]:
            file_utils.create_folder_if_not_exist(directory_path)

        self.create_webdriver_and_login()

        self.generate_and_dowload_states_changes_query_for_all_projects_except(projects_names_to_exclude=BIGGEST_PROJECTS_NAMES)

        number_of_exceptions_caught: int = 0
        for project_name in BIGGEST_PROJECTS_NAMES:
            logger_config.print_and_log_info(f"Handling project {project_name}")
            try:
                with logger_config.stopwatch_with_label(f"generate_and_dowload_query_for_project:{project_name}"):
                    self.generate_and_dowload_states_change_query_for_project(project_name=project_name)
            except Exception as e:
                number_of_exceptions_caught += 1
                logger_config.print_and_log_exception(e)
                self.driver.get_screenshot_as_file(f"{self.screenshots_output_sub_directory_name}/{project_name} {number_of_exceptions_caught} th Exception caught.png")
                with logger_config.stopwatch_with_label(f"reset_driver :{project_name}"):
                    self.reset_driver()
                with logger_config.stopwatch_with_label(f"generate_and_dowload_query_for_project:{project_name}"):
                    self.generate_and_dowload_states_change_query_for_project(project_name=project_name)

        time.sleep(1000)

    def generate_and_dowload_states_changes_query_for_all_projects_except(self, projects_names_to_exclude: List[str]) -> None:
        project_manual_selection_change_state_query = "66875867"
        self.open_request_url(project_manual_selection_change_state_query)

        with stopwatch_with_label_and_surround_with_screenshots(
            label="generate_and_dowload_query_for_all_projects_except element_to_be_clickable Sélectionner",
            remote_web_driver=self.driver,
            screenshots_directory_path=self.screenshots_output_relative_path,
        ):
            selectionner_button_container_node = WebDriverWait(self.driver, 100).until(
                expected_conditions.element_to_be_clickable((By.XPATH, "//span[@data-dojo-attach-point='containerNode' and text()='Sélectionner']"))
            )
        selectionner_button_container_node.click()

        add_all_button = WebDriverWait(self.driver, 100).until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'button[dojoattachpoint="addAllBtn"]')))
        add_all_button.click()

        for project_name_to_exclude in projects_names_to_exclude:
            project_selection_element = self.driver.find_element(By.XPATH, f"//select[@id='cq_widget_CqDoubleListBox_0_valueList']//option[text()='{project_name_to_exclude}']")
            actions = ActionChains(self.driver)
            with stopwatch_with_label_and_surround_with_screenshots(
                label="generate_and_dowload_query_for_all_projects_except project_selection_element double_click",
                remote_web_driver=self.driver,
                screenshots_directory_path=self.screenshots_output_relative_path,
            ):
                actions.double_click(project_selection_element).perform()

        ok_button = self.driver.find_element(By.XPATH, "//span[@class='dijitReset dijitInline dijitButtonText' and text()='OK']")
        ok_button.click()

        with stopwatch_with_label_and_surround_with_screenshots(
            label="generate_and_dowload_query_for_all_projects_except Exécuter la requête", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path
        ):
            executer_requete_button = self.driver.find_element(By.XPATH, "//span[@class='dijitReset dijitInline dijitButtonText' and text()='Exécuter la requête']")
            executer_requete_button.click()

        with stopwatch_with_label_and_surround_with_screenshots(
            label="generate_and_dowload_query_for_all_projects_except - wait table result",
            remote_web_driver=self.driver,
            screenshots_directory_path=self.screenshots_output_relative_path,
        ):
            WebDriverWait(self.driver, 1000).until(expected_conditions.presence_of_element_located((By.ID, "unique_info_col")))

        with stopwatch_with_label_and_surround_with_screenshots(
            label="generate_and_dowload_query_for_all_projects_except - wait column CFXID",
            remote_web_driver=self.driver,
            screenshots_directory_path=self.screenshots_output_relative_path,
        ):
            WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "//th/div[text()='CFXID']")))

        with stopwatch_with_label_and_surround_with_screenshots(
            label="generate_and_dowload_query_for_all_projects_except - request execution additional waiting time",
            remote_web_driver=self.driver,
            screenshots_directory_path=self.screenshots_output_relative_path,
        ):
            with logger_config.stopwatch_with_label(label="generate_and_dowload_query_for_all_projects_except request execution additional waiting time", enabled=True):
                time.sleep(10)

        with stopwatch_with_label_and_surround_with_screenshots(
            label="generate_and_dowload_query_for_all_projects_except locate_save_excel_click_it", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path
        ):
            self.dowload_states_changes_excel_file_query("Other_projects")

    def generate_and_dowload_states_change_query_for_project(self, project_name: str) -> None:
        project_manual_selection_change_state_query = "66875867"
        self.open_request_url(project_manual_selection_change_state_query)

        with surround_with_screenshots(label=f"{project_name} element_to_be_clickable Sélectionner", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
            selectionner_button_container_node = WebDriverWait(self.driver, 100).until(
                expected_conditions.element_to_be_clickable((By.XPATH, "//span[@data-dojo-attach-point='containerNode' and text()='Sélectionner']"))
            )
        selectionner_button_container_node.click()

        project_option_element = self.driver.find_element(By.XPATH, f"//select[@id='cq_widget_CqDoubleListBox_0_choiceList']//option[text()='{project_name}']")
        actions = ActionChains(self.driver)
        with surround_with_screenshots(label=f"{project_name} project_option_element double_click", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
            actions.double_click(project_option_element).perform()

        ok_button = self.driver.find_element(By.XPATH, "//span[@class='dijitReset dijitInline dijitButtonText' and text()='OK']")
        ok_button.click()

        with surround_with_screenshots(label=f"{project_name} Exécuter la requête", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
            executer_requete_button = self.driver.find_element(By.XPATH, "//span[@class='dijitReset dijitInline dijitButtonText' and text()='Exécuter la requête']")
            executer_requete_button.click()

        with surround_with_screenshots(
            label=f"{project_name} - request execution additional waiting time", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path
        ):
            with logger_config.stopwatch_with_label(label=f"{project_name} request execution additional waiting time", enabled=True):
                time.sleep(10)

        with surround_with_screenshots(label=f"{project_name} locate_save_excel_click_it", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
            with logger_config.stopwatch_with_label(label=f"{project_name} locate_save_excel_click_it", enabled=True):
                self.dowload_states_changes_excel_file_query(project_name)

    def download_excel_file_query(self, label: str, file_to_create_path: str) -> bool:

        with surround_with_screenshots(label=f"{label} arrow_to_acces_export element_to_be_clickable", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
            arrow_to_acces_export = WebDriverWait(self.driver, 100).until(expected_conditions.element_to_be_clickable((By.ID, "dijit_form_ComboButton_1_arrow")))

        with surround_with_screenshots(label=f"{label} arrow_to_acces_export click", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
            arrow_to_acces_export.click()

        export_button = self.driver.find_element(By.XPATH, "//td[contains(text(),'Exporter vers un tableur Excel')]")

        download_file_detector = download_utils.DownloadFileDetector(directory_path=self.web_browser_download_directory, filename_pattern=CFX_EXCEL_FILES_DOWNLOADED_PATTERN)
        export_button.click()

        file_downloaded_path: Optional[str] = download_file_detector.monitor_download()
        if not file_downloaded_path:
            logger_config.print_and_log_error(f"No downloaded file found for {label}")
            return False

        logger_config.print_and_log_info(f"File downloaded : {file_downloaded_path}")
        shutil.move(file_downloaded_path, f"{self.output_downloaded_files_final_directory_path}/states_changes_project_{label}.xlsx")

        return True

    # Locate the "History" tab using its unique attributes and click it
    def dowload_states_changes_excel_file_query(self, label: str) -> bool:
        return self.download_excel_file_query(label=label, file_to_create_path=f"{self.output_downloaded_files_final_directory_path}/states_changes_project_{label}.xlsx")

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

        # self.driver.command_executor.set_timeout(1000)

    def create_webdriver_and_login(self) -> None:
        self.create_webdriver_chrome()
        self.login_champfx()

    def reset_driver(self) -> None:
        self.driver.quit()
        self.create_webdriver_and_login()

    def login_champfx(self) -> None:
        logger_config.print_and_log_info("login_champfx")

        login_url = f"https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX?format=HTML&loginId={connexion_param.champfx_login}&password={connexion_param.champfx_password}"

        with logger_config.stopwatch_with_label(f"Driver get login url {login_url}"):
            self.driver.get(login_url)

        with logger_config.stopwatch_with_label(label="Waited page is loaded", enable_print=True):
            with surround_with_screenshots(label="login_champfx - title_contains ok", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
                WebDriverWait(self.driver, 100).until(expected_conditions.title_contains("01_CHAMP/CFX - IBM Rational ClearQuest"))
            # self.driver.get_screenshot_as_file("login_champfx: title_contains ok.png")

            with surround_with_screenshots(label="login_champfx - document.readyState complete", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
                WebDriverWait(self.driver, 40).until(lambda driver: self.driver.execute_script("return document.readyState") == "complete")
            try:
                with surround_with_screenshots(
                    label="login_champfx - text_to_be_present_in_element welcomeMsg", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path
                ):
                    WebDriverWait(self.driver, 100).until(expected_conditions.text_to_be_present_in_element((By.ID, "welcomeMsg"), "AD001\\fr232487"))
            except TimeoutException as e:
                logger_config.print_and_log_exception(e)

        with surround_with_screenshots(label="login_champfx - Additional waiting time", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
            with logger_config.stopwatch_with_label(label="Additional waiting time", enabled=True):
                time.sleep(10)

    def open_request_url(self, request_full_path: str) -> None:
        request_url = f"https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/QUERY/{request_full_path}?format=HTML&loginId={connexion_param.champfx_login}&password={connexion_param.champfx_password}&noframes=true"

        with logger_config.stopwatch_with_label(f"Driver get url {request_url}"):
            self.driver.get(request_url)
        self.driver.get_screenshot_as_file(f"{self.screenshots_output_relative_path}/open_request_url after get(request_url).png")

        with logger_config.stopwatch_with_label(label="Waited Title is now good"):
            WebDriverWait(self.driver, 10).until(expected_conditions.title_contains("01_CHAMP/CFX - IBM Rational ClearQuest"))
            self.driver.get_screenshot_as_file(f"{self.screenshots_output_relative_path}/open_request_url title_contains ok.png")

        with logger_config.stopwatch_with_label(label="Wait for the page to be fully loaded (JavaScript):: document.readyState now good"):
            WebDriverWait(self.driver, 10).until(lambda driver: self.driver.execute_script("return document.readyState") == "complete")
            self.driver.get_screenshot_as_file(f"{self.screenshots_output_relative_path}/open_request_url document.readyState complete.png")

        with logger_config.stopwatch_with_label(label="Additional waiting time", enabled=True):
            self.driver.get_screenshot_as_file(f"{self.screenshots_output_relative_path}/open_request_url before Additional waiting time.png")
            time.sleep(10)
            self.driver.get_screenshot_as_file(f"{self.screenshots_output_relative_path}/open_request_url after Additional waiting time.png")


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application"):
        logger_config.configure_logger_with_random_log_file_suffix("save_cfx_request_mutlpages_results")

        logger_config.print_and_log_info("Application start")

        parser = argparse.ArgumentParser(description="Your application description here.")

        parser.add_argument("--do_not_open_website_and_treat_previous_results", action=argparse.BooleanOptionalAction)

        output_parent_directory_name = OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME

        # first_cfx_index = 10
        # last_cfx_index = 100

        logger_config.print_and_log_info(f"output_parent_directory_name: {output_parent_directory_name}")

        application: SaveCfxRequestMultipagesResultsApplication = SaveCfxRequestMultipagesResultsApplication(
            output_parent_directory_name=output_parent_directory_name,
        )
        application.run()


if __name__ == "__main__":
    main()
