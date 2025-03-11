import argparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import selenium.webdriver.chrome.options
from selenium import webdriver
import selenium.webdriver.firefox.options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chromium.webdriver import ChromiumDriver

from typing import Optional


import cfx_extended_history


from common import json_encoders

import connexion_param


import pandas

from logger import logger_config


import os


def create_webdriver_firefox() -> ChromiumDriver:
    logger_config.print_and_log_info("create_webdriver_firefox")

    options = selenium.webdriver.firefox.options.Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    return driver


def create_webdriver_chrome() -> ChromiumDriver:
    logger_config.print_and_log_info("create_webdriver_chrome")
    # Path to the ChromeDriver
    chrome_driver_path = "C:\\Users\\fr232487\\Downloads\\chromedriver-win64\\chromedriver.exe"

    # Set up the Chrome options
    chrome_options = selenium.webdriver.chrome.options.Options()
    chrome_options.headless = True

    # Create a new instance of the Chrome driver
    driver_service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=driver_service, options=chrome_options)

    return driver


def create_webdriver_and_login() -> ChromiumDriver:
    driver = create_webdriver_chrome()
    # driver = create_webdriver_firefox()
    login_champfx(driver)
    return driver


def reset_driver(driver: ChromiumDriver) -> ChromiumDriver:
    driver.quit()
    driver = create_webdriver_and_login()
    return driver


def login_champfx(driver: ChromiumDriver) -> None:
    logger_config.print_and_log_info("login_champfx")

    login_url = f"https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX?format=HTML&loginId={connexion_param.champfx_login}&password={connexion_param.champfx_password}"

    with logger_config.stopwatch_with_label(f"Driver get login url {login_url}"):
        driver.get(login_url)

    with logger_config.stopwatch_with_label(f"Waited Title is now good"):
        WebDriverWait(driver, 100).until(expected_conditions.title_contains("01_CHAMP/CFX - IBM Rational ClearQuest"))

    with logger_config.stopwatch_with_label(f"Wait for the page to be fully loaded (JavaScript):: document.readyState now good"):
        WebDriverWait(driver, 40).until(lambda driver: driver.execute_script("return document.readyState") == "complete")

    with logger_config.stopwatch_with_label(f"Waited for welcome message"):
        try:
            welcome_msg_element = WebDriverWait(driver, 100).until(expected_conditions.text_to_be_present_in_element((By.ID, "welcomeMsg"), "AD001\\fr232487"))
        except TimeoutException as e:
            logger_config.print_and_log_error(str(e))


def open_cfx_url(cfx_id: str, driver: ChromiumDriver) -> None:
    # URL of the web page you want to save
    cfx_url = f"https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/RECORD/{cfx_id}?format=HTML&loginId={connexion_param.champfx_login}&password={connexion_param.champfx_password}&noframes=true"

    with logger_config.stopwatch_with_label(f"Driver get url {cfx_url}"):
        driver.get(cfx_url)

    with logger_config.stopwatch_with_label(f"Waited Title is now good"):
        WebDriverWait(driver, 10).until(expected_conditions.title_contains("01_CHAMP/CFX - IBM Rational ClearQuest"))

    with logger_config.stopwatch_with_label(f"Wait for the page to be fully loaded (JavaScript):: document.readyState now good"):
        WebDriverWait(driver, 10).until(lambda driver: driver.execute_script("return document.readyState") == "complete")

    with logger_config.stopwatch_with_label(f"Waited for history tab available"):
        welcome_msg_element = WebDriverWait(driver, 10).until(expected_conditions.text_to_be_present_in_element((By.ID, "dijit_layout_TabContainer_1_tablist_dijit_layout_ContentPane_14"), "History"))


# Locate the "History" tab using its unique attributes and click it
def locate_hitory_tab_and_click_it(cfx_id: str, driver: ChromiumDriver) -> None:
    history_tab = driver.find_element(By.XPATH, "//span[@data-dojo-attach-point='containerNode,focusNode' and text()='History']")
    history_tab.click()


def get_extended_history_text(driver: ChromiumDriver) -> str:

    extended_history_div = driver.find_element(By.XPATH, "//div[@id='cq_widget_CqReadonlyTextArea_4']")
    extended_history_text = extended_history_div.text
    return extended_history_text


