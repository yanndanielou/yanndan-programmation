import os
from enum import Enum, auto
from typing import cast

from logger import logger_config

# Third Party
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.remote_connection import RemoteConnection

DEFAULT_DOWNLOAD_DIRECTORY = os.path.expandvars(r"%userprofile%\downloads")


class BrowserVisibilityType(Enum):
    REGULAR = auto()
    NOT_VISIBLE_AKA_HEADLESS = auto()
    MINIMIZED = auto()


def create_webdriver_chrome(browser_visibility_type: BrowserVisibilityType, download_directory_path: str, global_timeout_in_seconds: int = 1000) -> webdriver.Chrome:
    logger_config.print_and_log_info("create_webdriver_chrome")
    chrome_driver_path = DEFAULT_DOWNLOAD_DIRECTORY + "\\chromedriver-win64\\chromedriver.exe"

    chrome_options = ChromeOptions()
    prefs = {
        "download.default_directory": download_directory_path,
        "savefile.default_directory": download_directory_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    if browser_visibility_type == BrowserVisibilityType.NOT_VISIBLE_AKA_HEADLESS:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")

    elif browser_visibility_type == BrowserVisibilityType.MINIMIZED:
        chrome_options.add_argument("--start-minimized")

    # chrome_options.add_argument("--remote-debugging-pipe")  # https://issues.chromium.org/issues/42323434#comment36
    driver_service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=driver_service, options=chrome_options)

    if browser_visibility_type == BrowserVisibilityType.MINIMIZED:
        try:
            driver.minimize_window()
        except Exception as exc:
            logger_config.print_and_log_exception(exc)

    cast(RemoteConnection, driver.command_executor).set_timeout(global_timeout_in_seconds)
    return driver


def create_webdriver_firefox(browser_visibility_type: BrowserVisibilityType) -> webdriver.Firefox:
    logger_config.print_and_log_info("create_webdriver_firefox")

    firefox_options = FirefoxOptions()
    if browser_visibility_type == BrowserVisibilityType.NOT_VISIBLE_AKA_HEADLESS:
        firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(options=firefox_options)
    if browser_visibility_type == BrowserVisibilityType.MINIMIZED:
        driver.minimize_window()

    return driver
