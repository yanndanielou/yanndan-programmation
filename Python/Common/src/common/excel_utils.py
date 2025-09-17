# Standard

import time
from typing import List, cast

import openpyxl
import xlwings

# Other libraries
from logger import logger_config
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# import pywintypes
from xlsxwriter.utility import xl_cell_to_rowcol


EXCEL_INTERNAL_RESERVED_SHEETS_NAMES = ["Register"]

EXCEL_FILE_EXTENSION = ".xlsx"


class XlWingOperationBase(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def do(self) -> None:
        pass


@dataclass
class XlWingsOpenWorkbookOperation:
    input_excel_file_path: str
    excel_visibility: bool

    def do(self) -> xlwings.Book:
        return XlWingsOpenWorkbookOperation.open_workbook(self.input_excel_file_path, self.excel_visibility)

    @staticmethod
    def open_workbook(input_excel_file_path: str, excel_visibility: bool) -> xlwings.Book:
        with logger_config.stopwatch_with_label(label=f"Open {input_excel_file_path}", inform_beginning=True):

            with xlwings.App(visible=excel_visibility):
                workbook_dml = xlwings.Book(input_excel_file_path)
        return workbook_dml


@dataclass
class XlWingsSaveAndCloseWorkbookOperation(XlWingOperationBase):
    workbook_dml: xlwings.Book | openpyxl.Workbook
    file_path: str

    def do(self) -> None:
        XlWingsSaveAndCloseWorkbookOperation.save_and_close_workbook(self.workbook_dml, self.file_path)

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
    workbook_dml: xlwings.Book
    sheets_to_keep_names: List[str]

    def do(self) -> None:
        XlWingsRemoveTabsOperation.remove_tabs_with_xlwings(self.workbook_dml, self.sheets_to_keep_names)

    @staticmethod
    def remove_tabs_with_xlwings(workbook_dml: xlwings.Book, sheets_to_keep_names: List[str]) -> None:
        with logger_config.stopwatch_with_label(f"remove_tabs_with_xlwings input_excel_file_path:{workbook_dml.name}, sheets_to_keep_names:{sheets_to_keep_names}", inform_beginning=True):

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
    workbook_dml: xlwings.Book

    def do(self) -> None:
        XlWingsSetExcelFormulasCalculationToManualOperation.set_excel_formulas_calculation_to_manual_xlwings(self.workbook_dml)

    @staticmethod
    def set_excel_formulas_calculation_to_manual_xlwings(workbook_dml: xlwings.Book) -> None:
        with logger_config.stopwatch_with_label(f"set_excel_formulas_calculation_to_manual input_excel_file_path:{workbook_dml.name}", inform_beginning=True):
            logger_config.print_and_log_info("set formulas calculations to manual to improve speed")
            workbook_dml.app.calculation = "manual"


@dataclass
class XlWingsRemoveExcelExternalLinksOperation(XlWingOperationBase):
    workbook_dml: xlwings.Book

    def do(self) -> None:
        XlWingsRemoveExcelExternalLinksOperation.remove_excel_external_links_with_xlwings(self.workbook_dml)

    @staticmethod
    def remove_excel_external_links_with_xlwings(workbook_dml: xlwings.Book) -> None:
        with logger_config.stopwatch_with_label(f"remove_excel_external_links_with_xlwings input_excel_file_path:{workbook_dml.name}", inform_beginning=True):
            external_links_sources = workbook_dml.api.LinkSources()

            logger_config.print_and_log_info(f"{len(external_links_sources)} links found: {external_links_sources}")

            for external_links_source_name in external_links_sources:
                with logger_config.stopwatch_with_label(label=f"Removing link:{external_links_source_name}"):
                    workbook_dml.api.BreakLink(Name=external_links_source_name, Type=1)  # Type=1 pour les liaisons de type Excel


@dataclass
class XlWingsReplaceFormulasWithCurrentValueOperation(XlWingOperationBase):
    workbook_dml: xlwings.Book

    def do(self) -> None:
        XlWingsReplaceFormulasWithCurrentValueOperation.replace_formulas_with_values_with_xlwings(self.workbook_dml)

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
    workbook_dml: xlwings.Book
    ranges_to_remove: List[str] = field(default_factory=list)

    def do(self) -> None:
        XlWingsRemoveRangesOperation.remove_ranges_with_xlwings(self.workbook_dml, self.ranges_to_remove)

    @staticmethod
    def remove_ranges_with_xlwings(workbook_dml: xlwings.Book, ranges_to_remove: List[str]) -> None:
        with logger_config.stopwatch_with_label(f"remove_ranges_with_xlwings input_excel_file_path:{workbook_dml.name}, ranges_to_remove:{ranges_to_remove}", inform_beginning=True):

            for range_to_remove in ranges_to_remove:
                with logger_config.stopwatch_with_label(label=f"Remove:{range_to_remove}", inform_beginning=True):
                    xlwings.Range(range_to_remove).delete()
        return


@dataclass
class XlWingsRemoveColumnsOperation(XlWingOperationBase):
    workbook_dml: xlwings.Book
    sheet_name: str
    columns_to_remove_names: List[str]

    def do(self) -> None:
        XlWingsRemoveColumnsOperation.remove_columns_with_xlwings(self.workbook_dml, self.sheet_name, self.columns_to_remove_names)

    @staticmethod
    def remove_columns_with_xlwings(workbook_dml: xlwings.Book, sheet_name: str, columns_to_remove_names: List[str]) -> None:

        with logger_config.stopwatch_with_label(
            f"remove_columns_with_xlwings input_excel_file_path:{workbook_dml.name}, sheet_name:{sheet_name}, columns_to_remove_names:{columns_to_remove_names}",
            inform_beginning=True,
        ):

            sht = workbook_dml.sheets[sheet_name]

            number_of_columns_to_remove = len(columns_to_remove_names)
            for colum_it, column_name_to_remove in enumerate(columns_to_remove_names):

                # Obtenir toutes les valeurs de la première ligne
                headers = sht.range("A1").expand("right").value
                logger_config.print_and_log_info(f"{len(headers)} headers:{headers}")

                # Trouver l'index de la colonne à supprimer
                logger_config.print_and_log_info(f"removing {colum_it+1}/{number_of_columns_to_remove}th column '{column_name_to_remove}' {round((colum_it+1)/number_of_columns_to_remove*100,2)}%")
                col_index = headers.index(column_name_to_remove) + 1  # Ajouter 1 car Excel utilise des index de base 1
                with logger_config.stopwatch_with_label(
                    label=f"Removing {colum_it+1}/{number_of_columns_to_remove}th column {column_name_to_remove} with index {col_index}.  {round((colum_it+1)/number_of_columns_to_remove*100,2)}%",
                    inform_beginning=False,
                ):
                    sht.range((1, col_index), (sht.cells.last_cell.row, col_index)).delete()  # Supprimer la colonne


def save_and_close_workbook(workbook_dml: xlwings.Book | openpyxl.Workbook, file_path: str) -> None:

    XlWingsSaveAndCloseWorkbookOperation(workbook_dml, file_path).do()


def remove_tabs_with_openpyxl(input_excel_file_path: str, file_to_create_path: str, sheets_to_keep_names: List[str], excel_visibility: bool = False) -> str:
    with logger_config.stopwatch_with_label(
        f"remove_tabs_with_xlwings input_excel_file_path:{input_excel_file_path}, file_to_create_path:{file_to_create_path}, sheets_to_keep_names:{sheets_to_keep_names}", inform_beginning=True
    ):
        with logger_config.stopwatch_with_label(label=f"Open {input_excel_file_path}", inform_beginning=True):
            workbook = openpyxl.load_workbook(input_excel_file_path)

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
    with logger_config.stopwatch_with_label(
        f"remove_tabs_with_xlwings input_excel_file_path:{input_excel_file_path}, file_to_create_path:{file_to_create_path}, sheets_to_keep_names:{sheets_to_keep_names}", inform_beginning=True
    ):
        workbook_dml = XlWingsOpenWorkbookOperation(input_excel_file_path=input_excel_file_path, excel_visibility=excel_visibility).do()
        XlWingsRemoveTabsOperation(workbook_dml=workbook_dml, sheets_to_keep_names=sheets_to_keep_names).do()
        XlWingsSaveAndCloseWorkbookOperation(workbook_dml=workbook_dml, file_path=file_to_create_path).do()
        return file_to_create_path


def set_excel_formulas_calculation_to_manual_xlwings(input_excel_file_path: str, file_to_create_path: str, excel_visibility: bool = False) -> str:
    with logger_config.stopwatch_with_label(
        f"set_excel_formulas_calculation_to_manual input_excel_file_path:{input_excel_file_path}, file_to_create_path:{file_to_create_path}", inform_beginning=True
    ):
        workbook_dml = XlWingsOpenWorkbookOperation(input_excel_file_path=input_excel_file_path, excel_visibility=excel_visibility).do()
        XlWingsSetExcelFormulasCalculationToManualOperation(workbook_dml=workbook_dml).do()
        XlWingsSaveAndCloseWorkbookOperation(workbook_dml=workbook_dml, file_path=file_to_create_path).do()
        return file_to_create_path


def remove_excel_external_links_with_xlwings(input_excel_file_path: str, file_to_create_path: str, excel_visibility: bool = False) -> str:
    with logger_config.stopwatch_with_label(
        f"remove_excel_external_links_with_xlwings input_excel_file_path:{input_excel_file_path}, file_to_create_path:{file_to_create_path}", inform_beginning=True
    ):
        workbook_dml = XlWingsOpenWorkbookOperation(input_excel_file_path=input_excel_file_path, excel_visibility=excel_visibility).do()
        XlWingsRemoveExcelExternalLinksOperation(workbook_dml=workbook_dml).do()
        XlWingsSaveAndCloseWorkbookOperation(workbook_dml=workbook_dml, file_path=file_to_create_path).do()
        return file_to_create_path


def replace_formulas_with_values_with_xlwings(input_excel_file_path: str, file_to_create_path: str, excel_visibility: bool = False) -> str:
    with logger_config.stopwatch_with_label(
        f"replace_formulas_with_values_with_xlwings input_excel_file_path:{input_excel_file_path}, file_to_create_path:{file_to_create_path}", inform_beginning=True
    ):
        workbook_dml = XlWingsOpenWorkbookOperation(input_excel_file_path=input_excel_file_path, excel_visibility=excel_visibility).do()
        XlWingsReplaceFormulasWithCurrentValueOperation(workbook_dml=workbook_dml).do()
        XlWingsSaveAndCloseWorkbookOperation(workbook_dml=workbook_dml, file_path=file_to_create_path).do()
        return file_to_create_path


def remove_ranges_with_xlwings(input_excel_file_path: str, file_to_create_path: str, ranges_to_remove: List[str], excel_visibility: bool = False) -> str:
    with logger_config.stopwatch_with_label(
        f"remove_ranges_with_xlwings input_excel_file_path:{input_excel_file_path}, file_to_create_path:{file_to_create_path}, ranges_to_remove:{ranges_to_remove}", inform_beginning=True
    ):
        workbook_dml = XlWingsOpenWorkbookOperation(input_excel_file_path=input_excel_file_path, excel_visibility=excel_visibility).do()
        XlWingsRemoveRangesOperation(workbook_dml=workbook_dml, ranges_to_remove=ranges_to_remove).do()
        XlWingsSaveAndCloseWorkbookOperation(workbook_dml=workbook_dml, file_path=file_to_create_path).do()
        return file_to_create_path


def remove_columns_with_xlwings(input_excel_file_path: str, sheet_name: str, file_to_create_path: str, columns_to_remove_names: List[str], excel_visibility: bool = False) -> str:

    with logger_config.stopwatch_with_label(
        f"remove_columns_with_xlwings input_excel_file_path:{input_excel_file_path}, sheet_name:{sheet_name}, file_to_create_path:{file_to_create_path}, columns_to_remove_names:{columns_to_remove_names}",
        inform_beginning=True,
    ):
        workbook_dml = XlWingsOpenWorkbookOperation(input_excel_file_path=input_excel_file_path, excel_visibility=excel_visibility).do()
        XlWingsRemoveColumnsOperation(workbook_dml=workbook_dml, sheet_name=sheet_name, columns_to_remove_names=columns_to_remove_names).do()
        XlWingsSaveAndCloseWorkbookOperation(workbook_dml=workbook_dml, file_path=file_to_create_path).do()
        return file_to_create_path


def xl_column_name_to_index(column_name: str) -> int:
    """Index starts 0"""
    _, col = xl_cell_to_rowcol(column_name + "1")
    assert isinstance(col, int)
    return col
