# Standard

import inspect
from dataclasses import dataclass
from typing import Optional

# Other libraries
from common import download_utils, excel_utils
from logger import logger_config
from pywintypes import com_error
from rhapsody import rhapsody_utils

import param


@dataclass
class DownloadAndCleanDMLApplication:

    def run(self) -> None:

        excel_utils.close_all_xlwings()
        dml_file_path = self.download_dml_file()

        # dml_file_path = excel_utils.convert_xlsx_file_to_xls_with_win32com_dispatch(dml_file_path)
        self.run_step_by_step(dml_file_path)

    def run_in_one_batch(self, dml_file_path: str) -> None:
        operations_batch = excel_utils.XlWingsOperationsBatch(excel_visibility=False, input_excel_file_path=dml_file_path, file_to_create_path=param.DML_FILE_CLEANED_FINAL)
        operations_batch.add_operation(excel_utils.XlWingsRemoveTabsOperation(sheets_to_keep_names=param.ALLOWED_DML_SHEETS_NAMES))
        operations_batch.add_operation(excel_utils.XlWingsSaveWorkbookOperation(file_to_create_path=param.DML_FILE_WITHOUT_USELESS_SHEETS_PATH))
        operations_batch.add_operation(excel_utils.XlWingsRemoveExcelExternalLinksOperation())
        operations_batch.add_operation(excel_utils.XlWingsSaveWorkbookOperation(file_to_create_path=param.DML_FILE_WITHOUT_LINKS))
        operations_batch.add_operation(excel_utils.XlWingsRemoveRangesOperation(ranges_to_remove=param.RANGES_TO_REMOVE))
        operations_batch.add_operation(excel_utils.XlWingsSaveWorkbookOperation(file_to_create_path=param.DML_FILE_WITH_USELESS_RANGES))
        operations_batch.add_operation(excel_utils.XlWingsRemoveColumnsOperation(columns_to_remove_names=param.COLUMNS_NAMES_TO_REMOVE, sheet_name=param.USEFUL_DML_SHEET_NAME))

        operations_batch.do()

    def run_step_by_step(self, dml_file_path: str) -> None:

        dml_file_path = self.remove_useless_tabs(dml_file_path)
        dml_file_path = self.remove_excel_external_links(dml_file_path)
        dml_file_path = self.remove_useless_ranges(dml_file_path)
        try:
            dml_file_path = self.remove_useless_columns(dml_file_path)
        except com_error as e:
            logger_config.print_and_log_exception(e)
            logger_config.print_and_log_error("Error when remove_useless_columns, will retry")
            except_info_error_code_5 = e.excepinfo[5]
            logger_config.print_and_log_error(f"Exception except_info_error_codes: {e.excepinfo}")
            logger_config.print_and_log_error(f"Exception except_info_error_code_5: {except_info_error_code_5}")
            if except_info_error_code_5 == -2147220464:
                logger_config.print_and_log_error("Please change the Quickbooks mode to Multi-user Mode.")

            elif except_info_error_code_5 == -2147220472:
                logger_config.print_and_log_error("Please start Quickbooks.")

            excel_utils.close_all_xlwings()

            logger_config.print_and_log_info("remove_useless_columns: retry")
            dml_file_path = self.remove_useless_columns(dml_file_path)

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
        file_to_create_path = param.DML_FILE_WITHOUT_LINKS

        if not param.REMOVE_LINKS_SHEETS_ENABLED:
            logger_config.print_and_log_warning(f"{inspect.stack(0)[0].function} Disabled: pass")
            return file_to_create_path

        final_excel_file_path: str = excel_utils.remove_excel_external_links_with_xlwings(input_excel_file_path=dml_file_path, file_to_create_path=file_to_create_path)

        return final_excel_file_path

    def remove_useless_ranges(self, dml_file_path: str) -> str:
        file_to_create_path = param.DML_FILE_WITH_USELESS_RANGES

        if not param.REMOVE_USELESS_RANGES_ENABLED:
            logger_config.print_and_log_warning(f"{inspect.stack(0)[0].function} Disabled: pass")
            return file_to_create_path

        final_excel_file_path: str = excel_utils.remove_ranges_with_xlwings(input_excel_file_path=dml_file_path, ranges_to_remove=param.RANGES_TO_REMOVE, file_to_create_path=file_to_create_path)
        return final_excel_file_path

    def remove_useless_columns(self, dml_file_path: str) -> str:
        file_to_create_path = param.DML_FILE_CLEANED_FINAL

        if not param.REMOVE_USELESS_COLUMNS_ENABLED:
            logger_config.print_and_log_warning(f"{inspect.stack(0)[0].function} Disabled: pass")
            return file_to_create_path

        final_excel_file_path: str = excel_utils.remove_columns_with_xlwings(
            input_excel_file_path=dml_file_path,
            columns_to_remove_names=param.COLUMNS_NAMES_TO_REMOVE,
            file_to_create_path=file_to_create_path,
            sheet_name=param.USEFUL_DML_SHEET_NAME,
            removal_operation_type=excel_utils.XlWingsRemoveColumnsOperation.RemovalOperationType.COLUMN_ONE_BY_ONE_USING_LETTER,
        )
        return final_excel_file_path

    def download_dml_file(self) -> str:
        file_to_create_path = param.DML_RAW_DOWNLOADED_FROM_RHAPSODY_FILE_PATH

        if not param.DOWNLOAD_FROM_RHAPSODY_ENABLED:
            logger_config.print_and_log_warning(f"{inspect.stack(0)[0].function} Disabled: pass")
            return file_to_create_path

        dml_download_url = "https://rhapsody.siemens.net/livelink/livelink.exe?func=ll&objId=79329709&objAction=Download"
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
