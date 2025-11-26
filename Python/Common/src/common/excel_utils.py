# Standard
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, cast

from enum import Enum, auto

import openpyxl
import xlwings
from xlwings.constants import DeleteShiftDirection

from win32com.client import Dispatch

from common import file_utils, file_name_utils


# Other libraries
from logger import logger_config

# import pywintypes
from xlsxwriter.utility import xl_cell_to_rowcol, xl_col_to_name

EXCEL_INTERNAL_RESERVED_SHEETS_NAMES = ["Register"]

EXCEL_FILE_EXTENSION = ".xlsx"

# cf    https://learn.microsoft.com/fr-fr/office/vba/api/Excel.XlFileFormat
EXCEL_8_XLS_FORMAT_XL_FILE_FORMAT_VALUE = 56
EXCEL_WORKBOOK_DEFAULT_XLSX_FORMAT_XL_FILE_FORMAT_VALUE = 51


def convert_xlsx_file_to_xls_with_win32com_dispatch(xlsx_file_full_path: str) -> str:
    with logger_config.stopwatch_with_label(f"convert_xlsx_file_to_xls: {xlsx_file_full_path}"):
        xls_output_file_path = xlsx_file_full_path[:-1]
        with logger_config.stopwatch_with_label("convert_xlsx_file_to_xls: open excel application"):
            xl = Dispatch("Excel.Application")

        xl.DisplayAlerts = False

        with logger_config.stopwatch_with_label(f"convert_xlsx_file_to_xls: open {xlsx_file_full_path}"):
            wb = xl.Workbooks.Add(xlsx_file_full_path)

        wb.CheckCompatibility = False
        wb.DoNotPromptForConvert = True

        with logger_config.stopwatch_with_label(f"convert_xlsx_file_to_xls: save {xls_output_file_path}"):
            wb.SaveAs(xls_output_file_path, FileFormat=EXCEL_8_XLS_FORMAT_XL_FILE_FORMAT_VALUE)
        with logger_config.stopwatch_with_label("convert_xlsx_file_to_xls: quit excel"):
            xl.Quit()
        return xls_output_file_path


def convert_excel_file_to_xlsx_with_win32com_dispatch(excel_file_full_path: str) -> str:
    with logger_config.stopwatch_with_label(f"convert_excel_file_to_xlsx_with_win32com_dispatch: {excel_file_full_path}"):

        xls_output_file_path = (
            file_name_utils.get_file_folder_from_full_path(excel_file_full_path) + "/" + file_name_utils.get_file_name_without_extension_from_full_path(excel_file_full_path) + ".xlsx"
        )
        with logger_config.stopwatch_with_label("convert_excel_file_to_xlsx_with_win32com_dispatch: open excel application"):
            xl = Dispatch("Excel.Application")

        xl.DisplayAlerts = False

        with logger_config.stopwatch_with_label(f"convert_excel_file_to_xlsx_with_win32com_dispatch: open {excel_file_full_path}"):
            wb = xl.Workbooks.Add(excel_file_full_path)

        wb.CheckCompatibility = False
        wb.DoNotPromptForConvert = True

        with logger_config.stopwatch_with_label(f"convert_excel_file_to_xlsx_with_win32com_dispatch: save {xls_output_file_path}"):
            wb.SaveAs(xls_output_file_path, FileFormat=EXCEL_WORKBOOK_DEFAULT_XLSX_FORMAT_XL_FILE_FORMAT_VALUE)
        with logger_config.stopwatch_with_label("convert_excel_file_to_xlsx_with_win32com_dispatch: quit excel"):
            xl.Quit()
        return xls_output_file_path


def convert_xlsx_file_to_xls_with_openpyxl(xlsx_file_full_path: str) -> str:
    xls_output_file_path = xlsx_file_full_path[:-1]
    with logger_config.stopwatch_with_label(f"convert_xlsx_file_to_xls_with_openpyxl: {xlsx_file_full_path}", inform_beginning=True):

        with logger_config.stopwatch_with_label(f"convert_xlsx_file_to_xls_with_openpyxl: open {xlsx_file_full_path}"):
            workbook = openpyxl.load_workbook(xlsx_file_full_path)
        with logger_config.stopwatch_with_label(f"convert_xlsx_file_to_xls_with_openpyxl: save {xls_output_file_path}"):
            workbook.save(xls_output_file_path)
        with logger_config.stopwatch_with_label(f"convert_xlsx_file_to_xls_with_openpyxl: close {xls_output_file_path}"):
            workbook.close()

    return xls_output_file_path


