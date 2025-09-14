# Standard

import inspect
import logging
import os
import threading
import time
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Set

from common import download_utils, file_utils, web_driver_utils

# Other libraries
from logger import logger_config

# Third Party
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

# Current programm
import connexion_param

CFX_FILES_DOWNLOADED_PATTERN_WITHOUT_EXTENSION = "QueryResult*"

DOWNLOADED_FILES_FINAL_DIRECTORY = "Input"
OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME = "output_save_cfx_request_results"

DEFAULT_DOWNLOAD_DIRECTORY = os.path.expandvars(r"%userprofile%\downloads")

CREATE_PARSED_EXTENDED_HISTORY_FILES = False

CREATE_PARSED_CURRENT_OWNNER_MODIFICATIONS_JSON_FILES = False

DEFAULT_DO_NOT_OPEN_WEBSITE_AND_TREAT_PREVIOUS_RESULTS = False
# DEFAULT_DO_NOT_OPEN_WEBSITE_AND_TREAT_PREVIOUS_RESULTS = True

DEFAULT_NUMBER_OF_THREADS = 2

PROJECT_MANUAL_SELECTION_DETAIL_QUERY_ID = 66977872
PROJECT_MANUAL_SELECTION_CHANGE_STATE_QUERY_ID = 66875867
NEXT_ATS_EXTENDED_HISTORY_QUERY_ID = 65753660
NEXT_ATS_CMC_QUERY_ID = 63323368

EXCEL_FILE_EXTENSION = ".xlsx"
TEXT_FILE_EXTENSION = ".txt"


class FilterFieldType(Enum):
    EQUAL_TO = "Egal à"
    DIFFERENT_TO = "Différent de"


class QueryOutputFileType(Enum):
    EXCEL_EXPORT = auto()
    TXT_EXPORT = auto()

    def get_file_extension(self) -> str:
        return TEXT_FILE_EXTENSION if self == QueryOutputFileType.TXT_EXPORT else EXCEL_FILE_EXTENSION

    def get_file_download_dropdown_menu_option_text(self) -> str:
        return "Exporter vers un fichier texte" if self == QueryOutputFileType.TXT_EXPORT else "Exporter vers un tableur Excel"


@dataclass
class ProjectsFieldFilter:
    projects_names: Set[str] | List[str]
    filter_type: FilterFieldType


@dataclass
class CfxQuery:
    output_file_name_without_extension: str
    query_id: int
    output_file_type: QueryOutputFileType
    projects_field_filters: Optional[ProjectsFieldFilter] = None
    label: str = ""

    def __post_init__(self) -> None:
        if self.label is None:
            self.label = self.output_file_name_without_extension


