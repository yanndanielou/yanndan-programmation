from champfx import application, constants

from logger import logger_config

from selenium.webdriver.support.ui import WebDriverWait, Select


import pandas as pd


from dataclasses import dataclass


from typing import Optional
from enum import Enum


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CREATE_CFX_URL = "https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/RECORD?format=HTML&recordType=CFXRequest&fieldsXml=&autoSave=false&noframes=true"


@dataclass
class CreateChampFxData:
    headline: str
    project_name: str
    request_type: constants.RequestType
    category: constants.Category
    severity: constants.Severity
    system_structure_part_1: str
    system_structure_part_2: str
    system_structure_part_3: str
    description: str
    current_owner: str
    environment_type: constants.EnvironmentType
    detected_in_phase: constants.DetectedInPhase
    safety_relevant: Optional[constants.SafetyRelevant] = None
    security_relevant: Optional[constants.SecurityRelevant] = None
    doc_id: Optional[str] = None
    doc_ver: Optional[str] = None
    documentation_reference: Optional[str] = None


class CreateChampFXApplication(application.ChampFxApplicationBase):

    def fill_input_with_optional_enum_value(self, element_id: str, value: Optional[Enum]) -> None:
        if value is not None:
            el = self.driver.find_element(By.ID, element_id)
            el.clear()
            el.send_keys(value.value)

    def fill_input(self, element_id: str, value: Optional[str]) -> None:
        if value is not None:
            el = self.driver.find_element(By.ID, element_id)
            el.clear()
            el.send_keys(value)

    def click_element(self, element_id: str) -> None:
        el = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, element_id)))
        el.click()

    def init(self) -> None:
        self.create_webdriver_and_login()
        self.driver.maximize_window()

    def export_all_current_fields(self) -> None:
        fields = self.driver.find_elements(By.XPATH, "//input | //textarea | //select")

        logger_config.print_and_log_info(f"Champs trouvés : {len(fields)}")

        for i, field in enumerate(fields, start=1):

            def get_label(field_id: str) -> str:
                # ---------- LABEL ----------
                label_text = ""
                if field_id:
                    labels = self.driver.find_elements(By.XPATH, f"//label[@for='{field_id}']")
                    if labels:
                        label_text = labels[0].text.strip()
                return label_text

            field_description = {
                "tag": field.tag_name.lower(),
                "type": field.get_attribute("type"),
                "text": field.get_attribute("text"),
                "id": field.get_attribute("id"),
                "name": field.get_attribute("name"),
                "label": get_label(field_id=field.get_attribute("id")),
                "enabled": field.is_enabled(),
            }

            # ---------- COMBOBOX ----------
            if field.tag_name.lower() == "select":
                select = Select(field)
                logger_config.print_and_log_info("Valeurs possibles :")
                for opt in select.options:
                    logger_config.print_and_log_info(f"  - {opt.text.strip()}")
                field_description["Possible values"] = ",".join([opt.text.strip() for opt in select.options])

            logger_config.print_and_log_info(f"field {i} : {field_description}")

    def create_champfx(self, cfx_data: CreateChampFxData) -> None:
        self.driver.get(CREATE_CFX_URL)
        wait = WebDriverWait(self.driver, 30)

        self.export_all_current_fields()

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

        self.fill_input_with_optional_enum_value("cq_widget_CqFilteringSelect_3", cfx_data.safety_relevant)
        self.fill_input_with_optional_enum_value("cq_widget_CqFilteringSelect_25", cfx_data.security_relevant)

        self.fill_input("cq_widget_CqFilteringSelect_4", cfx_data.severity.value)
        self.fill_input("cq_widget_CqFilteringSelect_5", cfx_data.detected_in_phase.value)
        self.fill_input("cq_widget_CqFilteringSelect_6", cfx_data.environment_type.value)

        # self.fill_input("cq_widget_CqTextBox_1", "ID secondaire")
        # self.fill_input("cq_widget_CqTextBox_2", "ID client")
        self.fill_input("cq_widget_CqTextBox_3", cfx_data.doc_id)
        self.fill_input("cq_widget_CqTextBox_4", cfx_data.doc_ver)
        self.fill_input("cq_widget_CqTextBox_5", cfx_data.documentation_reference)

        # self.fill_input("cq_widget_CqEditableCombo_4", "boolean")

        # NCC/NCR Checkbox
        # checkbox = wait.until(EC.element_to_be_clickable((By.ID, "cq_widget_CqCheckBox_0")))
        # if not checkbox.is_selected():
        #    checkbox.click()

        # Si vous voulez sauvegarder
        self.click_element("dijit_form_Button_26")

        # Fin
        # driver.quit()