def close_all_xlwings() -> None:
    logger_config.print_and_log_info("close_all_xlwings")
    app = xlwings.apps.add()
    wb = xlwings.Book()
    wb.close()
    app.quit()


class XlWingOperationBase(ABC):

    @abstractmethod
    def do(self, workbook_dml: xlwings.Book) -> None:
        pass


@dataclass
class XlWingsOpenWorkbookOperation:
    input_excel_file_path: str
    excel_visibility: bool
    work_on_temp_copy_of_input_file: bool = False

    def __post_init__(self) -> None:
        self.temp_copy_file_path = ""
        self.temp_copy_directory_path = ""

    def do(self) -> xlwings.Book:
        if self.work_on_temp_copy_of_input_file:
            self.temp_copy_directory_path, self.temp_copy_file_path = file_utils.get_temporary_copy_of_file(self.input_excel_file_path)
            return XlWingsOpenWorkbookOperation.open_workbook(self.temp_copy_file_path, self.excel_visibility)
        else:
            return XlWingsOpenWorkbookOperation.open_workbook(self.input_excel_file_path, self.excel_visibility)

    @staticmethod
    def open_workbook(input_excel_file_path: str, excel_visibility: bool) -> xlwings.Book:
        with logger_config.stopwatch_with_label(label=f"Open {input_excel_file_path}", inform_beginning=True):
            xlwings.App(visible=excel_visibility)
            workbook_dml = xlwings.Book(input_excel_file_path)

        return workbook_dml


@dataclass
class XlWingsSaveWorkbookOperation(XlWingOperationBase):
    file_to_create_path: str

    def do(self, workbook_dml: xlwings.Book | openpyxl.Workbook) -> None:
        XlWingsSaveWorkbookOperation.save_workbook(workbook_dml, self.file_to_create_path)

    @staticmethod
    def save_workbook(workbook_dml: xlwings.Book | openpyxl.Workbook, file_path: str) -> str:
        with logger_config.stopwatch_with_label(f"save_workbook {file_path}", inform_beginning=True):
            success = False
            while not success:
                try:
                    with logger_config.stopwatch_with_label(label=f"Save:{file_path}"):
                        workbook_dml.save(file_path)

                    success = True
                except Exception as e:
                    logger_config.print_and_log_exception(e)
                    logger_config.print_and_log_error(f"Could not save:{file_path}, must be locked")
                    time.sleep(1)

            return file_path


@dataclass
class XlWingsSaveAndCloseWorkbookOperation(XlWingOperationBase):
    file_to_create_path: str

    def do(self, workbook_dml: xlwings.Book | openpyxl.Workbook) -> None:
        XlWingsSaveAndCloseWorkbookOperation.save_and_close_workbook(workbook_dml, self.file_to_create_path)

    @staticmethod
    def save_and_close_workbook(workbook_dml: xlwings.Book | openpyxl.Workbook, file_path: str) -> str:
        with logger_config.stopwatch_with_label(f"save_and_close_workbook {file_path}", inform_beginning=True):
            success = False
            while not success:
                try:
                    with logger_config.stopwatch_with_label(label=f"Save:{file_path}"):
                        workbook_dml.save(file_path)

                    success = True
                except Exception as e:
                    logger_config.print_and_log_exception(e)
                    logger_config.print_and_log_error(f"Could not save:{file_path}, must be locked")
                    time.sleep(1)

            success = False
            while not success:
                try:

                    with logger_config.stopwatch_with_label(label="Close workbook"):
                        workbook_dml.close()

                    success = True
                except Exception as e:
                    logger_config.print_and_log_exception(e)
                    logger_config.print_and_log_error(f"Could not close:{file_path}, must be locked")
                    time.sleep(1)

            return file_path


