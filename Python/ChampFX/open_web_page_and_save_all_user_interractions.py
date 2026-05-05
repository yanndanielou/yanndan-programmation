from selenium import webdriver
from datetime import datetime
from pynput import mouse, keyboard
import json
import win32gui


def is_browser_focused() -> bool:
    """Vérifie si la fenêtre du navigateur a le focus."""
    hwnd = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(hwnd)
    return "01_CHAMP" in title


# Chemin vers le fichier de log des actions.
LOG_FILE = "actions_log.json"
actions = []

# Ouvrir le navigateur (Chrome Driver recommandé ici).
driver = webdriver.Chrome()
driver.get(
    "https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/RECORD?format=HTML&recordType=CFXRequest&fieldsXml=&autoSave=false&noframes=true&loginId=AD001%5Cfr232487&password=AntoineMoka1."
)  # Remplace par l'URL souhaitée.


def save_to_log(action_type, details):
    """Enregistrer une action (clic ou saisie clavier) avec les sélecteurs des éléments."""
    actions.append(
        {
            "timestamp": str(datetime.now()),
            "action_type": action_type,
            "details": details,
        }
    )
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


def on_click(x, y, button, pressed):
    """Gestionnaire pour les clics de souris."""
    if pressed and is_browser_focused():
        try:
            active_element = driver.switch_to.active_element
            record_click(active_element)
        except Exception as e:
            print(f"Erreur lors de l'enregistrement du clic: {e}")


def on_press(key):
    """Gestionnaire pour les pressions de clavier."""
    if is_browser_focused():
        try:
            active_element = driver.switch_to.active_element
            if hasattr(key, "char") and key.char:
                record_keyboard(active_element, key.char)
        except Exception as e:
            print(f"Erreur lors de l'enregistrement de la saisie clavier: {e}")


# Démarrage des enregistrements
print("L'enregistrement commence. Ouvrez le navigateur et interagissez avec la page. Appuyez sur Ctrl+C pour arrêter.")

try:
    with mouse.Listener(on_click=on_click) as mouse_listener, keyboard.Listener(on_press=on_press) as keyboard_listener:
        mouse_listener.join()
        keyboard_listener.join()
except KeyboardInterrupt:
    print("\nEnregistrement terminé. Les actions sont sauvegardées dans", LOG_FILE)
finally:
    driver.quit()
