# Standard
# Standard
import argparse

import pickle

import threading
import queue
import os
import time

from dataclasses import dataclass, field
from typing import Optional, List, Dict

# Third Party
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import selenium.webdriver.chrome.options
import selenium.webdriver.firefox.options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains


import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import fnmatch
import os

# Other libraries

from logger import logger_config
from common import file_utils, download_utils

# Current programm
import connexion_param


CFX_EXCEL_FILES_DOWNLOADED_PATTERN = "QueryResult*.xlsx"

OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME = "output_save_cfx_request_results"
nom_du_fichier_final = "generated_file_yda.xlsx"

DEFAULT_DOWNLOAD_DIRECTORY = os.path.expandvars(r"%userprofile%\downloads")

CREATE_PARSED_EXTENDED_HISTORY_FILES = False

CREATE_PARSED_CURRENT_OWNNER_MODIFICATIONS_JSON_FILES = False

DEFAULT_DO_NOT_OPEN_WEBSITE_AND_TREAT_PREVIOUS_RESULTS = False
# DEFAULT_DO_NOT_OPEN_WEBSITE_AND_TREAT_PREVIOUS_RESULTS = True

DEFAULT_NUMBER_OF_THREADS = 2


@dataclass
class SaveCfxRequestMultipagesResultsApplication:
    output_parent_directory_name: str = OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME
    web_browser_download_directory = DEFAULT_DOWNLOAD_DIRECTORY

    errors_output_sub_directory_name = "errors"
    driver: ChromiumDriver = None

    def __post_init__(self) -> None:
        self.lock = threading.Lock()

    def run(self) -> None:

        for directory_path in [
            self.output_parent_directory_name,
            f"{self.output_parent_directory_name}/{self.errors_output_sub_directory_name}",
        ]:
            file_utils.create_folder_if_not_exist(directory_path)

        self.create_webdriver_and_login()

        change_state_query = "Personal%20Queries/NExTEO_ATS_Courbes/NExteo_ATSp_changements_etats"
        change_state_query = "Personal%20Queries/all_projects/all_projets_changements_etats"
        change_state_query = "66875867"
        self.open_request_url(change_state_query)

        # resp = webdriver.request('POST','https://www.facebook.com/login/device-based/regular/login/?login_attempt=1&lwv=110', params)

        selectionner_button_containerNode = WebDriverWait(self.driver, 100).until(
            expected_conditions.element_to_be_clickable((By.XPATH, "//span[@data-dojo-attach-point='containerNode' and text()='Sélectionner']"))
        )
        # selectionner_button_containerNode = self.driver.find_element(By.XPATH, "//span[@data-dojo-attach-point='containerNode' and text()='Sélectionner']")
        selectionner_button_containerNode.click()

        # list_projets_select_element = self.driver.find_element(By.ID, "cq_widget_CqDoubleListBox_0_choiceList")
        # select_selector = Select(list_projets_select_element)
        # select_selector.select_by_visible_text("FR_NEXTEO")

        nexteo_option_element = self.driver.find_element(By.XPATH, "//select[@id='cq_widget_CqDoubleListBox_0_choiceList']//option[text()='FR_NEXTEO']")
        actions = ActionChains(self.driver)
        actions.double_click(nexteo_option_element).perform()

        ok_button = self.driver.find_element(By.XPATH, "//span[@class='dijitReset dijitInline dijitButtonText' and text()='OK']")
        ok_button.click()

        executer_requete_button = self.driver.find_element(By.XPATH, "//span[@class='dijitReset dijitInline dijitButtonText' and text()='Exécuter la requête']")
        executer_requete_button.click()

        with logger_config.stopwatch_with_label(label="Additional waiting time", enabled=True):
            time.sleep(10)

        with logger_config.stopwatch_with_label(label="locate_save_excel_click_it", enabled=True):
            self.dowload_excel_file()

        time.sleep(1000)

    # Fonction pour vérifier l'achèvement de téléchargement
    def wait_for_download_to_complete(self, download_dir: str, timeout: int = 120) -> None:
        seconds_passed = 0
        while seconds_passed < timeout:
            files = os.listdir(download_dir)
            # Vérifiez si un fichier temporaire est téléchargé
            if not any(file.endswith(".part") or file.endswith(".crdownload") for file in files):
                # Si aucun fichier temporaire trouvé, vérifiez si le fichier Excel est présent et complet
                logger_config.print_and_log_info(f"downloaded is in progress {(file.endswith(".part") or file.endswith(".crdownload") for file in files)}")

                if any(file.endswith(".xlsx") for file in files):
                    logger_config.print_and_log_info(f"downloaded filee found:{(file.endswith(".xlsx") for file in files)}")
                    break
            time.sleep(1)
            seconds_passed += 1
        else:
            raise Exception("Le téléchargement n'a pas pu être confirmé dans le délai imparti.")

    # Locate the "History" tab using its unique attributes and click it
    def dowload_excel_file(self) -> None:

        arrow_to_acces_export = WebDriverWait(self.driver, 40).until(expected_conditions.element_to_be_clickable((By.ID, "dijit_form_ComboButton_1_arrow")))
        arrow_to_acces_export.click()

        self.driver.get_screenshot_as_file("after_arrow_to_acces_export_click.png")

        # history_tab = self.driver.find_element(By.XPATH, "//text()='Exporter vers un tableur Excel']")
        # export_button = self.driver.find_element(By.ID, "dijit_MenuItem_42")
        export_button = self.driver.find_element(By.XPATH, "//td[contains(text(),'Exporter vers un tableur Excel')]")
        export_button.click()

        file_downloaded_path: Optional[str] = download_utils.monitor_download(directory_path=self.web_browser_download_directory, filename_pattern=CFX_EXCEL_FILES_DOWNLOADED_PATTERN)

        file_utils.create_folder_if_not_exist(OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME)
        # Attendre que le fichier soit téléchargé
        self.wait_for_download_to_complete(OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME)

        # Trouver le fichier téléchargé le plus récent
        list_of_files = os.listdir(OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME)
        list_of_files = [file for file in list_of_files if file.startswith("QueryResult") and file.endswith(".xlsx")]
        latest_file = max([os.path.join(OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME, f) for f in list_of_files], key=os.path.getctime)
        logger_config.print_and_log_info(f"latest_file: {latest_file}")

        # Renommer le fichier téléchargé
        os.rename(latest_file, os.path.join(OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME, nom_du_fichier_final))

        # excel_export_button = self.driver.find_element(By.XPATH, "//td[contains(text(),'Exporter vers un tableur Excel')]")
        # "excel_export_button.click()
        pass

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
            WebDriverWait(self.driver, 100).until(expected_conditions.title_contains("01_CHAMP/CFX - IBM Rational ClearQuest"))
            WebDriverWait(self.driver, 40).until(lambda driver: self.driver.execute_script("return document.readyState") == "complete")
            try:
                WebDriverWait(self.driver, 100).until(expected_conditions.text_to_be_present_in_element((By.ID, "welcomeMsg"), "AD001\\fr232487"))
            except TimeoutException as e:
                logger_config.print_and_log_exception(e)

        with logger_config.stopwatch_with_label(label="Additional waiting time", enabled=True):
            time.sleep(10)

    def open_request_url(self, request_full_path: str) -> None:
        request_url = f"https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/QUERY/{request_full_path}?format=HTML&loginId={connexion_param.champfx_login}&password={connexion_param.champfx_password}&noframes=true"

        with logger_config.stopwatch_with_label(f"Driver get url {request_url}"):
            self.driver.get(request_url)

        with logger_config.stopwatch_with_label(label="Waited Title is now good"):
            WebDriverWait(self.driver, 10).until(expected_conditions.title_contains("01_CHAMP/CFX - IBM Rational ClearQuest"))

        with logger_config.stopwatch_with_label(label="Wait for the page to be fully loaded (JavaScript):: document.readyState now good"):
            WebDriverWait(self.driver, 10).until(lambda driver: self.driver.execute_script("return document.readyState") == "complete")

        with logger_config.stopwatch_with_label(label="Additional waiting time", enabled=True):
            time.sleep(11)


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