@dataclass
class XlWingsRemoveTabsOperation(XlWingOperationBase):
    sheets_to_keep_names: List[str]

    def do(self, workbook_dml: xlwings.Book) -> None:
        XlWingsRemoveTabsOperation.remove_tabs_with_xlwings(workbook_dml, self.sheets_to_keep_names)

    @staticmethod
    def remove_tabs_with_xlwings(workbook_dml: xlwings.Book, sheets_to_keep_names: List[str]) -> None:
        with logger_config.stopwatch_with_label(f"remove_tabs_with_xlwings , sheets_to_keep_names:{sheets_to_keep_names}", inform_beginning=True):

            sheets_names = workbook_dml.sheet_names
            number_of_initial_sheets_names = len(sheets_names)
            logger_config.print_and_log_info(f"{number_of_initial_sheets_names} Sheets found: {sheets_names}")

            for sheet_number, sheet_name in enumerate(sheets_names):
                if sheet_name in sheets_to_keep_names:
                    logger_config.print_and_log_info(f"Allowed sheet:{sheet_name}")
                elif sheet_name in EXCEL_INTERNAL_RESERVED_SHEETS_NAMES:
                    logger_config.print_and_log_info(f"ignore Excel internal reserved sheet:{sheet_name}")
                else:
                    with logger_config.stopwatch_with_label(
                        label=f"Removing {sheet_number+1}/{number_of_initial_sheets_names}th sheet:{sheet_name} : {round((sheet_number+1)/number_of_initial_sheets_names*100,2)}%",
                        inform_beginning=True,
                        monitor_ram_usage=True,
                    ):
                        try:
                            # Accéder à la feuille que l'on veut supprimer
                            sheet_to_remove = xlwings.sheets[sheet_name]
                            # Supprimer la feuille
                            sheet_to_remove.delete()
                        except Exception as exc:
                            logger_config.print_and_log_exception(type(exc))
                            logger_config.print_and_log_exception(exc)


@dataclass
class XlWingsSetExcelFormulasCalculationToManualOperation(XlWingOperationBase):

    def do(self, workbook_dml: xlwings.Book) -> None:
        XlWingsSetExcelFormulasCalculationToManualOperation.set_excel_formulas_calculation_to_manual_xlwings(workbook_dml)

    @staticmethod
    def set_excel_formulas_calculation_to_manual_xlwings(workbook_dml: xlwings.Book) -> None:
        with logger_config.stopwatch_with_label(f"set_excel_formulas_calculation_to_manual input_excel_file_path:{workbook_dml.name}", inform_beginning=True):
            logger_config.print_and_log_info("set formulas calculations to manual to improve speed")
            workbook_dml.app.calculation = "manual"


class XlWingsRemoveExcelExternalLinksOperation(XlWingOperationBase):

    def do(self, workbook_dml: xlwings.Book) -> None:
        XlWingsRemoveExcelExternalLinksOperation.remove_excel_external_links_with_xlwings(workbook_dml)

    @staticmethod
    def remove_excel_external_links_with_xlwings(workbook_dml: xlwings.Book) -> None:
        with logger_config.stopwatch_with_label(f"remove_excel_external_links_with_xlwings input_excel_file_path:{workbook_dml.name}", inform_beginning=True):
            external_links_sources = workbook_dml.api.LinkSources()

            if external_links_sources:
                logger_config.print_and_log_info(f"{len(external_links_sources)} links found: {external_links_sources}")

                for external_links_source_name in external_links_sources:
                    with logger_config.stopwatch_with_label(label=f"Removing link:{external_links_source_name}"):
                        workbook_dml.api.BreakLink(Name=external_links_source_name, Type=1)  # Type=1 pour les liaisons de type Excel
            else:
                logger_config.print_and_log_info("No external link found (pass)")