BIGGEST_PROJECTS_NAMES: List[str] = [
    "SA_RMP_COM",
    "SA_RMP_REL",
    "ESBO",
    "SA_RMP_SIG_Site",
    "TrashCan",
    "DK_S-bane",
    "Cargo",
    "Sicas Tools",
    "Op_LT_D_901",
    "Simis_Basis",
    "OC501",
    "OC100",
    "ESF",
    "TGMT R3",
    "AU_BHPBIO",
    "GB_Crossrail_CRL",
    "Simis_W_Basis",
    "TGMT R1",
    "BE_ETCS_L2_IXL_RO",
    "LZB80E - LZB-STM",
    "EPOS",
    "Entegro",
    "Controlguide",
    "ATSP",
    "FI_ESKO",
    "US_NYCT_CBTC-Queens-Blvd_61OP-00025",
    "NL_EBS_PLUS",
    "TGMT R2",
    "PTC_OBU",
    "FR_CS_Op_and_Maint",
    "ML_Projektierungstools",
    "ES_AVE_S10x",
    "LT_Siauliai_Klaipeda",
    "HK_Signalling_SCL",
    "BE_ETCS_L2_IXL",
    "TCR3_CBTC",
    "CH_CHP_ETCS",
    "GCP5000",
    "FR_PAR4",
    "US_PATH_CBTC-Phase2-STS-F_61OP-70051",
    "iVIU_PTC_Console",
    "MY_KVLRT3-SIG",
    "LZB8016",
    "SA_RMP_CIS",
    "SA_RMP_SIG",
    "FR_PL14",
    "NO_NOR_TRA",
    "Stage",
    "SA_RMP_PSD",
    "STAC",
    "Engineering_Tools",
    "BAI",
    "DE_FPTS",
    "Simis_W_Logic_International",
    "IN_CMRP1",
    "FR_NEXTEO",
    "PTC_BOS",
    "NL_HSL_Zuid",
    "SA_RMP_RST",
    "FR_POUR_Ouragan",
    "Guide",
    "US_MTA_PTC-LIRR-MNR_61OP-70027_70028",
    "SA_RMP_SYS",
    "BE_Corridor_C",
    "UK_Freight",
    "Airlink",
    "DE-Vectron-Rahmenvertrag",
    "Tesys",
    "Simis_W_GB_Applications",
    "FR_PAR1_Paris_Line_1",
    "SG_Jurong_Line",
    "CH-ETCS_zweite_Welle",
    "FR_PATH",
    "PT_ML",
    "DiB_LT_iBS",
    "MX_Metro_Mexico_Line_1",
    "FR_SPL4_Sao_Paulo_L4",
    "BE_DML_AM08_ETCS",
    "CN_JJ-Line",
    "FR_REB_CityVAL_RENNES_LineB",
    "TCS Odometrie",
    "DK_S-bane_TMS_Int",
    "BR_SMB",
    "Sicas SU",
    "BG_SML3",
    "RM_RA",
    "GR_Attiko_Ext_Ph_B",
    "NO_Resignalling_Oslo_Sporveien_Metro",
    "US_SEPTA_ATC-ACSES_61OP-00040",
    "FR_HKL1_Helsinki",
    "BHP",
    "HU_FEFE",
    "Sicas Silogik",
    "DCR",
    "AGenDA",
    "TGMTZUB",
    "UK_DesiroCity_ETCS",
    "CN_BJL10P2",
    "DiB_LT_iUZ",
    "EE_Estonian_Railways_CCS",
    "DS3",
    "Zub_242t_ZBS",
    "AT_FFU5",
    "FR_BUD2_Budapest_M2",
    "AU_Goonyella_ETCS_L2",
    "HU_KLBA",
    "CommsManager",
    "Simis FM Basis",
    "SIMIS LC",
    "GCP_CPU3",
    "FR_FPT3",
    "FR_BUM4_Budapest_M4",
    "TW_TTY-Extension",
    "EG_Benha-Port_Said",
    "Crossrail_ATS",
    "GEN_OBU",
    "CA_OTLE",
    "FR_BKK_APM",
    "FR_BAC9_Barcelone_L9",
    "ZA_PRASA_S1",
    "PT_Entroncamento_Statio",
    "WaysideInspector",
    "HU_FEGY",
    "US_NYCT_CBTC-8th-Avenue_61OP-00188",
    "CH_GEN",
    "DE_ICx_ETCS_L2_DB-AG",
    "STM_DK",
    "Op_LT_D_Proj",
    "UK_DCM",
    "EurosuiteDAT",
    "WT_Templates_ER",
    "WT_Templates_SSC3.1",
    "MX_MTY_L3",
    "CH_EC250",
    "GUIDO",
    "US_NYCT_CBTC-Culver-Line_61OP-00155",
    "AR_BALH_ExtLs",
    "CHAMP",
    "CN_GMCL5",
    "PEACCplus",
    "ID_JBDB",
    "US_LIRR_ATC-M9_61OP-70024",
    "OLD_ML_GnatsMigration",
    "SIMIS PC",
    "CN_JJDPL",
    "XT_CONFIGURATION_TOOLS",
    "FR_GPE1567",
    "Zub_222t",
    "DMI",
    "CN_SZL4_NE",
    "NO_DRM",
    "CN_SUZL5",
    "DE_ETCS_L2_Ländereintritt_D",
    "HU_BAAB",
    "DE 00878 Tra000 Produkt",
    "PT_Lote_A_Portugal",
    "Westrace_Tools",
    "CDB",
    "AC_100",
    "SICAS S7",
    "GCP4000",
    "H-Bahn",
    "US_CTA_5000",
    "GEO2",
    "CG_ISM_100",
    "TGBI",
    "AU_WESTCAD",
    "Vicos_T&S_TGMT",
    "XT_ODO",
    "TR_Izmir_Metro_Signaliz",
    "NO_OSL47",
    "Simis_W_BE",
    "IN_NGP",
    "CN_BJL8P2",
    "TW_Taiwan_68_Stations",
    "DiagnosticTerminal",
    "IN_MMOPL",
    "AU_MO_QM_System",
    "GEMMI",
    "CN_SUZL2",
    "SY_CFS_Contracts_27-28",
    "AT_DesiroML_OEBB_cityjet",
    "Contribution_Process_FR",
    "Simis_W_DE",
    "TCRD_CBTC",
    "IN_RMGL",
    "DE-Velaro_D_MS_BR407_ETCS_OBU",
    "TH_MRT_Blue_Line_Ext",
    "CN_Nanjing_L10",
    "BE_PreMetro_Antwerp_IXL",
    "CoreShield_S2L2_Linux",
    "IN_Bangalore_Metro_Rail",
    "NO_SNO",
    "CN_CQL6",
    "DE_VGF_DTC",
    "Simis_W_NOR",
    "BR_Sao_Paulo_L6",
    "XT_MULTIPROJET_TRANSPORT_FR",
    "CN_XAL3P1",
    "CN_GZL1R",
    "US_CSX_Trainguard-PTC-OBU_61OP-70022",
    "Falko",
    "CN_CQL1",
    "NO_DRM47",
    "FR_NYCV_CULVER",
    "KR_SSWS",
    "ES_Rodalies_R4_BCN",
    "WCCT",
]

