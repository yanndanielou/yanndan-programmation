import time
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
time.sleep(1)
driver = webdriver.Chrome(service=driver_service, options=chrome_options)
time.sleep(1)
connexion_param_champfx_login = "AD001%5Cfr232487"
connexion_param_champfx_password = "Zzeerrttyy9."
login_url = f"https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX?format=HTML&loginId={connexion_param_champfx_login}&password={connexion_param_champfx_password}"
# https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX?format=HTML&loginId=AD001%5Cfr232487&password=Zzeerrttyy9."
driver.get(login_url)
time.sleep(50)
ccb_nexteo_query_url = f"https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/QUERY/Personal%20Queries/NEXTEO/ATS%2B%20%26%20NExTEO%20pour%20CMC?format=HTML&loginId={connexion_param_champfx_login}&password={connexion_param_champfx_password}&noframes=true"
driver.get(ccb_nexteo_query_url)
time.sleep(30)

with open("D:\\temp\\before_arrow_to_acces_export_click.txt", "w", encoding="utf-8") as text_dump_file:
    text_dump_file.write(driver.page_source)

# this works: export as txt
exporter_combobutton = driver.find_element(By.ID, "dijit_form_ComboButton_1_button")
exporter_combobutton.click()

arrow_to_acces_export = driver.find_element(By.ID, "dijit_form_ComboButton_1_arrow")
arrow_to_acces_export.click()

with open("D:\\temp\\after_arrow_to_acces_export_click.txt", "w", encoding="utf-8") as text_dump_file:
    text_dump_file.write(driver.page_source)

excel_export_button = driver.find_element(By.XPATH, "//td[contains(text(),'Exporter vers un tableur Excel')]")
excel_export_button.click()


export_button_by_id = driver.find_element(By.ID, "dijit_form_ComboButton_1_label")
export_button_by_id.click()

excel_export_button_by_id = driver.find_element(By.ID, "dijit_MenuItem_42_text")
excel_export_button_by_id.click()

export_button_by_text = driver.find_element(By.XPATH, "//td[contains(text(),'Exporter')]")

page_html = driver.page_source
with open("D:\\temp\\text_dump_file.txt", "w", encoding="utf-8") as text_dump_file:
    text_dump_file.write(page_html)