@dataclass
class XlWingsReplaceFormulasWithCurrentValueOperation(XlWingOperationBase):

    def do(self, workbook_dml: xlwings.Book) -> None:
        XlWingsReplaceFormulasWithCurrentValueOperation.replace_formulas_with_values_with_xlwings(workbook_dml)

    @staticmethod
    def replace_formulas_with_values_with_xlwings(workbook_dml: xlwings.Book) -> None:
        with logger_config.stopwatch_with_label(f"replace_formulas_with_values_with_xlwings input_excel_file_path:{workbook_dml.name}", inform_beginning=True):
            number_of_cells_updated = 0
            number_of_cells_not_updated = 0

            # Parcourir toutes les feuilles
            for sheet in workbook_dml.sheets:
                sheet = cast(xlwings.Sheet, sheet)
                number_of_cells_to_parse = len(sheet.used_range)
                with logger_config.stopwatch_with_label(label=f"Handle sheet:{sheet.name} with {number_of_cells_to_parse} cells to parse", inform_beginning=True):
                    # Parcourir toutes les cellules dans la zone utilisée de la feuille
                    for cell in sheet.used_range:

                        number_of_cells_treated = number_of_cells_updated + number_of_cells_not_updated
                        if (number_of_cells_treated) % 500 == 0:
                            logger_config.print_and_log_info(f"sheet:{sheet.name} : {number_of_cells_treated} cells treated {number_of_cells_treated/number_of_cells_to_parse*100:.2f} %")

                        # Si la cellule contient une formule
                        if cell.formula != "":
                            # Remplacer la formule par sa valeur actuelle
                            cell.value = cell.value
                            number_of_cells_updated += 1
                        else:
                            number_of_cells_not_updated += 1

            logger_config.print_and_log_info(f"{number_of_cells_updated} cells updateds and {number_of_cells_not_updated} not updated")


@dataclass
class XlWingsRemoveRangesOperation(XlWingOperationBase):
    ranges_to_remove: List[str] = field(default_factory=list)

    def do(self, workbook_dml: xlwings.Book) -> None:
        XlWingsRemoveRangesOperation.remove_ranges_with_xlwings(workbook_dml, self.ranges_to_remove)

    @staticmethod
    def remove_ranges_with_xlwings(workbook_dml: xlwings.Book, ranges_to_remove: List[str]) -> None:
        with logger_config.stopwatch_with_label(f"remove_ranges_with_xlwings input_excel_file_path:{workbook_dml.name}, ranges_to_remove:{ranges_to_remove}", inform_beginning=True):

            for range_to_remove in ranges_to_remove:
                with logger_config.stopwatch_with_label(label=f"Remove:{range_to_remove}", inform_beginning=True):
                    xlwings.Range(range_to_remove).delete()
        return


class ColumnRemovalOperationType(Enum):
    ALL_COLUMNS_AT_ONCE = auto()
    COLUMN_ONE_BY_ONE_USING_LETTER = auto()
    COLUMN_ONE_BY_ONE_USING_INDEX = auto()


@dataclass
class RemoveColumnsInstructions:
    input_excel_file_path: str
    sheet_name: str
    columns_to_remove_names: List[str]
    removal_operation_type: ColumnRemovalOperationType
    file_to_create_path: str
    assert_if_column_is_missing: bool