INTERESTED_IN_PROJECTS_NAMES: List[str] = ["FR_NEXTEO", "ATSP"]


@contextmanager
def stopwatch_with_label_and_surround_with_screenshots(label: str, remote_web_driver: ChromiumDriver, screenshots_directory_path: str) -> Generator[float, None, None]:
    """Décorateur de contexte pour mesurer le temps d'exécution d'une fonction :
    https://www.docstring.fr/glossaire/with/"""
    remote_web_driver.get_screenshot_as_file(f"{screenshots_directory_path}/before {label}.png")

    previous_stack = inspect.stack(0)[2]
    file_name = previous_stack.filename
    line_number = previous_stack.lineno
    calling_file_name_and_line_number = file_name + ":" + str(line_number)

    to_print_and_log = f"{label} begin"
    # pylint: disable=line-too-long
    log_timestamp = time.asctime(time.localtime(time.time()))

    print(log_timestamp + "\t" + calling_file_name_and_line_number + "\t" + to_print_and_log)
    logging.info(f"{calling_file_name_and_line_number} \t {to_print_and_log}")  # pylint: disable=logging-fstring-interpolation

    debut = time.perf_counter()
    yield time.perf_counter() - debut
    fin = time.perf_counter()
    remote_web_driver.get_screenshot_as_file(f"{screenshots_directory_path}/after {label}.png")

    duree = fin - debut
    to_print_and_log = f"{label} Elapsed: {duree:.2f} seconds"

    log_timestamp = time.asctime(time.localtime(time.time()))

    # pylint: disable=line-too-long
    print(log_timestamp + "\t" + calling_file_name_and_line_number + "\t" + to_print_and_log)

    logging.info(f"{calling_file_name_and_line_number} \t {to_print_and_log}")  # pylint: disable=logging-fstring-interpolation


@contextmanager
def surround_with_screenshots(label: str, remote_web_driver: ChromiumDriver, screenshots_directory_path: str) -> Generator[float, None, None]:
    remote_web_driver.get_screenshot_as_file(f"{screenshots_directory_path}/before {label}.png")
    yield 0.0
    remote_web_driver.get_screenshot_as_file(f"{screenshots_directory_path}/after {label}.png")


