from champfx import application


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CREATE_CFX_URL = "https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/RECORD?format=HTML&recordType=CFXRequest&fieldsXml=&autoSave=false&noframes=true"


class CreateChampFXApplication(application.ChampFxApplicationBase):

    def fill_input(self, element_id: str, value: str) -> None:
        el = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, element_id)))
        el.clear()
        el.send_keys(value)

    def click_element(self, element_id: str) -> None:
        el = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, element_id)))
        el.click()

    def run(self) -> None:
        self.create_webdriver_and_login()
        self.driver.maximize_window()

        self.driver.get(CREATE_CFX_URL)
        wait = WebDriverWait(self.driver, 10)

        # Search panel
        self.fill_input("cqFindRecordString", "exemple")
        self.click_element("searchById")

        # Main record form
        self.fill_input("widget_cq_widget_CqTextBox_0", "Titre de la demandeaaaa")
        self.fill_input("cq_widget_CqTextBox_0", "Titre de la demande")

        self.fill_input("cq_widget_CqFilteringSelect_0", "Projet Exemple")
        self.fill_input("cq_widget_CqFilteringSelect_1", "Type de requête Exemple")
        self.fill_input("cq_widget_CqFilteringSelect_2", "Catégorie Exemple")

        self.fill_input("cq_widget_CqEditableCombo_0", "Valeur combo 1")
        self.fill_input("cq_widget_CqEditableCombo_1", "Valeur combo 2")
        self.fill_input("cq_widget_CqEditableCombo_2", "Valeur combo 3")

        self.fill_input("cq_widget_CqTextArea_0", "Voici la description de l'élément.")
        self.fill_input("cq_widget_CqTextArea_1", "Informations sur l'environnement.")

        self.fill_input("cq_widget_CqEditableCombo_3", "Propriétaire suivant")
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