@dataclass
class XlWingsRemoveColumnsOperation(XlWingOperationBase):

    sheet_name: str
    columns_to_remove_names: List[str]
    assert_if_column_is_missing: bool
    removal_operation_type: ColumnRemovalOperationType = ColumnRemovalOperationType.COLUMN_ONE_BY_ONE_USING_LETTER

    def do(self, workbook_dml: xlwings.Book) -> None:
        XlWingsRemoveColumnsOperation.remove_columns_with_xlwings(
            workbook_dml=workbook_dml,
            sheet_name=self.sheet_name,
            columns_to_remove_names=self.columns_to_remove_names,
            assert_if_column_is_missing=self.assert_if_column_is_missing,
            removal_operation_type=self.removal_operation_type,
        )

    @staticmethod
    def remove_columns_with_xlwings(
        workbook_dml: xlwings.Book,
        sheet_name: str,
        columns_to_remove_names: List[str],
        assert_if_column_is_missing: bool,
        removal_operation_type: ColumnRemovalOperationType = ColumnRemovalOperationType.COLUMN_ONE_BY_ONE_USING_LETTER,
    ) -> None:

        number_of_columns_to_remove = len(columns_to_remove_names)

        with logger_config.stopwatch_with_label(
            f"remove_columns_with_xlwings input_excel_file_path:{workbook_dml.name}, sheet_name:{sheet_name}, {number_of_columns_to_remove} columns to remove: names:{columns_to_remove_names}",
            inform_beginning=True,
        ):

            sht: xlwings.Sheet = workbook_dml.sheets(sheet_name)

            # Obtenir toutes les valeurs de la première ligne
            at_beginning_headers: List[str] = sht.range("A1").expand("right").value
            logger_config.print_and_log_info(f"At beginning, {len(at_beginning_headers)} headers: {at_beginning_headers}")

            if removal_operation_type == ColumnRemovalOperationType.ALL_COLUMNS_AT_ONCE:

                all_col_initial_index_to_remove: List[int] = []
                for colum_it, column_name_to_remove in enumerate(columns_to_remove_names):
                    col_index_starting_0 = at_beginning_headers.index(column_name_to_remove)
                    all_col_initial_index_to_remove.append(col_index_starting_0)
                logger_config.print_and_log_info(f"all_col_initial_index_to_remove: {all_col_initial_index_to_remove}")

                all_col_initial_index_to_remove_sorted = list(reversed(sorted(all_col_initial_index_to_remove)))
                logger_config.print_and_log_info(f"all_col_initial_index_to_remove_sorted: {all_col_initial_index_to_remove_sorted}")

                all_columns_letters_to_remove = [xl_col_to_name(col_index) for col_index in all_col_initial_index_to_remove]
                logger_config.print_and_log_info(f"all_columns_letters_to_remove: {all_columns_letters_to_remove}")

                all_columns_letters_to_remove_range = ",".join([f"{letter}:{letter}" for letter in all_columns_letters_to_remove])
                logger_config.print_and_log_info(f"all_columns_letters_to_remove_range: {all_columns_letters_to_remove_range}")

                with logger_config.stopwatch_with_label(
                    label=f"Removing range {all_columns_letters_to_remove_range} columns {all_columns_letters_to_remove}",
                    inform_beginning=True,
                ):
                    sht.range(all_columns_letters_to_remove_range).api.Delete(DeleteShiftDirection.xlShiftToLeft)

            else:

                # Obtenir toutes les valeurs de la première ligne
                headers_found_in_excel: List[str] = sht.range("A1").expand("right").value
                logger_config.print_and_log_info(f"{len(headers_found_in_excel)} headers:{headers_found_in_excel}")

                if assert_if_column_is_missing:
                    # Check that all columns to remove are present
                    for column_to_remove_name in columns_to_remove_names:
                        assert column_to_remove_name in headers_found_in_excel, f"Column {column_to_remove_name} not found in excel among {headers_found_in_excel}"

                for colum_it, column_name_to_remove in enumerate(columns_to_remove_names):
                    # Obtenir toutes les valeurs de la première ligne
                    headers_found_in_excel = sht.range("A1").expand("right").value
                    logger_config.print_and_log_info(f"{len(headers_found_in_excel)} headers:{headers_found_in_excel}")

                    if column_name_to_remove in headers_found_in_excel:

                        # Trouver l'index de la colonne à supprimer
                        logger_config.print_and_log_info(
                            f"removing {colum_it+1}/{number_of_columns_to_remove}th column '{column_name_to_remove}' {round((colum_it+1)/number_of_columns_to_remove*100,2)}%"
                        )
                        col_index_starting_0 = headers_found_in_excel.index(column_name_to_remove)
                        col_letter = xl_col_to_name(col_index_starting_0)
                        logger_config.print_and_log_info(f"col_index:{col_index_starting_0}, col_letter:{col_letter}")
                        with logger_config.stopwatch_with_label(
                            label=f"Removing {colum_it+1}/{number_of_columns_to_remove}th column {column_name_to_remove} with index(starting0):{col_index_starting_0}, letter:{col_letter}.  {round((colum_it+1)/number_of_columns_to_remove*100,2)}%",
                            inform_beginning=False,
                        ):
                            if removal_operation_type == ColumnRemovalOperationType.COLUMN_ONE_BY_ONE_USING_LETTER:
                                col_range = f"{col_letter}:{col_letter}"

                                if sht.range(col_range).column_width == 0:
                                    logger_config.print_and_log_info(f"Attempting to delete hidden column {col_range}: show it")
                                    sht.range(col_range).column_width = 10
                                sht.range(col_range).delete()
                                # sht.range(col_range).delete(DeleteShiftDirection.xlShiftToLeft)
                            elif removal_operation_type == ColumnRemovalOperationType.COLUMN_ONE_BY_ONE_USING_INDEX:
                                col_index_starting_1 = headers_found_in_excel.index(column_name_to_remove) + 1
                                sht.range((1, col_index_starting_1), (sht.cells.last_cell.row, col_index_starting_1)).delete()  # Supprimer la colonne
                    else:
                        logger_config.print_and_log_error(f"Column {column_name_to_remove} not found in excel among {headers_found_in_excel}")

            at_end_headers: List[str] = sht.range("A1").expand("right").value
            logger_config.print_and_log_info(f"At the end, {len(at_end_headers)} headers: {at_end_headers}")


