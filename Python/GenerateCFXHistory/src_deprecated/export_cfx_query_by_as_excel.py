import os
from dataclasses import dataclass

import selenium.webdriver.chrome.options
import selenium.webdriver.firefox.options
from logger import logger_config
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

import connexion_param

OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME = "export_query_to_excel"

CCB_QUERY = f"https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/QUERY/Personal%20Queries/NEXTEO/ATS%2B%20%26%20NExTEO%20pour%20CMC?format=HTML&loginId={connexion_param.champfx_login}&password={connexion_param.champfx_password}&noframes=true"

# https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/REPORT/Personal%20Queries/NExTEO%20%26%20ATS%2B/ATS%2B%20%26%20NExTEO%20changements%20%C3%A9tats?format=HTML&loginId={{loginid}}&password={{password}}&noframes=true

# https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/QUERY/Personal%20Queries/NEXTEO/ATS%2B%20%26%20NExTEO%20pour%20CMC?format=HTML&loginId=AD001%5Cfr232487&password=Zzeerrttyy9.&noframes=true
# https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/QUERY/Personal%20Queries/NEXTEO/NExTEO%20%26%20ATS%2B/ATS%2B%20%26%20NExTEO%20changements%20%C3%A9tats?format=HTML&loginId=AD001%5Cfr232487&


@dataclass
class ExportCfxQueryApplication:
    output_parent_directory_name: str = OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME
    driver: ChromiumDriver = None

    def run(self):

        self.create_webdriver_and_login()

        for directory_path in [self.output_parent_directory_name]:
            if not os.path.exists(directory_path):
                logger_config.print_and_log_info(f"Create folder {directory_path}")
                os.mkdir(directory_path)
            else:
                logger_config.print_and_log_info(f"Folder {directory_path} already exists")

        with logger_config.stopwatch_with_label(f"open_cfx_url CCB"):
            self.open_query_url(query_url=CCB_QUERY)

        self.driver.implicitly_wait(10)

        with logger_config.stopwatch_with_label(f"locate_save_excel_click_it"):
            self.locate_save_excel_click_it()
        pass
        pass

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
        # self.create_webdriver_firefox()
        self.login_champfx()

    def reset_driver(self):
        self.driver.quit()
        self.create_webdriver_and_login()

    def login_champfx(self) -> None:
        logger_config.print_and_log_info("login_champfx")

        login_url = f"https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX?format=HTML&loginId={connexion_param.champfx_login}&password={connexion_param.champfx_password}"

        with logger_config.stopwatch_with_label(f"Driver get login url {login_url}"):
            self.driver.get(login_url)

        with logger_config.stopwatch_with_label("Waited Title is now good"):
            WebDriverWait(self.driver, 300).until(expected_conditions.title_contains("01_CHAMP/CFX - IBM Rational ClearQuest"))

        with logger_config.stopwatch_with_label("Wait for the page to be fully loaded (JavaScript):: document.readyState now good"):
            WebDriverWait(self.driver, 40).until(lambda driver: self.driver.execute_script("return document.readyState") == "complete")

        with logger_config.stopwatch_with_label("Waited for welcome message"):
            try:
                WebDriverWait(self.driver, 100).until(expected_conditions.text_to_be_present_in_element((By.ID, "welcomeMsg"), "AD001\\fr232487"))
            except TimeoutException as e:
                logger_config.print_and_log_error(str(e))

    def open_query_url(self, query_url: str) -> None:

        with logger_config.stopwatch_with_label(f"Driver get url {query_url}"):
            self.driver.get(query_url)

        with logger_config.stopwatch_with_label("Waited Title is now good"):
            WebDriverWait(self.driver, 10).until(expected_conditions.title_contains("01_CHAMP/CFX - IBM Rational ClearQuest"))

        with logger_config.stopwatch_with_label("Wait for the page to be fully loaded (JavaScript):: document.readyState now good"):
            WebDriverWait(self.driver, 10).until(lambda driver: self.driver.execute_script("return document.readyState") == "complete")

        # with logger_config.stopwatch_with_label("Waited for save to excel"):
        #    WebDriverWait(self.driver, 10).until(expected_conditions.text_to_be_present_in_element((By.ID, "dijit_MenuItem_42_text"), "Exporter vers un tableur Excel"))

        # with logger_config.stopwatch_with_label("Waited for save to excel"):
        #    WebDriverWait(self.driver, 10).until(expected_conditions.text_to_be_present_in_element((By.ID, "dijit_MenuItem_41_text"), "Exporter vers un fichier texte"))

        pass

    # Locate the "History" tab using its unique attributes and click it
    def locate_save_excel_click_it(self) -> None:
        # history_tab = self.driver.find_element(By.XPATH, "//text()='Exporter vers un tableur Excel']")
        # export_button = self.driver.find_element(By.ID, "dijit_MenuItem_42")
        export_button = self.driver.find_element(By.XPATH, "//td[contains(text(),'Exporter vers un tableur Excel')]")

        export_button.click()


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application"):
        logger_config.configure_logger_with_random_log_file_suffix("ExportCfxQuery")

        logger_config.print_and_log_info("Application start")
        application: ExportCfxQueryApplication = ExportCfxQueryApplication()
        application.run()


if __name__ == "__main__":
    main()
