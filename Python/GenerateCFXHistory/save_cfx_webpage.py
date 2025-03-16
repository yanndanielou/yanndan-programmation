# Standard
import argparse

import pickle

import threading
import queue
import os

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

import pandas


# Other libraries

from logger import logger_config
from common import json_encoders

# Current programm
import cfx_extended_history
import connexion_param


OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME = "output_save_cfx_webpage"


CREATE_PARSED_EXTENDED_HISTORY_FILES = False

CREATE_PARSED_CURRENT_OWNNER_MODIFICATIONS_JSON_FILES = False

DO_NOT_OPEN_WEBSITE_AND_TREAT_PREVIOUS_RESULTS = False
# DO_NOT_OPEN_WEBSITE_AND_TREAT_PREVIOUS_RESULTS = True

DEFAULT_NUMBER_OF_THREADS = 2


@dataclass
class SaveCfxWebpageApplication:
    first_cfx_index: Optional[int]
    last_cfx_index: Optional[int]
    _number_of_threads: int
    output_parent_directory_name: str = OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME
    all_current_owner_modifications: List[cfx_extended_history.CFXHistoryField] = field(default_factory=list)
    all_current_owner_modifications_per_cfx: Dict[str, cfx_extended_history.CFXHistoryField] = field(default_factory=dict)

    extended_history_raw_text_sub_output_directory_name = "extended_history_raw_text"
    parsed_extended_history_sub_output_directory_name = "parsed_extended_history"
    parsed_current_owner_changes_output_directory_name = "parsed_current_owner_changes"

    errors_output_sub_directory_name = "errors"

    def __post_init__(self):
        self.lock = threading.Lock()

    def add_all_current_owner_modification(self, cfx_id: str, current_owner_field_modifications: List[cfx_extended_history.CFXHistoryField]):
        with self.lock:
            self.all_current_owner_modifications.extend(current_owner_field_modifications)
            self.all_current_owner_modifications_per_cfx[cfx_id] = current_owner_field_modifications

    def run(self):

        for directory_path in [
            self.output_parent_directory_name,
            f"{self.output_parent_directory_name}/{self.extended_history_raw_text_sub_output_directory_name}",
            f"{self.output_parent_directory_name}/{self.parsed_extended_history_sub_output_directory_name}",
            f"{self.output_parent_directory_name}/{self.errors_output_sub_directory_name}",
            f"{self.output_parent_directory_name}/{self.parsed_current_owner_changes_output_directory_name}",
        ]:
            if not os.path.exists(directory_path):
                logger_config.print_and_log_info(f"Create folder {directory_path}")
                os.mkdir(directory_path)
            else:
                logger_config.print_and_log_info(f"Folder {directory_path} already exists")

        all_cfx_id_unique_ordered_list: list[str] = self.get_all_cfx_id_unique_ordered_list()
        all_cfx_id_to_handle_unique_ordered_list = all_cfx_id_unique_ordered_list[self.first_cfx_index : self.last_cfx_index]
        logger_config.print_and_log_info(f"Number of cfx to treat: {len(all_cfx_id_to_handle_unique_ordered_list)}")

        task_queue = queue.Queue()

        with logger_config.stopwatch_with_label("Create Threads"):
            threads = []
            for _ in range(self._number_of_threads):
                thread = HandlingCfxThread(task_queue=task_queue, application=self)
                thread.start()
                threads.append(thread)

        with logger_config.stopwatch_with_label("Add tasks to the queue"):
            for cfx_id_to_handle in all_cfx_id_to_handle_unique_ordered_list:
                task_queue.put(cfx_id_to_handle)

        with logger_config.stopwatch_with_label("Block until all tasks are done"):
            task_queue.join()

        with logger_config.stopwatch_with_label("Stop the threads by adding a sentinel object (None)"):
            for _ in threads:
                task_queue.put(None)
            for thread in threads:
                thread.join()

        # for cfx_id in all_cfx_id_to_handle_unique_ordered_list:
        #    self.handle_cfx(cfx_id=cfx_id)

        all_current_owner_modifications_json_file_full_path = f"{self.output_parent_directory_name}/all_current_owner_modifications.json"
        all_current_owner_modifications_pickel_file_full_path = f"{self.output_parent_directory_name}/all_current_owner_modifications.pkl"

        all_current_owner_modifications_per_cfx_json_file_full_path = f"{self.output_parent_directory_name}/all_current_owner_modifications_per_cfx.json"
        all_current_owner_modifications_per_cfx_picke_filel_full_path = f"{self.output_parent_directory_name}/all_current_owner_modifications_per_cfx.pkl"

        with logger_config.stopwatch_with_label("Create current owner modification json files"):
            json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(list_objects=self.all_current_owner_modifications, json_file_full_path=all_current_owner_modifications_json_file_full_path)
            json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(
                list_objects=self.all_current_owner_modifications_per_cfx, json_file_full_path=all_current_owner_modifications_per_cfx_json_file_full_path
            )

        with logger_config.stopwatch_with_label("Create current owner modification pickle files"):
            with open(all_current_owner_modifications_pickel_file_full_path, "wb") as file:
                pickle.dump(self.all_current_owner_modifications, file)
            with open(all_current_owner_modifications_per_cfx_picke_filel_full_path, "wb") as file:
                pickle.dump(self.all_current_owner_modifications_per_cfx, file)

    def get_all_cfx_id_unique_ordered_list(self) -> list[str]:
        champfx_details_excel_file_full_path = "Input/extract_cfx_details.xlsx"
        with logger_config.stopwatch_with_label(f"Open cfx details excel file {champfx_details_excel_file_full_path}"):
            cfx_details_data_frame = pandas.read_excel(champfx_details_excel_file_full_path)
            all_cfx_id_unique_ordered_list = sorted(list(set([row["CFXID"] for index, row in cfx_details_data_frame.iterrows()])))

        logger_config.print_and_log_info(f"{len(all_cfx_id_unique_ordered_list)} cfx found")
        return all_cfx_id_unique_ordered_list


