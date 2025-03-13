from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import selenium.webdriver.chrome.options
import selenium.webdriver.firefox.options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chromium.webdriver import ChromiumDriver

chrome_driver_path = "C:\\Users\\fr232487\\Downloads\\chromedriver-win64\\chromedriver.exe"
chrome_options = selenium.webdriver.chrome.options.Options()
# chrome_options.headless = True
driver_service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=driver_service, options=chrome_options)
# login_url = f"https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX?format=HTML&loginId=AD001%5Cfr232487&password\=Zzeerrttyy9."
# driver.get(login_url)
ccb_nexteo_query_url = f"https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/QUERY/Personal%20Queries/NEXTEO/ATS%2B%20%26%20NExTEO%20pour%20CMC?format=HTML&loginId=AD001%5Cfr232487&password\=Zzeerrttyy9.&noframes=true"
driver.get(ccb_nexteo_query_url)
export_button = driver.find_element(By.ID, "dijit_form_ComboButton_1_label")
export_button.click()
