from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from datetime import datetime, timezone

from common import json_encoders


import pandas

from logger import logger_config

import time
import re

import os


# Define a regular expression pattern to extract content between "====START====" and "====END===="
one_history_start_and_end_pattern = r"====START====(.*?)====END===="


def create_webdriver_chrome() -> webdriver.Chrome:
    # Path to the ChromeDriver
    chrome_driver_path = "C:\\Users\\fr232487\\Downloads\\chromedriver-win64\\chromedriver.exe"

    # Set up the Chrome options
    chrome_options = Options()

    # Create a new instance of the Chrome driver
    driver_service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=driver_service, options=chrome_options)

    return driver


def login_champfx(driver) -> None:
    login_url = "https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX?format=HTML&loginId=AD001%5Cfr232487&password=Zzeerrttyy9."

    with logger_config.stopwatch_with_label(f"Driver get login url {login_url}"):
        driver.get(login_url)
    # WebDriverWait(driver, 10).until(EC.url_contains("expected_url"))

    # Wait for the page to be fully loaded (JavaScript):

    with logger_config.stopwatch_with_label(f"Waited Title is now good"):
        WebDriverWait(driver, 100).until(expected_conditions.title_contains("01_CHAMP/CFX - IBM Rational ClearQuest"))

    with logger_config.stopwatch_with_label(f"Wait for the page to be fully loaded (JavaScript):: document.readyState now good"):
        WebDriverWait(driver, 40).until(lambda driver: driver.execute_script("return document.readyState") == "complete")

    with logger_config.stopwatch_with_label(f"Waited for welcome message"):
        try:
            welcome_msg_element = WebDriverWait(driver, 100).until(expected_conditions.text_to_be_present_in_element((By.ID, "welcomeMsg"), "AD001\\fr232487"))
        except TimeoutException as e:
            logger_config.print_and_log_error(str(e))


def open_cfx_url(cfx_id, driver):
    # URL of the web page you want to save
    cfx_url = f"https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/RECORD/{cfx_id}?format=HTML&loginId=AD001%5Cfr232487&password=Zzeerrttyy9.&noframes=true"

    with logger_config.stopwatch_with_label(f"Driver get url {cfx_url}"):
        driver.get(cfx_url)

    # Wait for the page to be fully loaded (JavaScript):

    with logger_config.stopwatch_with_label(f"Waited Title is now good"):
        WebDriverWait(driver, 10).until(expected_conditions.title_contains("01_CHAMP/CFX - IBM Rational ClearQuest"))

    with logger_config.stopwatch_with_label(f"Wait for the page to be fully loaded (JavaScript):: document.readyState now good"):
        WebDriverWait(driver, 10).until(lambda driver: driver.execute_script("return document.readyState") == "complete")

    # time.sleep(1)

    with logger_config.stopwatch_with_label(f"Waited for history tab available"):
        welcome_msg_element = WebDriverWait(driver, 10).until(expected_conditions.text_to_be_present_in_element((By.ID, "dijit_layout_TabContainer_1_tablist_dijit_layout_ContentPane_14"), "History"))

    # with logger_config.stopwatch_with_label(f"Waited for welcome message"):
    # welcome_msg_element = WebDriverWait(driver, 100).until(expected_conditions.text_to_be_present_in_element((By.ID, "welcomeMsg"), "AD001\\fr232487"))


def parse_section(section):
    section_data = {}
    lines = section.strip().split("\n")
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key == "Time":
                try:
                    section_data[key] = datetime.strptime(value, "%Y-%m-%d %H:%M:%S %z")
                except ValueError:
                    section_data[key] = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            elif key == "Schema Rev":
                section_data[key] = int(value)
            else:
                section_data[key] = value

    fields_start = lines.index("==Fields==") + 1
    fields_end = lines.index("", fields_start)
    fields = lines[fields_start:fields_end]

    field_data = {}
    for field in fields:
        field_name = field.split("(")[0].strip()
        field_values = field.split("(")[1][:-1].split(":")
        field_data[field_name] = {"Old": field_values[0].strip(), "New": field_values[1].strip()}

    section_data["Fields"] = field_data
    return section_data


def parse_extended_history_text(text):

    data = []
    sections = text.split("====START====")
    for section in sections[1:]:
        data.append(parse_section(section=section))


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application"):
        logger_config.configure_logger_with_random_log_file_suffix("SaveCfxWebPage")

        logger_config.print_and_log_info("Application start")

        driver = create_webdriver_chrome()

        login_champfx(driver=driver)

        output_directory_name = "output_save_cfx_webpage"
        if not os.path.exists(output_directory_name):
            os.mkdir(output_directory_name)

        champfx_details_excel_file_full_path = "extract_cfx_details.xlsx"
        with logger_config.stopwatch_with_label(f"Open cfx details excel file {champfx_details_excel_file_full_path}"):
            cfx_details_data_frame = pandas.read_excel(champfx_details_excel_file_full_path)

            all_cfx_id = set([row["CFXID"] for index, row in cfx_details_data_frame.iterrows()])

        logger_config.print_and_log_info(f"{len(all_cfx_id)} cfx to parse")

        for cfx_id in all_cfx_id:

            with logger_config.stopwatch_with_label(f"open_cfx_url {cfx_id}"):
                open_cfx_url(cfx_id=cfx_id, driver=driver)

            """  max_delay = 50

            for i in range(1, max_delay):
                time.sleep(1)  # Wait for the page to load completely
                print(i)
                page_html = driver.page_source
                page_url = driver.current_url
                logger_config.print_and_log_info(f"Delay {print} url {page_url}")

                page_html_content_depending[i] = page_html

                with open(f"{output_directory_name}/text_dump_file_{i}.txt", "w", encoding="utf-8") as text_dump_file:
                    text_dump_file.write(page_html) """

            # print(page_html)

            # Locate the "History" tab using its unique attributes and click it
            history_tab = driver.find_element(By.XPATH, "//span[@data-dojo-attach-point='containerNode,focusNode' and text()='History']")
            history_tab.click()

            extended_history_div = driver.find_element(By.XPATH, "//div[@id='cq_widget_CqReadonlyTextArea_4']")
            extended_history_text = extended_history_div.text

            with open(f"{output_directory_name}/{cfx_id}_cq_widget_CqReadonlyTextArea_4.txt", "w", encoding="utf-8") as text_dump_file:
                text_dump_file.write(extended_history_text)

            json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(extended_history_text.split("====START===="), f"{output_directory_name}/{cfx_id}_raw_sections.json")

            try:
                parsed_extended_history = parse_extended_history_text(extended_history_text)
            except:
                parsed_extended_history = "Could not parse extended_history_text"

            # Use re.findall to extract all matching content
            # history_entries = re.findall(one_history_start_and_end_pattern, extended_history_text, re.DOTALL)

            # print(history_entries)
            json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(parsed_extended_history, f"{output_directory_name}/{cfx_id}_parsed_extended_history.txt")

            # Create a history object
            # history = {"entries": history_entries}

            # Simulate Ctrl+S to open "Save As" dialog
            # driver.execute_script("window.print();")  # Print invokes the Save Page As dialog in some configurations

            # Pause for a realistic delay if needed to manually complete the save, if auto-save not configured
            time.sleep(5)


if __name__ == "__main__":
    main()
