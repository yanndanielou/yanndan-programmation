from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

# Path to the ChromeDriver
chrome_driver_path = "C:\\Users\\fr232487\\Downloads\\chromedriver-win64\\chromedriver.exe"

# URL of the web page you want to save
url = "https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/RECORD/CFX00393065?format=HTML&loginId=AD001%5Cfr232487&password=Zzeerrttyy9.&noframes=true"

# Set up the Chrome options
chrome_options = Options()

# Create a new instance of the Chrome driver
driver_service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=driver_service, options=chrome_options)

try:

    page_html_content_depending = dict()

    driver.get(url)

    max_delay = 50

    for i in range(1, max_delay):
        time.sleep(1)  # Wait for the page to load completely
        print(i)
        page_html = driver.page_source
        page_html_content_depending[i] = page_html

        with open(f"text_dump_file_{i}.txt", "w", encoding="utf-8") as text_dump_file:
            text_dump_file.write(page_html)

    # print(page_html)

    # Locate the "History" tab using its unique attributes and click it
    history_tab = driver.find_element(By.XPATH, "//span[@data-dojo-attach-point='containerNode,focusNode' and text()='History']")
    history_tab.click()

    extended_history_div = driver.find_element(By.XPATH, "//div[@id='cq_widget_CqReadonlyTextArea_4']")
    extended_history_text = extended_history_div.text

    # Define a regular expression pattern to extract content between "====START====" and "====END===="
    one_history_start_and_end_pattern = r"====START====(.*?)====END===="

    # Use re.findall to extract all matching content
    history_entries = re.findall(one_history_start_and_end_pattern, extended_history_text, re.DOTALL)

    print(history_entries)

    # Create a history object
    history = {"entries": history_entries}

    # Simulate Ctrl+S to open "Save As" dialog
    driver.execute_script("window.print();")  # Print invokes the Save Page As dialog in some configurations

    # Pause for a realistic delay if needed to manually complete the save, if auto-save not configured
    time.sleep(5)

finally:
    driver.quit()