def save_extended_history(output_directory_name: str, cfx_id: str, extended_history_text: str) -> None:

    with open(f"{output_directory_name}/{cfx_id}_cq_widget_CqReadonlyTextArea_4.txt", "w", encoding="utf-8") as text_dump_file:
        text_dump_file.write(extended_history_text)

    with logger_config.stopwatch_with_label("Parse and save extended_history_text"):

        with logger_config.stopwatch_with_label(f"parse_extended_history_text method"):

            try:
                parsed_extended_history = cfx_extended_history.parse_history(extended_history_text)
            except:
                parsed_extended_history = "Could not parse extended_history_text"

        with logger_config.stopwatch_with_label(f"Create {output_directory_name}/{cfx_id}_parsed_extended_history.txt"):
            json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(parsed_extended_history, f"{output_directory_name}/{cfx_id}_parsed_extended_history.json")


def safe_handle_cfx(output_directory_name: str, cfx_id: str, driver: ChromiumDriver) -> ChromiumDriver:
    try:
        handle_cfx(output_directory_name=output_directory_name, cfx_id=cfx_id, driver=driver)

    except Exception as e:
        logger_config.print_and_log_exception(cfx_id, e)
        driver = reset_driver(driver)
        handle_cfx(output_directory_name=output_directory_name, cfx_id=cfx_id, driver=driver)

    return driver


def handle_cfx(output_directory_name: str, cfx_id: str, driver: ChromiumDriver) -> ChromiumDriver:

    with logger_config.stopwatch_with_label(f"open_cfx_url {cfx_id}"):
        open_cfx_url(cfx_id=cfx_id, driver=driver)

    locate_hitory_tab_and_click_it(cfx_id=cfx_id, driver=driver)

    extended_history_text = get_extended_history_text(driver=driver)

    save_extended_history(output_directory_name, cfx_id, extended_history_text)


def get_all_cfx_id_unique_ordered_list() -> list[str]:
    champfx_details_excel_file_full_path = "extract_cfx_details.xlsx"
    with logger_config.stopwatch_with_label(f"Open cfx details excel file {champfx_details_excel_file_full_path}"):
        cfx_details_data_frame = pandas.read_excel(champfx_details_excel_file_full_path)
        all_cfx_id_unique_ordered_list = sorted(list(set([row["CFXID"] for index, row in cfx_details_data_frame.iterrows()])))

    logger_config.print_and_log_info(f"{len(all_cfx_id_unique_ordered_list)} cfx found")
    return all_cfx_id_unique_ordered_list


def run_application(first_cfx_index: Optional[int], last_cfx_index: Optional[int]) -> None:
    logger_config.print_and_log_info(f"run_application, handle CFX index from {first_cfx_index} to {last_cfx_index}")
    driver: ChromiumDriver = create_webdriver_and_login()

    output_directory_name = "output_save_cfx_webpage"
    if not os.path.exists(output_directory_name):
        os.mkdir(output_directory_name)

    all_cfx_id_unique_ordered_list = get_all_cfx_id_unique_ordered_list()
    all_cfx_id_to_handle_unique_ordered_list = all_cfx_id_unique_ordered_list[first_cfx_index:last_cfx_index]

    logger_config.print_and_log_info(f"Number of cfx to treat: {len(all_cfx_id_to_handle_unique_ordered_list)}")

    for cfx_id in all_cfx_id_to_handle_unique_ordered_list:
        driver = safe_handle_cfx(output_directory_name=output_directory_name, cfx_id=cfx_id, driver=driver)


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application"):
        logger_config.configure_logger_with_random_log_file_suffix("SaveCfxWebPage")

        logger_config.print_and_log_info("Application start")

        parser = argparse.ArgumentParser(description="Your application description here.")
        parser.add_argument("--first_cfx_index", type=int, help="An integer parameter for your application.", default=None)
        parser.add_argument("--last_cfx_index", type=str, help="A string parameter for your application.", default=None)

        args = parser.parse_args()

        first_cfx_index = args.first_cfx_index
        last_cfx_index = args.last_cfx_index

        run_application(first_cfx_index, last_cfx_index)


if __name__ == "__main__":
    main()
