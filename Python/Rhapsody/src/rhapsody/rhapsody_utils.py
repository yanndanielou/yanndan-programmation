# Standard


import time
from typing import Optional

from common import download_utils, web_driver_utils

# Other libraries
from logger import logger_config

# Third Party
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


def download_file_from_rhapsody(
    file_to_download_pattern: str, file_to_download_url: str, file_move_after_download_action: Optional[download_utils.DownloadFileDetector.FileMoveAfterDownloadAction] = None
) -> Optional[str]:

    with logger_config.stopwatch_with_label(f"download_file_from_rhapsody file {file_to_download_pattern}"):

        driver = web_driver_utils.create_webdriver_firefox(web_driver_utils.BrowserVisibilityType.NOT_VISIBLE_AKA_HEADLESS)

        driver.get(file_to_download_url)

        with logger_config.stopwatch_with_label("download_file_from_rhapsody: additional waiting time:"):
            time.sleep(0.5)

        wait = WebDriverWait(driver, 10)
        more_providers_button = wait.until(expected_conditions.element_to_be_clickable((By.ID, "moreProviders")))
        more_providers_button.click()

        # Wait until the Azure option is visible and then click it
        azure_option = wait.until(expected_conditions.visibility_of_element_located((By.XPATH, "//li[@class='secondary-menu-item authprovider-choice' and @data-authhandler='Azure']")))

        download_file_detector = download_utils.DownloadFileDetector(
            directory_path=web_driver_utils.DEFAULT_DOWNLOAD_DIRECTORY,
            filename_pattern=file_to_download_pattern,
            timeout_in_seconds=30,
            file_move_after_download_action=file_move_after_download_action,
        )

        azure_option.click()

        file_downloaded_path: Optional[str] = download_file_detector.monitor_download()
        if not file_downloaded_path:
            logger_config.print_and_log_error("No downloaded file found")
            return None

        with logger_config.stopwatch_with_label("download_file_from_rhapsody: additional waiting time:"):
            time.sleep(1)

        driver.quit()
        return file_downloaded_path
