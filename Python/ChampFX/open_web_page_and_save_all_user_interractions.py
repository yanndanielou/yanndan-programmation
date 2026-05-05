from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from pynput import mouse, keyboard
import json

# Chemin vers le fichier de log des actions.
LOG_FILE = "actions_log.json"
actions = []

# Ouvrir le navigateur (Chrome Driver recommandé ici).
driver = webdriver.Chrome()
# driver.get("https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX?format=HTML&loginId=AD001%5Cfr232487&password=AntoineMoka1.")  # Remplace par l'URL souhaitée.
driver.get(
    "https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/RECORD?format=HTML&recordType=CFXRequest&fieldsXml=&autoSave=false&noframes=true&loginId=AD001%5Cfr232487&password=AntoineMoka1."
)  # Remplace par l'URL souhaitée.
action_chain = ActionChains(driver)


def save_to_log(action_type, details):
    """Enregistrer une action (clic ou saisie clavier) avec les sélecteurs des éléments."""
    actions.append({"action_type": action_type, "details": details})
    with open(LOG_FILE, "w") as log_file:
        json.dump(actions, log_file, indent=4)


def get_element_selector(element):
    """Extraire un sélecteur descriptif d'un élément HTML."""
    selector = {}
    if element.get_attribute("id"):
        selector["id"] = element.get_attribute("id")
    if element.get_attribute("name"):
        selector["name"] = element.get_attribute("name")
    if element.get_attribute("class"):
        selector["class"] = element.get_attribute("class")
    selector["tag_name"] = element.tag_name
    return selector


def record_click(element):
    """Enregistrer un clic sur un élément."""
    selector = get_element_selector(element)
    save_to_log("click", {"selector": selector})


def record_keyboard(element, key):
    """Enregistrer une action clavier dans un champ."""
    selector = get_element_selector(element)
    save_to_log("keyboard_input", {"selector": selector, "key": key})


# Moniteur de clics
def monitor_clicks():
    while True:
        active_element = driver.switch_to.active_element
        input("Cliquez sur un élément ou tapez Entrée pour stopper l'enregistrement.")
        record_click(active_element)


# Moniteur de clavier
def monitor_typings():
    while True:
        active_element = driver.switch_to.active_element
        key = input("Tapez et appuyez `Entrée` pour chaque touche à enregistrer.")
        record_keyboard(active_element, key)


# Démarrage des enregistrements
print("L'enregistrement commence. Ouvrez le navigateur et interagissez avec la page.")
while True:
    try:
        action = input("Tapez 'clic' pour enregistrer un clic ou 'clavier' pour du texte (CTRL+C pour quitter) : ").strip().lower()
        if action == "clic":
            monitor_clicks()
        elif action == "clavier":
            monitor_typings()
    except KeyboardInterrupt:
        print("\nEnregistrement terminé. Les actions sont sauvegardées dans", LOG_FILE)
