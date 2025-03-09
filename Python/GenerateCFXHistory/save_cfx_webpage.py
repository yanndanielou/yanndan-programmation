from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Path to the ChromeDriver
chrome_driver_path = "C:\\Users\\fr232487\\Downloads\\chromedriver-win64\\chromedriver.exe"

# URL of the web page you want to save
url = "https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/RECORD/CFX00393065?format=HTML&loginId=AD001%5Cfr232487&password=Zzeerrttyy9.&noframes=true"

# Set up the Chrome options
chrome_options = Options()
chrome_options.add_experimental_option(
    "prefs",
    {
        "download.default_directory": "/path/to/download/directory",
        "savefile.default_directory": "/path/to/save/directory",
    },


# Create a new instance of the Chrome driver
driver_service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=driver_service, options=chrome_options)

try:
    driver.get(url)
    time.sleep(5)  # Wait for the page to load completely

    # Locate the "History" tab using its unique attributes and click it
    history_tab = driver.find_element(By.XPATH, "//span[@data-dojo-attach-point='containerNode,focusNode' and text()='History']")
    history_tab.click()

    page_html = driver.page_source
    
    extended_history_div = driver.find_element(By.XPATH, "//div[@id='cq_widget_CqReadonlyTextArea_4']")
    extended_history_text = extended_history_div.text


    # Define a regular expression pattern to extract content between "====START====" and "====END===="
    pattern = r'====START====(.*?)====END===='

    # Use re.findall to extract all matching content
    history_entries = re.findall(pattern, div_content, re.DOTALL)

    # Create a history object
    history = {"entries": history_entries}

    # Simulate Ctrl+S to open "Save As" dialog
    driver.execute_script("window.print();")  # Print invokes the Save Page As dialog in some configurations
    

    # Pause for a realistic delay if needed to manually complete the save, if auto-save not configured
    time.sleep(5)

finally:
    driver.quit()
