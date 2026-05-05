from champfx import application

from dataclasses import dataclass

from enum import Enum


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CREATE_CFX_URL = "https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/RECORD?format=HTML&recordType=CFXRequest&fieldsXml=&autoSave=false&noframes=true"


class RequestType(Enum):
    CHANGE_REQUEST_EXTERNAL = "Change Request, external"
    DEFECT = "Defect"
    CHANGE_REQUEST_INTERNAL = "Change Request, internal"
    DEVELOPMENT_REQUEST = "Development Request"
    HAZARD = "Hazard"
    ACTION_ITEM = "Action Item"
    OPEN_POINT = "Open Point"


class Category(Enum):
    SYSTEM = "System"
    SOFTWARE = "Software"
    HARDWARE = "Hardware"
    DOCUMENTATION = "Documentation"
    CONFIGURATION_DATA = "Configuration Data"


@dataclass
class CreateChampFxData:
    headline: str
    project_name: str
    request_type: RequestType
    category: Category
    system_structure_part_1: str
    system_structure_part_2: str
    system_structure_part_3: str
    description: str
    current_owner: str


class CreateChampFXApplication(application.ChampFxApplicationBase):

    def fill_input(self, element_id: str, value: str) -> None:
        el = self.driver.find_element(By.ID, element_id)
        el.clear()
        el.send_keys(value)

    def click_element(self, element_id: str) -> None:
        el = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, element_id)))
        el.click()

    def init(self) -> None:
        self.create_webdriver_and_login()
        self.driver.maximize_window()

    def create_champfx(self, cfx_data: CreateChampFxData) -> None:
        self.driver.get(CREATE_CFX_URL)
        wait = WebDriverWait(self.driver, 30)

        # Main record form
        self.fill_input("cq_widget_CqTextBox_0", cfx_data.headline)

        self.fill_input("cq_widget_CqFilteringSelect_0", cfx_data.project_name)
        self.fill_input("cq_widget_CqFilteringSelect_1", cfx_data.request_type.value)
        self.fill_input("cq_widget_CqFilteringSelect_2", cfx_data.category.value)

        self.fill_input("cq_widget_CqEditableCombo_0", cfx_data.system_structure_part_1)
        self.fill_input("cq_widget_CqEditableCombo_1", cfx_data.system_structure_part_2)
        self.fill_input("cq_widget_CqEditableCombo_2", cfx_data.system_structure_part_3)

        self.fill_input("cq_widget_CqTextArea_0", cfx_data.description)
        # self.fill_input("cq_widget_CqTextArea_1", "Informations sur l'environnement.")

        self.fill_input("cq_widget_CqEditableCombo_3", cfx_data.current_owner)
        self.fill_input("cq_widget_CqFilteringSelect_3", "Oui")
        self.fill_input("cq_widget_CqFilteringSelect_4", "Majeur")
        self.fill_input("cq_widget_CqFilteringSelect_5", "Phase de détection Exemple")
        self.fill_input("cq_widget_CqFilteringSelect_6", "Type d'environnement Exemple")

        self.fill_input("cq_widget_CqTextBox_1", "ID secondaire")
        self.fill_input("cq_widget_CqTextBox_2", "ID client")
        self.fill_input("cq_widget_CqTextBox_3", "DOC-12345")
        self.fill_input("cq_widget_CqTextBox_4", "1.0")
        self.fill_input("cq_widget_CqTextBox_5", "Référence documentaire")

        self.fill_input("cq_widget_CqEditableCombo_4", "CCB Exemple")

        # Checkbox
        checkbox = wait.until(EC.element_to_be_clickable((By.ID, "cq_widget_CqCheckBox_0")))
        if not checkbox.is_selected():
            checkbox.click()

        # Si vous voulez sauvegarder
        self.click_element("dijit_form_Button_26")

        # Fin
        # driver.quit()
