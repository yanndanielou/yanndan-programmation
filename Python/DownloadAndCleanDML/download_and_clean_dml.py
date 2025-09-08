# Standard

import inspect
import os
from dataclasses import dataclass
from typing import Optional

from common import download_utils, excel_utils

# Other libraries
from logger import logger_config
from rhapsody import rhapsody_utils

from param import COLUMNS_NAMES_TO_REMOVE

# import pywintypes

DEFAULT_DOWNLOAD_DIRECTORY = os.path.expandvars(r"%userprofile%\downloads")

DML_FILE_DOWNLOADED_PATTERN = "DML_NEXTEO_ATS+_V*.xlsm"

DML_FILE_WITHOUT_USELESS_SHEETS_PATH = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14_without_useless_sheets.xlsm"
DML_FILE_WITH_USELESS_RANGES = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14_with_useless_ranges_cleaned.xlsm"
DML_FILE_WITH_USELESS_COLUMNS_CLEANED = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14_with_useless_columns_cleaned.xlsm"
DML_FILE_WITHOUT_LINKS = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14_without_links.xlsm"
DML_FILE_CLEANED_FINAL = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14_cleaned_light.xlsm"
DML_RAW_DOWNLOADED_FROM_RHAPSODY_FILE_PATH = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14_raw_from_rhapsody.xlsm"
DML_FILE_FINAL_DESTINATION_PATH = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14.xlsm"

USEFUL_DML_SHEET_NAME = "Database"
ALLOWED_DML_SHEETS_NAMES = [USEFUL_DML_SHEET_NAME]

FIRST_LINE_TO_REMOVE_RANGES = "1:1"
RANGES_TO_REMOVE = [FIRST_LINE_TO_REMOVE_RANGES]

DOWNLOAD_FROM_RHAPSODY_ENABLED = True
REMOVE_USELESS_SHEETS_ENABLED = True
REMOVE_LINKS_SHEETS_ENABLED = True
REMOVE_USELESS_RANGES_ENABLED = True
REMOVE_USELESS_COLUMNS_ENABLED = True


@dataclass
class DownloadAndCleanDMLApplication:

    def run(self) -> None:

        dml_file_path = self.download_dml_file()
        if dml_file_path:
            dml_file_path = self.remove_useless_tabs(dml_file_path)
            dml_file_path = self.remove_excel_external_links(dml_file_path)
            dml_file_path = self.remove_useless_ranges(dml_file_path)
            dml_file_path = self.remove_useless_columns(dml_file_path)
        else:
            logger_config.print_and_log_error("Aborted")

    def remove_useless_tabs(self, dml_file_path: str) -> str:
        file_to_create_path = DML_FILE_WITHOUT_USELESS_SHEETS_PATH

        if not REMOVE_USELESS_SHEETS_ENABLED:
            logger_config.print_and_log_info(f"{inspect.stack(0)[0].function} Disabled: pass")
            return file_to_create_path

        final_excel_file_path: str = excel_utils.remove_tabs_with_xlwings(
            input_excel_file_path=dml_file_path,
            file_to_create_path=file_to_create_path,
            sheets_to_keep_names=ALLOWED_DML_SHEETS_NAMES,
        )

        return final_excel_file_path

    def remove_excel_external_links(self, dml_file_path: str) -> str:
        file_to_create_path = DML_FILE_WITHOUT_LINKS

        if not REMOVE_LINKS_SHEETS_ENABLED:
            logger_config.print_and_log_info(f"{inspect.stack(0)[0].function} Disabled: pass")
            return file_to_create_path

        final_excel_file_path: str = excel_utils.remove_excel_external_links_with_xlwings(input_excel_file_path=dml_file_path, file_to_create_path=file_to_create_path)

        return final_excel_file_path

    def remove_useless_ranges(self, dml_file_path: str) -> str:
        file_to_create_path = DML_FILE_WITH_USELESS_RANGES

        if not REMOVE_USELESS_RANGES_ENABLED:
            logger_config.print_and_log_info(f"{inspect.stack(0)[0].function} Disabled: pass")
            return file_to_create_path

        final_excel_file_path: str = excel_utils.remove_ranges_with_xlwings(input_excel_file_path=dml_file_path, ranges_to_remove=RANGES_TO_REMOVE, file_to_create_path=file_to_create_path)
        return final_excel_file_path

    def remove_useless_columns(self, dml_file_path: str) -> str:
        file_to_create_path = DML_FILE_CLEANED_FINAL

        if not REMOVE_USELESS_COLUMNS_ENABLED:
            logger_config.print_and_log_info(f"{inspect.stack(0)[0].function} Disabled: pass")
            return file_to_create_path

        final_excel_file_path: str = excel_utils.remove_columns_with_xlwings(
            input_excel_file_path=dml_file_path, columns_to_remove_names=COLUMNS_NAMES_TO_REMOVE, file_to_create_path=file_to_create_path, sheet_name=USEFUL_DML_SHEET_NAME
        )
        return final_excel_file_path

    def download_dml_file(self) -> Optional[str]:
        file_to_create_path = DML_RAW_DOWNLOADED_FROM_RHAPSODY_FILE_PATH

        if not DOWNLOAD_FROM_RHAPSODY_ENABLED:
            logger_config.print_and_log_info(f"{inspect.stack(0)[0].function} Disabled: pass")
            return file_to_create_path

        dml_download_url = "https://rhapsody.siemens.net/livelink/livelink.exe?func=ll&objId=79329709&objAction=Download"
        rhapsody_utils.download_file_from_rhapsody(
            file_to_download_pattern=DML_FILE_DOWNLOADED_PATTERN,
            file_to_download_url=dml_download_url,
            file_move_after_download_action=download_utils.DownloadFileDetector.FileMoveAfterDownloadAction(final_path=DML_RAW_DOWNLOADED_FROM_RHAPSODY_FILE_PATH, retry_in_case_of_error=True),
        )

        return file_to_create_path


if __name__ == "__main__":

    with logger_config.application_logger("DownloadAndCleanDML"):

        application: DownloadAndCleanDMLApplication = DownloadAndCleanDMLApplication()
        application.run()
