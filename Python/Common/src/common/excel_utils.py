# Standard

import time
from typing import List, cast

import openpyxl
import xlwings

# Other libraries
from logger import logger_config

# import pywintypes


EXCEL_INTERNAL_RESERVED_SHEETS_NAMES = ["Register"]

EXCEL_FILE_EXTENSION = ".xlsx"


def save_and_close_workbook(workbook_dml: xlwings.Book | openpyxl.Workbook, file_path: str) -> str:

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


def remove_tabs_with_xlwings(input_excel_file_path: str, file_to_create_path: str, sheets_to_keep_names: List[str]) -> str:

    with logger_config.stopwatch_with_label(label=f"Open {input_excel_file_path}", inform_beginning=True):
        workbook_dml = xlwings.Book(input_excel_file_path)

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

    return save_and_close_workbook(workbook_dml, file_to_create_path)


def set_excel_formulas_calculation_to_manual(input_excel_file_path: str, file_to_create_path: str) -> str:
    with logger_config.stopwatch_with_label(label=f"Open: {input_excel_file_path}", inform_beginning=True):
        workbook_dml = xlwings.Book(input_excel_file_path)

    logger_config.print_and_log_info("set formulas calculations to manual to improve speed")
    workbook_dml.app.calculation = "manual"
    return save_and_close_workbook(workbook_dml, file_to_create_path)


def remove_excel_external_links_with_xlwings(input_excel_file_path: str, file_to_create_path: str) -> str:

    with logger_config.stopwatch_with_label(label=f"Open: {input_excel_file_path}", inform_beginning=True):
        workbook_dml = xlwings.Book(input_excel_file_path)

    external_links_sources = workbook_dml.api.LinkSources()

    logger_config.print_and_log_info(f"{len(external_links_sources)} links found: {external_links_sources}")

    for external_links_source_name in external_links_sources:
        with logger_config.stopwatch_with_label(label=f"Removing link:{external_links_source_name}"):
            workbook_dml.api.BreakLink(Name=external_links_source_name, Type=1)  # Type=1 pour les liaisons de type Excel

    return save_and_close_workbook(workbook_dml, file_to_create_path)


def replace_formulas_with_values_with_xlwings(input_excel_file_path: str, file_to_create_path: str) -> str:

    with logger_config.stopwatch_with_label(label=f"Open: {input_excel_file_path}", inform_beginning=True):
        workbook_dml = xlwings.Book(input_excel_file_path)

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

    return save_and_close_workbook(workbook_dml, file_to_create_path)


def remove_ranges_with_xlwings(input_excel_file_path: str, file_to_create_path: str, ranges_to_remove: List[str]) -> str:

    with logger_config.stopwatch_with_label(label=f"Open: {input_excel_file_path}", inform_beginning=True):
        workbook_dml = xlwings.Book(input_excel_file_path)

    for range_to_remove in ranges_to_remove:
        with logger_config.stopwatch_with_label(label=f"Remove:{range_to_remove}", inform_beginning=True):
            xlwings.Range(range_to_remove).delete()

    return save_and_close_workbook(workbook_dml, file_to_create_path)


def remove_columns_with_xlwings(input_excel_file_path: str, sheet_name: str, file_to_create_path: str, columns_to_remove_names: List[str]) -> str:

    with logger_config.stopwatch_with_label(label=f"Open: {input_excel_file_path}", inform_beginning=True):
        workbook_dml = xlwings.Book(input_excel_file_path)

    sht = workbook_dml.sheets[sheet_name]

    for column_name_to_remove in columns_to_remove_names:

        # Obtenir toutes les valeurs de la première ligne
        headers = sht.range("A1").expand("right").value
        logger_config.print_and_log_info(f"{len(headers)} headers:{headers}")

        # Trouver l'index de la colonne à supprimer
        logger_config.print_and_log_error(f"removing column '{column_name_to_remove}'")
        col_index = headers.index(column_name_to_remove) + 1  # Ajouter 1 car Excel utilise des index de base 1
        with logger_config.stopwatch_with_label(label=f"Removing column {column_name_to_remove} with index {col_index}", inform_beginning=True):
            sht.range((1, col_index), (sht.cells.last_cell.row, col_index)).delete()  # Supprimer la colonne

    return save_and_close_workbook(workbook_dml, file_to_create_path)
