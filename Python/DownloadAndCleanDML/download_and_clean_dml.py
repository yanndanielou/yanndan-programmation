# Standard

import datetime
import inspect
import os
import shutil
from dataclasses import dataclass
from typing import Optional

# Other libraries
from common import download_utils, excel_utils, file_name_utils, file_utils
from logger import logger_config
from rhapsody import rhapsody_utils

import param


@dataclass
class DownloadAndCleanDMLApplication:

    def run(self) -> None:

        excel_utils.close_all_xlwings()
        dml_file_path = self.download_dml_file()

        dml_file_path = excel_utils.copy_and_paste_excel_content_with_format_with_win32(
            input_excel_file_path=dml_file_path,
            sheet_name="Database",
            output_excel_file_path=param.DML_FILE_CONVERTED_TO_STANDARD_XSLX_PATH,
            # output_excel_file_path=f"{os.path.expandvars(r"%userprofile%\downloads")}\\copy_and_paste_excel_content_with_format_with_win32.xlsx",
        )

        # dml_file_path = excel_utils.convert_xlsx_file_to_xls_with_win32com_dispatch(dml_file_path)
        self.run_step_by_step(dml_file_path)

    def run_in_one_batch(self, dml_file_path: str) -> None:
        operations_batch = excel_utils.XlWingsOperationsBatch(excel_visibility=False, input_excel_file_path=dml_file_path, file_to_create_path=param.DML_FILE_CLEANED_FINAL_PATH)
        operations_batch.add_operation(excel_utils.XlWingsRemoveTabsOperation(sheets_to_keep_names=param.ALLOWED_DML_SHEETS_NAMES))
        operations_batch.add_operation(excel_utils.XlWingsSaveWorkbookOperation(file_to_create_path=param.DML_FILE_WITHOUT_USELESS_SHEETS_PATH))
        operations_batch.add_operation(excel_utils.XlWingsRemoveExcelExternalLinksOperation())
        operations_batch.add_operation(excel_utils.XlWingsSaveWorkbookOperation(file_to_create_path=param.DML_FILE_WITHOUT_LINKS_PATH))
        operations_batch.add_operation(excel_utils.XlWingsRemoveRangesOperation(ranges_to_remove=param.RANGES_TO_REMOVE))
        operations_batch.add_operation(excel_utils.XlWingsSaveWorkbookOperation(file_to_create_path=param.DML_FILE_WITH_USELESS_RANGES_PATH))
        operations_batch.add_operation(
            excel_utils.XlWingsRemoveColumnsOperation(columns_to_remove_names=param.COLUMNS_NAMES_TO_REMOVE, sheet_name=param.USEFUL_DML_SHEET_NAME, assert_if_column_is_missing=False)
        )

        operations_batch.do()

    def run_step_by_step(self, dml_file_path: str) -> None:

        dml_file_path = self.remove_useless_tabs(dml_file_path)
        dml_file_path = self.remove_excel_external_links(dml_file_path)
        dml_file_path = self.remove_useless_ranges(dml_file_path)
        # dml_file_path_standard_excel = self.convert_excel_to_standard_xslx(dml_file_path)
        dml_file_path_openpyxl = self.remove_useless_columns_with_openpyxl(dml_file_path)
        dml_file_path_xlwings = self.remove_useless_columns_with_xlwings(dml_file_path)
        dml_file_path = shutil.copy(dml_file_path_xlwings, param.DML_FILE_CLEANED_FINAL_PATH)

        self.create_dated_copy_of_dml(dml_file_path_xlwings)

    def remove_useless_tabs(self, dml_file_path: str) -> str:
        file_to_create_path = param.DML_FILE_WITHOUT_USELESS_SHEETS_PATH

        if not param.REMOVE_USELESS_SHEETS_ENABLED:
            logger_config.print_and_log_warning(f"{inspect.stack(0)[0].function} Disabled: pass")
            return file_to_create_path

        final_excel_file_path: str = excel_utils.remove_tabs_with_xlwings(
            input_excel_file_path=dml_file_path,
            file_to_create_path=file_to_create_path,
            sheets_to_keep_names=param.ALLOWED_DML_SHEETS_NAMES,
        )

        return final_excel_file_path

    def remove_excel_external_links(self, dml_file_path: str) -> str:
        file_to_create_path = param.DML_FILE_WITHOUT_LINKS_PATH

        if not param.REMOVE_LINKS_SHEETS_ENABLED:
            logger_config.print_and_log_warning(f"{inspect.stack(0)[0].function} Disabled: pass")
            return file_to_create_path

        final_excel_file_path: str = excel_utils.remove_excel_external_links_with_xlwings(input_excel_file_path=dml_file_path, file_to_create_path=file_to_create_path)

        return final_excel_file_path

    def remove_useless_ranges(self, dml_file_path: str) -> str:
        file_to_create_path = param.DML_FILE_WITH_USELESS_RANGES_PATH

        if not param.REMOVE_USELESS_RANGES_ENABLED:
            logger_config.print_and_log_warning(f"{inspect.stack(0)[0].function} Disabled: pass")
            return file_to_create_path

        final_excel_file_path: str = excel_utils.remove_ranges_with_xlwings(input_excel_file_path=dml_file_path, ranges_to_remove=param.RANGES_TO_REMOVE, file_to_create_path=file_to_create_path)
        return final_excel_file_path

    def convert_excel_to_standard_xslx(self, dml_file_path: str) -> str:
        file_to_create_path = param.DML_FILE_CONVERTED_TO_STANDARD_XSLX_PATH

        if not param.CONVERT_EXCEL_TO_STANDARD_XSLX_ENABLED:
            logger_config.print_and_log_warning(f"{inspect.stack(0)[0].function} Disabled: pass")
            return file_to_create_path

        logger_config.print_and_log_info(f"convert_excel_to_standard_xslx: {dml_file_path}")

        with file_utils.temporary_copy_of_file(dml_file_path) as temp_xlsm_file_full_path:
            xlsx_excel_file_path: str = excel_utils.convert_excel_file_to_xlsx_with_win32com_dispatch(temp_xlsm_file_full_path)
            shutil.copy(xlsx_excel_file_path, file_to_create_path)

        return file_to_create_path

    def remove_useless_columns_with_openpyxl(self, dml_file_path: str) -> str:
        file_to_create_path = param.DML_FILE_WITH_USELESS_COLUMNS_REMOVED_OPENPYXL_PATH

        if not param.REMOVE_USELESS_COLUMNS_ENABLED:
            logger_config.print_and_log_warning(f"{inspect.stack(0)[0].function} Disabled: pass")
            return file_to_create_path

        final_excel_file_path: str = excel_utils.remove_columns_with_openpyxl(
            excel_utils.RemoveColumnsInstructions(
                input_excel_file_path=dml_file_path,
                columns_to_remove_names=param.COLUMNS_NAMES_TO_REMOVE,
                file_to_create_path=file_to_create_path,
                sheet_name=param.USEFUL_DML_SHEET_NAME,
                removal_operation_type=excel_utils.ColumnRemovalOperationType.COLUMN_ONE_BY_ONE_USING_LETTER,
                assert_if_column_is_missing=False,
            )
        )
        return final_excel_file_path

    def remove_useless_columns_with_xlwings(self, dml_file_path: str) -> str:
        file_to_create_path = param.DML_FILE_WITH_USELESS_COLUMNS_REMOVED_XLWINGS_PATH

        if not param.REMOVE_USELESS_COLUMNS_ENABLED:
            logger_config.print_and_log_warning(f"{inspect.stack(0)[0].function} Disabled: pass")
            return file_to_create_path

        final_excel_file_path: str = excel_utils.remove_columns_with_xlwings(
            excel_utils.RemoveColumnsInstructions(
                input_excel_file_path=dml_file_path,
                columns_to_remove_names=param.COLUMNS_NAMES_TO_REMOVE,
                file_to_create_path=file_to_create_path,
                sheet_name=param.USEFUL_DML_SHEET_NAME,
                removal_operation_type=excel_utils.ColumnRemovalOperationType.COLUMN_ONE_BY_ONE_USING_LETTER,
                assert_if_column_is_missing=False,
            )
        )

        return final_excel_file_path

    def create_dated_copy_of_dml(self, dml_file_path: str) -> None:

        today_copy_file_name = (
            file_name_utils.get_file_name_without_extension_from_full_path(dml_file_path)
            + " - "
            + datetime.datetime.now().strftime("%Y-%m-%d")
            + file_name_utils.file_extension_from_full_path(dml_file_path)
        )
        final_excel_file_directory = os.path.dirname(dml_file_path)
        today_copy_file_full_path = f"{final_excel_file_directory}/{today_copy_file_name}"
        logger_config.print_and_log_info(f"Copy final {dml_file_path} to today copy {today_copy_file_full_path}")
        shutil.copy(dml_file_path, today_copy_file_full_path)

    def download_dml_file(self) -> str:
        file_to_create_path = param.DML_RAW_DOWNLOADED_FROM_RHAPSODY_FILE_PATH

        if not param.DOWNLOAD_FROM_RHAPSODY_ENABLED:
            logger_config.print_and_log_warning(f"{inspect.stack(0)[0].function} Disabled: pass")
            return file_to_create_path

        dml_download_url = f"https://rhapsody.siemens.net/livelink/livelink.exe?func=ll&objId={param.DML_FILE_RHAPS_ID}&objAction=Download"
        file_downloaded: Optional[str] = rhapsody_utils.download_file_from_rhapsody_old(
            file_to_download_pattern=param.DML_FILE_DOWNLOADED_PATTERN,
            file_to_download_url=dml_download_url,
            file_move_after_download_action=download_utils.DownloadFileDetector.FileMoveAfterDownloadAction(
                final_path=param.DML_RAW_DOWNLOADED_FROM_RHAPSODY_FILE_PATH, retry_in_case_of_error=download_utils.DownloadFileDetector.RetryInCaseOfErrorAction()
            ),
        )
        assert file_downloaded

        return file_downloaded


if __name__ == "__main__":

    with logger_config.application_logger("DownloadAndCleanDML"):

        application: DownloadAndCleanDMLApplication = DownloadAndCleanDMLApplication()
        application.run()
