from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from pynput import mouse, keyboard
from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button
from typing import Dict, List, Any
import json
import win32gui
from datetime import datetime


def is_browser_focused() -> bool:
    """Vérifie si la fenêtre du navigateur a le focus."""
    hwnd = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(hwnd)
    return "01_CHAMP" in title


# Chemin vers le fichier de log des actions.
LOG_FILE: str = "actions_log.json"
actions: List[Dict[str, Any]] = []
typing_buffer: str = ""

# Ouvrir le navigateur (Chrome Driver recommandé ici).
driver = webdriver.Chrome()
driver.get(
    "https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/RECORD?format=HTML&recordType=CFXRequest&fieldsXml=&autoSave=false&noframes=true&loginId=AD001%5Cfr232487&password=AntoineMoka1."
)  # Remplace par l'URL souhaitée.


def save_to_log(action_type: str, details: Dict[str, Any]) -> None:
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


def get_element_selector(element: WebElement) -> Dict[str, str]:
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


def record_click(element: WebElement) -> None:
    """Enregistrer un clic sur un élément."""
    selector = get_element_selector(element)
    save_to_log("click", {"selector": selector})


def record_keyboard(element: WebElement, key: str) -> None:
    """Enregistrer une action clavier dans un champ."""
    selector = get_element_selector(element)
    save_to_log("keyboard_input", {"selector": selector, "key": key})


def on_click(x: int, y: int, button: Button, pressed: bool) -> None:
    """Gestionnaire pour les clics de souris."""
    global typing_buffer
    if pressed and is_browser_focused():
        try:
            active_element = driver.switch_to.active_element
            record_click(active_element)
            typing_buffer = ""  # Clear buffer on click
        except Exception as e:
            print(f"Erreur lors de l'enregistrement du clic: {e}")


def on_press(key: Any) -> None:
    """Gestionnaire pour les pressions de clavier."""
    global typing_buffer
    if is_browser_focused():
        if hasattr(key, "char") and key.char:
            typing_buffer += key.char
        elif key in (Key.enter, Key.tab, Key.esc):
            if typing_buffer:
                try:
                    active_element = driver.switch_to.active_element
                    record_keyboard(active_element, typing_buffer)
                    typing_buffer = ""
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