@dataclass
class XlWingsOperationsBatch:

    excel_visibility: bool
    input_excel_file_path: str
    file_to_create_path: str
    operations: List[XlWingOperationBase] = field(default_factory=list)

    def hide_excel(self) -> "XlWingsOperationsBatch":
        self.excel_visibility = False
        return self

    def show_excel(self) -> "XlWingsOperationsBatch":
        self.excel_visibility = True
        return self

    def add_operation(self, operation: XlWingOperationBase) -> "XlWingsOperationsBatch":
        self.operations.append(operation)
        return self

    def do(self) -> None:
        workbook_dml = XlWingsOpenWorkbookOperation(input_excel_file_path=self.input_excel_file_path, excel_visibility=self.excel_visibility).do()
        for operation in self.operations:
            operation.do(workbook_dml=workbook_dml)

        XlWingsSaveAndCloseWorkbookOperation(file_to_create_path=self.file_to_create_path).do(workbook_dml)


def save_and_close_workbook(workbook_dml: xlwings.Book | openpyxl.Workbook, file_path: str) -> None:

    XlWingsSaveAndCloseWorkbookOperation(file_path).do(workbook_dml)


def remove_tabs_with_openpyxl(input_excel_file_path: str, file_to_create_path: str, sheets_to_keep_names: List[str]) -> str:
    with file_utils.temporary_copy_of_file(input_excel_file_path) as temp_file_full_path:

        with logger_config.stopwatch_with_label(
            f"remove_tabs_with_xlwings input_excel_file_path:{input_excel_file_path}, file_to_create_path:{file_to_create_path}, sheets_to_keep_names:{sheets_to_keep_names}", inform_beginning=True
        ):

            with logger_config.stopwatch_with_label(label=f"Open {temp_file_full_path}", inform_beginning=True):
                workbook = openpyxl.load_workbook(temp_file_full_path)

            sheets_names = workbook.sheetnames
            number_of_initial_sheets_names = len(sheets_names)
            logger_config.print_and_log_info(f"{number_of_initial_sheets_names} Sheets found: {sheets_names}")

            for sheet_number, sheet_name in enumerate(sheets_names):
                if sheet_name in sheets_to_keep_names:
                    logger_config.print_and_log_info(f"Allowed sheet:{sheet_name}")
                elif sheet_name in EXCEL_INTERNAL_RESERVED_SHEETS_NAMES:
                    logger_config.print_and_log_info(f"ignore Excel internal reserved sheet:{sheet_name}")
                else:
                    with logger_config.stopwatch_with_label(
                        label=f"Removing {sheet_number+1}/{number_of_initial_sheets_names}th sheet:{sheet_name} : {round((sheet_number+1)/number_of_initial_sheets_names*100,2)}%",
                        inform_beginning=True,
                        monitor_ram_usage=True,
                    ):
                        try:
                            # Accéder à la feuille que l'on veut supprimer
                            sheet_to_remove = workbook[sheet_name]
                            # Supprimer la feuille
                            workbook.remove(sheet_to_remove)

                            workbook.save(file_to_create_path + "_without_" + sheet_name)
                        except Exception as exc:
                            logger_config.print_and_log_exception(type(exc))
                            logger_config.print_and_log_exception(exc)

            workbook.save(file_to_create_path)
            workbook.close()
            return file_to_create_path


def remove_tabs_with_xlwings(input_excel_file_path: str, file_to_create_path: str, sheets_to_keep_names: List[str], excel_visibility: bool = False) -> str:
    with file_utils.temporary_copy_of_file(input_excel_file_path) as temp_file_full_path:
        with logger_config.stopwatch_with_label(
            f"remove_tabs_with_xlwings input_excel_file_path:{input_excel_file_path}, file_to_create_path:{file_to_create_path}, sheets_to_keep_names:{sheets_to_keep_names}", inform_beginning=True
        ):
            workbook_dml = XlWingsOpenWorkbookOperation(input_excel_file_path=temp_file_full_path, excel_visibility=excel_visibility).do()
            XlWingsRemoveTabsOperation(sheets_to_keep_names=sheets_to_keep_names).do(workbook_dml)
            XlWingsSaveAndCloseWorkbookOperation(file_to_create_path=file_to_create_path).do(workbook_dml)
            return file_to_create_path