@dataclass
class SaveCfxRequestMultipagesResultsApplication:
    projects_to_handle_list: List[str]
    output_parent_directory_name: str = OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME
    output_downloaded_files_final_directory_path: str = DOWNLOADED_FILES_FINAL_DIRECTORY
    web_browser_download_directory = DEFAULT_DOWNLOAD_DIRECTORY
    headless: bool = False  # <--- Add this option

    errors_output_sub_directory_name = "errors"
    screenshots_output_sub_directory_name = "screenshots"
    driver: ChromiumDriver = field(init=False)

    def __post_init__(self) -> None:
        self.lock = threading.Lock()
        self.errors_output_relative_path = f"{self.output_parent_directory_name}/{self.errors_output_sub_directory_name}"
        self.screenshots_output_relative_path = f"{self.output_parent_directory_name}/{self.screenshots_output_sub_directory_name}"
        self.number_of_exceptions_caught = 0

    @contextmanager
    def stopwatch_with_label_and_surround_with_screenshots(self, label: str) -> Generator[float, None, None]:
        """Décorateur de contexte pour mesurer le temps d'exécution d'une fonction :
        https://www.docstring.fr/glossaire/with/"""
        self.driver.get_screenshot_as_file(f"{self.screenshots_output_relative_path}/before {label}.png")
        debut = time.perf_counter()
        yield time.perf_counter() - debut
        fin = time.perf_counter()
        self.driver.get_screenshot_as_file(f"{self.screenshots_output_relative_path}/after {label}.png")

        duree = fin - debut
        to_print_and_log = f"{label} Elapsed: {duree:.2f} seconds"

        log_timestamp = time.asctime(time.localtime(time.time()))

        previous_stack = inspect.stack(0)[2]
        file_name = previous_stack.filename
        line_number = previous_stack.lineno
        calling_file_name_and_line_number = file_name + ":" + str(line_number)

        # pylint: disable=line-too-long
        print(log_timestamp + "\t" + calling_file_name_and_line_number + "\t" + to_print_and_log)

        logging.info(f"{calling_file_name_and_line_number} \t {to_print_and_log}")  # pylint: disable=logging-fstring-interpolation

    def run(self) -> None:

        for directory_path in [self.output_parent_directory_name, self.errors_output_relative_path, self.screenshots_output_relative_path, self.output_downloaded_files_final_directory_path]:
            file_utils.create_folder_if_not_exist(directory_path)

        self.create_webdriver_and_login()

        self.generate_and_download_query_results_for_project_filters(
            change_state_cfx_query=CfxQuery(
                query_id=NEXT_ATS_CMC_QUERY_ID,
                output_file_name_without_extension="nextatsp_CMC",
                output_file_type=QueryOutputFileType.EXCEL_EXPORT,
            )
        )

        self.generate_and_download_query_results_for_project_filters(
            change_state_cfx_query=CfxQuery(
                query_id=NEXT_ATS_EXTENDED_HISTORY_QUERY_ID,
                output_file_name_without_extension="extended_history_nextats",
                output_file_type=QueryOutputFileType.TXT_EXPORT,
            )
        )

        for project_name in self.projects_to_handle_list:
            projects_field_filter = ProjectsFieldFilter(projects_names=[project_name], filter_type=FilterFieldType.EQUAL_TO)
            change_state_cfx_query = CfxQuery(
                projects_field_filters=projects_field_filter,
                query_id=PROJECT_MANUAL_SELECTION_CHANGE_STATE_QUERY_ID,
                output_file_name_without_extension=f"states_changes_project_{project_name}",
                label=project_name,
                output_file_type=QueryOutputFileType.EXCEL_EXPORT,
            )
            extended_history_cfx_query = CfxQuery(
                projects_field_filters=projects_field_filter,
                query_id=PROJECT_MANUAL_SELECTION_DETAIL_QUERY_ID,
                output_file_name_without_extension=f"details_project_{project_name}",
                label=project_name,
                output_file_type=QueryOutputFileType.EXCEL_EXPORT,
            )
            logger_config.print_and_log_info(f"Handling project {project_name}")
            with logger_config.stopwatch_with_label(
                f"generate_and_dowload_query_for_project:{project_name} {change_state_cfx_query.label} {change_state_cfx_query.output_file_name_without_extension}"
            ):
                self.generate_and_download_query_results_for_project_filters(change_state_cfx_query=change_state_cfx_query)
            logger_config.print_and_log_info(f"Handling project {project_name}")
            with logger_config.stopwatch_with_label(
                f"generate_and_dowload_query_for_project:{project_name} {extended_history_cfx_query.label} {extended_history_cfx_query.output_file_name_without_extension}"
            ):
                self.generate_and_download_query_results_for_project_filters(change_state_cfx_query=extended_history_cfx_query)

        with stopwatch_with_label_and_surround_with_screenshots(
            label="generate_and_download_query_results_for_project_filters for all other projects",
            remote_web_driver=self.driver,
            screenshots_directory_path=self.screenshots_output_relative_path,
        ):
            projects_field_filters = ProjectsFieldFilter(projects_names=set(self.projects_to_handle_list), filter_type=FilterFieldType.DIFFERENT_TO)

            self.generate_and_download_query_results_for_project_filters(
                change_state_cfx_query=CfxQuery(
                    projects_field_filters=projects_field_filters,
                    query_id=PROJECT_MANUAL_SELECTION_CHANGE_STATE_QUERY_ID,
                    output_file_name_without_extension="states_changes_other_projects",
                    label="other_projects",
                    output_file_type=QueryOutputFileType.EXCEL_EXPORT,
                )
            )

            self.generate_and_download_query_results_for_project_filters(
                change_state_cfx_query=CfxQuery(
                    projects_field_filters=projects_field_filters,
                    query_id=PROJECT_MANUAL_SELECTION_DETAIL_QUERY_ID,
                    output_file_name_without_extension="details_project_other_projects",
                    label="other_projects",
                    output_file_type=QueryOutputFileType.EXCEL_EXPORT,
                )
            )

    def generate_and_download_query_results_for_project_filters(self, change_state_cfx_query: CfxQuery, number_of_retry_if_failure: int = 3) -> None:

        try:
            projects_field_filter = change_state_cfx_query.projects_field_filters
            self.open_request_url(change_state_cfx_query.query_id)

            if projects_field_filter:
                filter_text_to_type = projects_field_filter.filter_type.value
                with stopwatch_with_label_and_surround_with_screenshots(
                    label=f"generate_and_download_query_results_for_project_filters type filter type {filter_text_to_type}",
                    remote_web_driver=self.driver,
                    screenshots_directory_path=self.screenshots_output_relative_path,
                ):
                    input_element = WebDriverWait(self.driver, 100).until(expected_conditions.presence_of_element_located((By.ID, "dijit_form_FilteringSelect_0")))

                    # input_element = self.driver.find_element(By.ID, "dijit_form_FilteringSelect_0")
                    input_element.clear()  # Clear any pre-existing text
                    input_element.send_keys(filter_text_to_type)

                with stopwatch_with_label_and_surround_with_screenshots(
                    label=f"{change_state_cfx_query.label} generate_and_download_query_results_for_project_filters element_to_be_clickable Sélectionner",
                    remote_web_driver=self.driver,
                    screenshots_directory_path=self.screenshots_output_relative_path,
                ):
                    selectionner_button_container_node = WebDriverWait(self.driver, 100).until(
                        expected_conditions.element_to_be_clickable((By.XPATH, "//span[@data-dojo-attach-point='containerNode' and text()='Sélectionner']"))
                    )

                with stopwatch_with_label_and_surround_with_screenshots(
                    label=f"{change_state_cfx_query.label} selectionner_button_container_node.click()",
                    remote_web_driver=self.driver,
                    screenshots_directory_path=self.screenshots_output_relative_path,
                ):
                    selectionner_button_container_node.click()

                for project_name in projects_field_filter.projects_names:

                    with stopwatch_with_label_and_surround_with_screenshots(
                        label=f"{change_state_cfx_query.label} generate_and_download_query_results_for_project_filters - search input_project_name_to_type",
                        remote_web_driver=self.driver,
                        screenshots_directory_path=self.screenshots_output_relative_path,
                    ):
                        input_project_name_to_type = WebDriverWait(self.driver, 100).until(expected_conditions.presence_of_element_located((By.ID, "cq_widget_CqDoubleListBox_0_textBox")))

                    with stopwatch_with_label_and_surround_with_screenshots(
                        label=f"{change_state_cfx_query.label} generate_and_download_query_results_for_project_filters - type {project_name} in input_project_name_to_type",
                        remote_web_driver=self.driver,
                        screenshots_directory_path=self.screenshots_output_relative_path,
                    ):
                        input_project_name_to_type.clear()
                        input_project_name_to_type.send_keys(project_name)

                    with stopwatch_with_label_and_surround_with_screenshots(
                        label=f"{project_name}  project_option_element find_element", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path
                    ):
                        project_option_element = self.driver.find_element(By.XPATH, f"//select[@id='cq_widget_CqDoubleListBox_0_choiceList']//option[text()='{project_name}']")

                    actions = ActionChains(self.driver)

                    with stopwatch_with_label_and_surround_with_screenshots(
                        label=f"{project_name} project_option_element double_click", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path
                    ):
                        actions.double_click(project_option_element).perform()

                ok_button = self.driver.find_element(By.XPATH, "//span[@class='dijitReset dijitInline dijitButtonText' and text()='OK']")
                with stopwatch_with_label_and_surround_with_screenshots(label="ok_button.click", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
                    ok_button.click()

                with stopwatch_with_label_and_surround_with_screenshots(
                    label=f"{change_state_cfx_query.label} generate_and_download_query_results_for_project_filters - wait popup closed to allow request execution",
                    remote_web_driver=self.driver,
                    screenshots_directory_path=self.screenshots_output_relative_path,
                ):
                    WebDriverWait(self.driver, 10).until(expected_conditions.invisibility_of_element((By.ID, "cq_widget_CqDoubleListBox_0_choiceList")))

                with stopwatch_with_label_and_surround_with_screenshots(
                    label=f"{change_state_cfx_query.label} generate_and_download_query_results_for_project_filters Exécuter la requête",
                    remote_web_driver=self.driver,
                    screenshots_directory_path=self.screenshots_output_relative_path,
                ):
                    executer_requete_button = self.driver.find_element(By.XPATH, "//span[@class='dijitReset dijitInline dijitButtonText' and text()='Exécuter la requête']")
                    executer_requete_button.click()

            with stopwatch_with_label_and_surround_with_screenshots(
                label=f"{change_state_cfx_query.label} generate_and_download_query_results_for_project_filters - wait table result",
                remote_web_driver=self.driver,
                screenshots_directory_path=self.screenshots_output_relative_path,
            ):
                WebDriverWait(self.driver, 150).until(expected_conditions.presence_of_element_located((By.ID, "unique_info_col")))

            with stopwatch_with_label_and_surround_with_screenshots(
                label=f"{change_state_cfx_query.label} generate_and_download_query_results_for_project_filters - wait column CFXID",
                remote_web_driver=self.driver,
                screenshots_directory_path=self.screenshots_output_relative_path,
            ):
                WebDriverWait(self.driver, 100).until(expected_conditions.presence_of_element_located((By.XPATH, "//th/div[text()='CFXID']")))

            with stopwatch_with_label_and_surround_with_screenshots(
                label=f"{change_state_cfx_query.label} generate_and_download_query_results_for_project_filters - request execution additional waiting time",
                remote_web_driver=self.driver,
                screenshots_directory_path=self.screenshots_output_relative_path,
            ):
                time.sleep(0.5)

            match change_state_cfx_query.output_file_type:
                case QueryOutputFileType.EXCEL_EXPORT:
                    with stopwatch_with_label_and_surround_with_screenshots(
                        label=f"{change_state_cfx_query.label} download_current_query_to_excel_file",
                        remote_web_driver=self.driver,
                        screenshots_directory_path=self.screenshots_output_relative_path,
                    ):
                        self.download_current_query_to_file(
                            change_state_cfx_query=change_state_cfx_query,
                            label=change_state_cfx_query.label,
                            file_to_create_path_with_extension=f"{self.output_downloaded_files_final_directory_path}/{change_state_cfx_query.output_file_name_without_extension}{EXCEL_FILE_EXTENSION}",
                        )
                case QueryOutputFileType.TXT_EXPORT:

                    with stopwatch_with_label_and_surround_with_screenshots(
                        label=f"{change_state_cfx_query.label} download_current_query_to_text_file",
                        remote_web_driver=self.driver,
                        screenshots_directory_path=self.screenshots_output_relative_path,
                    ):
                        self.download_current_query_to_file(
                            change_state_cfx_query=change_state_cfx_query,
                            label=change_state_cfx_query.label,
                            file_to_create_path_with_extension=f"{self.output_downloaded_files_final_directory_path}/{change_state_cfx_query.output_file_name_without_extension}{TEXT_FILE_EXTENSION}",
                        )

        except Exception as e:

            self.number_of_exceptions_caught += 1
            logger_config.print_and_log_exception(e)
            logger_config.print_and_log_error(f"{self.number_of_exceptions_caught}th Exception  {self.number_of_exceptions_caught}  number_of_retry_if_failure:{number_of_retry_if_failure}")
            self.driver.get_screenshot_as_file(f"{self.errors_output_relative_path}/{self.number_of_exceptions_caught} th Exception caught.png")

            for i in range(1, 15):
                with stopwatch_with_label_and_surround_with_screenshots(
                    label=f"Post mortem {self.number_of_exceptions_caught}th Exception delay {i}", remote_web_driver=self.driver, screenshots_directory_path=self.errors_output_relative_path
                ):
                    time.sleep(i)

            self.driver.get_screenshot_as_file(f"{self.errors_output_relative_path}/{self.number_of_exceptions_caught} th Exception caught after post mortem delay.png")

            with logger_config.stopwatch_with_label("Reset_driver :"):
                self.reset_driver()
            if number_of_retry_if_failure > 0:
                with logger_config.stopwatch_with_label("Generate_and_dowload_query_for_project"):
                    self.generate_and_download_query_results_for_project_filters(change_state_cfx_query=change_state_cfx_query, number_of_retry_if_failure=number_of_retry_if_failure - 1)

    def download_current_query_to_file(self, change_state_cfx_query: CfxQuery, label: str, file_to_create_path_with_extension: str) -> bool:

        with surround_with_screenshots(label=f"{label} arrow_to_acces_export element_to_be_clickable", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
            arrow_to_acces_export = WebDriverWait(self.driver, 100).until(expected_conditions.element_to_be_clickable((By.ID, "dijit_form_ComboButton_1_arrow")))

        with surround_with_screenshots(label=f"{label} arrow_to_acces_export click", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
            arrow_to_acces_export.click()

        export_button = self.driver.find_element(By.XPATH, "//td[contains(text(),'" + change_state_cfx_query.output_file_type.get_file_download_dropdown_menu_option_text() + "')]")

        download_file_detector = download_utils.DownloadFileDetector(
            directory_path=self.web_browser_download_directory,
            filename_pattern=CFX_FILES_DOWNLOADED_PATTERN_WITHOUT_EXTENSION + change_state_cfx_query.output_file_type.get_file_extension(),
            timeout_in_seconds=1000,
            file_move_after_download_action=download_utils.DownloadFileDetector.FileMoveAfterDownloadAction(final_path=file_to_create_path_with_extension),
        )
        export_button.click()

        file_downloaded_path: Optional[str] = download_file_detector.monitor_download()
        if not file_downloaded_path:
            logger_config.print_and_log_error(f"No downloaded file found for {label}")
            return False

        return True

    def create_webdriver_chrome(self) -> None:
        self.driver = web_driver_utils.create_webdriver_chrome(
            browser_visibility_type=web_driver_utils.BrowserVisibilityType.NOT_VISIBLE_AKA_HEADLESS, download_directory_path=DEFAULT_DOWNLOAD_DIRECTORY, global_timeout_in_seconds=1000
        )

    def create_webdriver_firefox(self) -> None:
        self.driver = web_driver_utils.create_webdriver_firefox(browser_visibility_type=web_driver_utils.BrowserVisibilityType.REGULAR)

    def create_webdriver_and_login(self) -> None:
        # Use Chrome by default, switch to Firefox if you want
        # self.create_webdriver_chrome()
        self.create_webdriver_firefox()
        self.login_champfx()

    def reset_driver(self) -> None:
        self.driver.quit()
        self.create_webdriver_and_login()

    def login_champfx(self) -> None:
        logger_config.print_and_log_info("login_champfx")

        login_url = f"https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX?format=HTML&loginId={connexion_param.champfx_login}&password={connexion_param.champfx_password}"

        with stopwatch_with_label_and_surround_with_screenshots(
            label=f"Driver get login url {login_url}", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path
        ):
            self.driver.get(login_url)

        with stopwatch_with_label_and_surround_with_screenshots(label="Waited page is loaded", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
            with surround_with_screenshots(label="login_champfx - title_contains ok", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
                WebDriverWait(self.driver, 100).until(expected_conditions.title_contains("01_CHAMP/CFX - IBM Rational ClearQuest"))

            with surround_with_screenshots(label="login_champfx - document.readyState complete", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
                WebDriverWait(self.driver, 40).until(lambda driver: self.driver.execute_script("return document.readyState") == "complete")
            try:
                with surround_with_screenshots(
                    label="login_champfx - text_to_be_present_in_element welcomeMsg", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path
                ):
                    WebDriverWait(self.driver, 100).until(expected_conditions.text_to_be_present_in_element((By.ID, "welcomeMsg"), "AD001\\fr232487"))
            except TimeoutException as e:
                logger_config.print_and_log_exception(e)

        with stopwatch_with_label_and_surround_with_screenshots(
            label="login_champfx - Additional waiting time", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path
        ):
            time.sleep(0.5)

    def open_request_url(self, request_full_path: int) -> None:
        request_url = f"https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/QUERY/{request_full_path}?format=HTML&loginId={connexion_param.champfx_login}&password={connexion_param.champfx_password}&noframes=true"

        with stopwatch_with_label_and_surround_with_screenshots(label=f"Driver get url {request_url}", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
            self.driver.get(request_url)

        with stopwatch_with_label_and_surround_with_screenshots(label="Waited Title is now good", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
            WebDriverWait(self.driver, 10).until(expected_conditions.title_contains("01_CHAMP/CFX - IBM Rational ClearQuest"))

        with stopwatch_with_label_and_surround_with_screenshots(
            label="Wait for the page to be fully loaded (JavaScript):: document.readyState now good", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path
        ):
            WebDriverWait(self.driver, 10).until(lambda driver: self.driver.execute_script("return document.readyState") == "complete")  # mypy: disable=disallow-untyped-calls

        with stopwatch_with_label_and_surround_with_screenshots(label="Additional waiting time", remote_web_driver=self.driver, screenshots_directory_path=self.screenshots_output_relative_path):
            time.sleep(0.8)


def main() -> None:
    """Main function"""

    with logger_config.application_logger("save_cfx_requests_to_files"):
        output_parent_directory_name = OUTPUT_PARENT_DIRECTORY_DEFAULT_NAME
        logger_config.print_and_log_info(f"output_parent_directory_name: {output_parent_directory_name}")

        application: SaveCfxRequestMultipagesResultsApplication = SaveCfxRequestMultipagesResultsApplication(
            output_parent_directory_name=output_parent_directory_name,
            projects_to_handle_list=INTERESTED_IN_PROJECTS_NAMES + BIGGEST_PROJECTS_NAMES,
            headless=True,  # <--- Set to True for completely hidden, False for minimized
        )
        application.run()


if __name__ == "__main__":
    main()