class HandlingCfxThread(threading.Thread):

    def __init__(self, task_queue: queue.Queue, application: SaveCfxWebpageApplication):
        threading.Thread.__init__(self)
        self._application = application

        self.task_queue = task_queue

        self.driver: ChromiumDriver = None

    def run(self):
        if not DO_NOT_OPEN_WEBSITE_AND_TREAT_PREVIOUS_RESULTS:
            with logger_config.stopwatch_with_label("create_webdriver_and_login"):
                self.create_webdriver_and_login()

        while True:
            cfx_id = self.task_queue.get()  # Get a task from the queue
            if cfx_id is None:  # None is a signal to stop the thread
                break
            # Implement the complex logic here
            self.handle_cfx(cfx_id)
            self.task_queue.task_done()  # Signal completion of the task

    def create_webdriver_firefox(self):
        logger_config.print_and_log_info("create_webdriver_firefox")

        options = selenium.webdriver.firefox.options.Options()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)

    def create_webdriver_chrome(self):
        logger_config.print_and_log_info("create_webdriver_chrome")
        # Path to the ChromeDriver
        chrome_driver_path = "C:\\Users\\fr232487\\Downloads\\chromedriver-win64\\chromedriver.exe"

        # Set up the Chrome options
        chrome_options = selenium.webdriver.chrome.options.Options()
        chrome_options.headless = True

        # Create a new instance of the Chrome self.driver
        driver_service = Service(chrome_driver_path)
        self.driver = webdriver.Chrome(service=driver_service, options=chrome_options)

    def create_webdriver_and_login(self):
        self.create_webdriver_chrome()
        # create_webdriver_firefox()
        self.login_champfx()

    def reset_driver(self):
        self.driver.quit()
        self.create_webdriver_and_login()

    def login_champfx(self) -> None:
        logger_config.print_and_log_info("login_champfx")

        login_url = f"https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX?format=HTML&loginId={connexion_param.champfx_login}&password={connexion_param.champfx_password}"

        with logger_config.stopwatch_with_label(f"Driver get login url {login_url}"):
            self.driver.get(login_url)

        with logger_config.stopwatch_with_label(label="Waited page is loaded", enable_print=False):
            WebDriverWait(self.driver, 100).until(expected_conditions.title_contains("01_CHAMP/CFX - IBM Rational ClearQuest"))
            WebDriverWait(self.driver, 40).until(lambda driver: self.driver.execute_script("return document.readyState") == "complete")
            try:
                WebDriverWait(self.driver, 100).until(expected_conditions.text_to_be_present_in_element((By.ID, "welcomeMsg"), "AD001\\fr232487"))
            except TimeoutException as e:
                logger_config.print_and_log_exception(e)

    def open_cfx_url(self, cfx_id: str) -> None:
        # URL of the web page you want to save
        cfx_url = (
            f"https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/RECORD/{cfx_id}?format=HTML&loginId={connexion_param.champfx_login}&password={connexion_param.champfx_password}&noframes=true"
        )

        with logger_config.stopwatch_with_label(f"Driver get url {cfx_url}", enabled=False):
            self.driver.get(cfx_url)

        with logger_config.stopwatch_with_label(label="Waited page to be loaded", enabled=False):

            with logger_config.stopwatch_with_label(label="Waited Title is now good", enabled=False):
                WebDriverWait(self.driver, 10).until(expected_conditions.title_contains("01_CHAMP/CFX - IBM Rational ClearQuest"))

            with logger_config.stopwatch_with_label(label="Wait for the page to be fully loaded (JavaScript):: document.readyState now good", enabled=False):
                WebDriverWait(self.driver, 10).until(lambda driver: self.driver.execute_script("return document.readyState") == "complete")

            with logger_config.stopwatch_with_label(label="Waited for history tab available", enabled=False):
                WebDriverWait(self.driver, 10).until(expected_conditions.text_to_be_present_in_element((By.ID, "dijit_layout_TabContainer_1_tablist_dijit_layout_ContentPane_14"), "History"))

    # Locate the "History" tab using its unique attributes and click it
    def locate_hitory_tab_and_click_it(self) -> None:
        history_tab = self.driver.find_element(By.XPATH, "//span[@data-dojo-attach-point='containerNode,focusNode' and text()='History']")
        history_tab.click()

    def get_extended_history_text(self) -> str:

        extended_history_div = self.driver.find_element(By.XPATH, "//div[@id='cq_widget_CqReadonlyTextArea_4']")
        extended_history_text = extended_history_div.text
        return extended_history_text

    def get_extended_history_raw_text_output_file_name(self, cfx_id: str) -> str:
        extended_history_raw_text_output_file_name = f"{cfx_id}_raw_extended_history.txt"
        extended_history_raw_text_output_file_full_path = (
            f"{self._application.output_parent_directory_name}/{self._application.extended_history_raw_text_sub_output_directory_name}/{extended_history_raw_text_output_file_name}"
        )
        return extended_history_raw_text_output_file_full_path

    def load_extended_history_from_file(self, cfx_id: str) -> None:
        with open(self.get_extended_history_raw_text_output_file_name(cfx_id=cfx_id), "r", encoding="utf-8") as text_raw_extended_history_file:
            raw_extended_history = text_raw_extended_history_file.read()
            return raw_extended_history

    def save_extended_history(self, cfx_id: str, extended_history_text: str) -> str:
        with open(self.get_extended_history_raw_text_output_file_name(cfx_id=cfx_id), "w", encoding="utf-8") as text_raw_extended_history_file:
            text_raw_extended_history_file.write(extended_history_text)

    def process_extended_history(self, cfx_id: str, extended_history_text: str) -> None:

        with logger_config.stopwatch_with_label("Process extended_history_text"):

            parsed_extended_history_file_name = f"{cfx_id}_parsed_extended_history.json"
            parsed_extended_history_file_full_path = (
                f"{self._application.output_parent_directory_name}/{self._application.parsed_extended_history_sub_output_directory_name}/{parsed_extended_history_file_name}"
            )
            change_current_owner_only_fields_modification_json_file_full_path = (
                f"{self._application.output_parent_directory_name}/{self._application.parsed_current_owner_changes_output_directory_name}/{cfx_id}_change_current_owner_only_fields_modifications.json"
            )
            change_current_owner_only_fields_modification_picke_file_full_path = (
                f"{self._application.output_parent_directory_name}/{self._application.parsed_current_owner_changes_output_directory_name}/{cfx_id}_change_current_owner_only_fields_modifications.pkl"
            )
            try:
                parsed_extended_history = cfx_extended_history.parse_history(cfx_id=cfx_id, extended_history_text=extended_history_text)

                if CREATE_PARSED_EXTENDED_HISTORY_FILES:
                    with logger_config.stopwatch_with_label(f"Create {parsed_extended_history_file_full_path}"):
                        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(parsed_extended_history, parsed_extended_history_file_full_path)

                parsed_extended_history_all_current_owner_field_modifications = parsed_extended_history.get_all_current_owner_field_modifications()

                if CREATE_PARSED_CURRENT_OWNNER_MODIFICATIONS_JSON_FILES:
                    with logger_config.stopwatch_with_label(f"Create {change_current_owner_only_fields_modification_json_file_full_path}"):
                        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(
                            parsed_extended_history_all_current_owner_field_modifications, change_current_owner_only_fields_modification_json_file_full_path
                        )
                with logger_config.stopwatch_with_label(f"Create {change_current_owner_only_fields_modification_picke_file_full_path}", enabled=False):
                    with open(change_current_owner_only_fields_modification_picke_file_full_path, "wb") as file:
                        pickle.dump(parsed_extended_history_all_current_owner_field_modifications, file)

                self._application.add_all_current_owner_modification(cfx_id=cfx_id, current_owner_field_modifications=parsed_extended_history_all_current_owner_field_modifications)

            except Exception as e:
                logger_config.print_and_log_exception(exception_to_print=e)
                json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(
                    str(e), f"{self._application.output_parent_directory_name}/{self._application.errors_output_sub_directory_name}/{parsed_extended_history_file_name}"
                )
                with open(change_current_owner_only_fields_modification_json_file_full_path, "w", encoding="utf-8") as text_dump_file:
                    text_dump_file.write(str(e))

    def safe_extract_extended_history_text_from_website(self, cfx_id: str) -> str:

        try:
            return self.extract_extended_history_text_from_website(cfx_id=cfx_id)

        except Exception as e:
            logger_config.print_and_log_exception(additional_text=cfx_id, exception_to_print=e)
            self.reset_driver()
            return self.extract_extended_history_text_from_website(cfx_id=cfx_id)

    def extract_extended_history_text_from_website(self, cfx_id: str) -> str:
        with logger_config.stopwatch_with_label(f"open_cfx_url {cfx_id}"):
            self.open_cfx_url(cfx_id=cfx_id)

        self.locate_hitory_tab_and_click_it()

        extended_history_text = self.get_extended_history_text()
        self.save_extended_history(cfx_id, extended_history_text)

        return extended_history_text

    def handle_cfx(self, cfx_id: str):

        if DO_NOT_OPEN_WEBSITE_AND_TREAT_PREVIOUS_RESULTS:
            extended_history_text = self.load_extended_history_from_file(cfx_id=cfx_id)

        else:
            extended_history_text = self.safe_extract_extended_history_text_from_website(cfx_id=cfx_id)

        self.process_extended_history(cfx_id, extended_history_text)


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application"):
        logger_config.configure_logger_with_random_log_file_suffix("SaveCfxWebPage")

        logger_config.print_and_log_info("Application start")

        parser = argparse.ArgumentParser(description="Your application description here.")
        parser.add_argument("--first_cfx_index", type=int, help="first_cfx_index.", default=None)
        parser.add_argument("--last_cfx_index", type=int, help="last_cfx_index.", default=None)
        parser.add_argument("--number_of_threads", type=int, help="Number of threads.", default=DEFAULT_NUMBER_OF_THREADS)

        args = parser.parse_args()

        first_cfx_index = args.first_cfx_index
        last_cfx_index = args.last_cfx_index
        number_of_threads = args.number_of_threads

        output_parent_directory_name = (
            OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME if (first_cfx_index is None and last_cfx_index is None) else f"{OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME}_{first_cfx_index}_{last_cfx_index}"
        )

        output_parent_directory_name = output_parent_directory_name + f"_{number_of_threads}_Threads"

        # first_cfx_index = 10
        # last_cfx_index = 100

        logger_config.print_and_log_info(f"first_cfx_index:{first_cfx_index}")
        logger_config.print_and_log_info(f"last_cfx_index: {last_cfx_index}")
        logger_config.print_and_log_info(f"output_parent_directory_name: {output_parent_directory_name}")
        logger_config.print_and_log_info(f"number_of_threads: {number_of_threads}")

        application: SaveCfxWebpageApplication = SaveCfxWebpageApplication(
            first_cfx_index=first_cfx_index, last_cfx_index=last_cfx_index, output_parent_directory_name=output_parent_directory_name, _number_of_threads=number_of_threads
        )
        application.run()


if __name__ == "__main__":
    main()