def set_excel_formulas_calculation_to_manual_xlwings(input_excel_file_path: str, file_to_create_path: str, excel_visibility: bool = False) -> str:
    with file_utils.temporary_copy_of_file(input_excel_file_path) as temp_file_full_path:

        with logger_config.stopwatch_with_label(
            f"set_excel_formulas_calculation_to_manual input_excel_file_path:{input_excel_file_path}, file_to_create_path:{file_to_create_path}", inform_beginning=True
        ):
            workbook_dml = XlWingsOpenWorkbookOperation(input_excel_file_path=temp_file_full_path, excel_visibility=excel_visibility).do()
            XlWingsSetExcelFormulasCalculationToManualOperation().do(workbook_dml)
            XlWingsSaveAndCloseWorkbookOperation(file_to_create_path=file_to_create_path).do(workbook_dml)
            return file_to_create_path


def remove_excel_external_links_with_xlwings(input_excel_file_path: str, file_to_create_path: str, excel_visibility: bool = False) -> str:
    with file_utils.temporary_copy_of_file(input_excel_file_path) as temp_file_full_path:

        with logger_config.stopwatch_with_label(
            f"remove_excel_external_links_with_xlwings input_excel_file_path:{input_excel_file_path}, file_to_create_path:{file_to_create_path}", inform_beginning=True
        ):
            workbook_dml = XlWingsOpenWorkbookOperation(input_excel_file_path=temp_file_full_path, excel_visibility=excel_visibility).do()
            XlWingsRemoveExcelExternalLinksOperation().do(workbook_dml)
            XlWingsSaveAndCloseWorkbookOperation(file_to_create_path=file_to_create_path).do(workbook_dml)
            return file_to_create_path


def replace_formulas_with_values_with_xlwings(input_excel_file_path: str, file_to_create_path: str, excel_visibility: bool = False) -> str:
    with file_utils.temporary_copy_of_file(input_excel_file_path) as temp_file_full_path:

        with logger_config.stopwatch_with_label(
            f"replace_formulas_with_values_with_xlwings input_excel_file_path:{input_excel_file_path}, file_to_create_path:{file_to_create_path}", inform_beginning=True
        ):
            workbook_dml = XlWingsOpenWorkbookOperation(input_excel_file_path=temp_file_full_path, excel_visibility=excel_visibility).do()
            XlWingsReplaceFormulasWithCurrentValueOperation().do(workbook_dml)
            XlWingsSaveAndCloseWorkbookOperation(file_to_create_path=file_to_create_path).do(workbook_dml)
            return file_to_create_path


def remove_ranges_with_xlwings(input_excel_file_path: str, file_to_create_path: str, ranges_to_remove: List[str], excel_visibility: bool = False) -> str:
    with file_utils.temporary_copy_of_file(input_excel_file_path) as temp_file_full_path:

        with logger_config.stopwatch_with_label(
            f"remove_ranges_with_xlwings input_excel_file_path:{input_excel_file_path}, file_to_create_path:{file_to_create_path}, ranges_to_remove:{ranges_to_remove}", inform_beginning=True
        ):
            workbook_dml = XlWingsOpenWorkbookOperation(input_excel_file_path=temp_file_full_path, excel_visibility=excel_visibility).do()
            XlWingsRemoveRangesOperation(ranges_to_remove=ranges_to_remove).do(workbook_dml)
            XlWingsSaveAndCloseWorkbookOperation(file_to_create_path=file_to_create_path).do(workbook_dml)
            return file_to_create_path


