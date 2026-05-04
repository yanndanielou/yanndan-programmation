import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =========================
# CONFIGURATION
# =========================
URL = "https://champweb.siemens.net/..."  # URL ClearQuest
EXCEL_FILE = "data.xlsx"
BROWSER = "edge"  # "edge" ou "chrome"

# =========================
# CHARGEMENT EXCEL
# =========================
df = pd.read_excel(EXCEL_FILE)
row = df.iloc[0]  # 1ère ligne de données

# =========================
# LANCEMENT NAVIGATEUR
# =========================
if BROWSER.lower() == "chrome":
    driver = webdriver.Chrome()
else:
    driver = webdriver.Edge()

wait = WebDriverWait(driver, 20)
driver.get(URL)

# =========================
# OPTIONNEL : LOGIN
# =========================
# wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("login")
# driver.find_element(By.ID, "password").send_keys("password")
# driver.find_element(By.ID, "loginButton").click()

# =========================
# ATTENTE ONGLET MAIN
# =========================
wait.until(EC.presence_of_element_located((By.ID, "Main")))
driver.find_element(By.ID, "Main").click()

# =========================
# REMPLISSAGE DES CHAMPS
# =========================
for field_name, field_value in row.items():

    if pd.isna(field_value):
        continue

    try:
        element = wait.until(EC.presence_of_element_located((By.NAME, field_name)))  # ou By.ID

        tag = element.tag_name.lower()

        if tag == "input":
            element.clear()
            element.send_keys(str(field_value))

        elif tag == "textarea":
            element.clear()
            element.send_keys(str(field_value))

        elif tag == "select":
            from selenium.webdriver.support.ui import Select

            Select(element).select_by_visible_text(str(field_value))

        else:
            print(f"Type de champ non géré : {field_name}")

        print(f"✔ Champ rempli : {field_name}")

    except Exception as e:
        print(f"❌ Champ introuvable : {field_name} ({e})")

# =========================
# FIN
# =========================
time.sleep(2)
# driver.quit()