def remove_columns_with_openpyxl(
    remove_columns_instruction: RemoveColumnsInstructions,
) -> str:
    with file_utils.temporary_copy_of_file(remove_columns_instruction.input_excel_file_path) as temp_xlsm_file_full_path:
        with logger_config.stopwatch_with_label(
            f"remove_columns_with_xlwings input_excel_file_path:{remove_columns_instruction.input_excel_file_path}, sheet_name:{remove_columns_instruction.sheet_name}, file_to_create_path:{remove_columns_instruction.file_to_create_path}, columns_to_remove_names:{remove_columns_instruction.columns_to_remove_names}",
            inform_beginning=True,
        ):

            with logger_config.stopwatch_with_label(label=f"Open {temp_xlsm_file_full_path}", inform_beginning=True):
                workbook = openpyxl.load_workbook(temp_xlsm_file_full_path)

            worksheet = workbook[remove_columns_instruction.sheet_name]

            rows = worksheet.iter_rows(min_row=1, max_row=1)
            first_row = next(rows)
            at_beginning_headers = [c.value for c in first_row]

            logger_config.print_and_log_info(f"At beginning, {len(at_beginning_headers)} headers: {at_beginning_headers}")

            number_of_columns_to_remove = len(remove_columns_instruction.columns_to_remove_names)

            for colum_it, column_name_to_remove in enumerate(remove_columns_instruction.columns_to_remove_names):
                # Obtenir toutes les valeurs de la première ligne

                rows = worksheet.iter_rows(min_row=1, max_row=1)
                first_row = next(rows)
                headers_found_in_excel = [c.value for c in first_row]
                logger_config.print_and_log_info(f"{len(headers_found_in_excel)} headers:{headers_found_in_excel}")

                if column_name_to_remove in headers_found_in_excel:

                    # Trouver l'index de la colonne à supprimer
                    logger_config.print_and_log_info(f"removing {colum_it+1}/{number_of_columns_to_remove}th column '{column_name_to_remove}' {round((colum_it+1)/number_of_columns_to_remove*100,2)}%")

                    col_index_starting_0 = headers_found_in_excel.index(column_name_to_remove)
                    col_index_starting_1 = headers_found_in_excel.index(column_name_to_remove) + 1
                    col_letter = xl_col_to_name(col_index_starting_0)
                    logger_config.print_and_log_info(f"col_index:{col_index_starting_1}, col_letter:{col_letter}")
                    with logger_config.stopwatch_with_label(
                        label=f"Removing {colum_it+1}/{number_of_columns_to_remove}th column {column_name_to_remove} with index(starting0):{col_index_starting_0}, letter:{col_letter}.  {round((colum_it+1)/number_of_columns_to_remove*100,2)}%",
                        inform_beginning=False,
                    ):
                        worksheet.delete_cols(col_index_starting_1)

                else:
                    logger_config.print_and_log_error(f"Column {column_name_to_remove} not found in excel among {headers_found_in_excel}")

            save_and_close_workbook(workbook, remove_columns_instruction.file_to_create_path)
            return remove_columns_instruction.file_to_create_path


def remove_columns_with_xlwings(
    remove_columns_instruction: RemoveColumnsInstructions,
    excel_visibility: bool = False,
) -> str:
    with file_utils.temporary_copy_of_file(remove_columns_instruction.input_excel_file_path) as temp_file_full_path:
        with logger_config.stopwatch_with_label(
            f"remove_columns_with_xlwings input_excel_file_path:{remove_columns_instruction.input_excel_file_path}, sheet_name:{remove_columns_instruction.sheet_name}, file_to_create_path:{remove_columns_instruction.file_to_create_path}, columns_to_remove_names:{remove_columns_instruction.columns_to_remove_names}",
            inform_beginning=True,
        ):
            workbook_dml = XlWingsOpenWorkbookOperation(input_excel_file_path=temp_file_full_path, excel_visibility=excel_visibility).do()
            XlWingsRemoveColumnsOperation(
                sheet_name=remove_columns_instruction.sheet_name,
                columns_to_remove_names=remove_columns_instruction.columns_to_remove_names,
                removal_operation_type=remove_columns_instruction.removal_operation_type,
                assert_if_column_is_missing=remove_columns_instruction.assert_if_column_is_missing,
            ).do(workbook_dml)
            XlWingsSaveAndCloseWorkbookOperation(file_to_create_path=remove_columns_instruction.file_to_create_path).do(workbook_dml)
            return remove_columns_instruction.file_to_create_path


def xl_column_name_to_index(column_name: str) -> int:
    """Index starts 0"""
    _, col = xl_cell_to_rowcol(column_name + "1")
    assert isinstance(col, int)
    return col
