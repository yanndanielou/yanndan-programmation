# -*-coding:Utf-8 -*

# parse folder
import glob

# For Excel to Csv
import pandas


# For Excel
from openpyxl import load_workbook

# For logs
import random
import logging
import os
import sys

import param

# To get line number for logs
from inspect import currentframe, getframeinfo
import inspect

# Dates
import datetime
import time

# For args
import argparse

import getopt

# Regex
import re

from logger import logger_config

# wordContainingUnderscoreToTranformRegexCompiledPattern = re.compile(wordContainingUnderscoreToTranformRegexPatternAsString)


def transform_text_to_valid_excel_date(initial_text: str) -> str:
    transformed_text: str = initial_text.replace("UTC+1", "")
    transformed_text = transformed_text.replace("UTC+2", "")
    transformed_text = transformed_text.replace("à ", "")
    return transformed_text


def get_list_of_excel_files_names() -> list[str]:
    dir_path = r"*.xls*"
    res = glob.glob(dir_path)
    return res


def transform_excel_file_to_csv_files(excel_file_name_with_extension: str) -> None:

    logger_config.print_and_log_info("Load workbook:" + excel_file_name_with_extension)
    workbook = load_workbook(filename=excel_file_name_with_extension)

    excel_file_name_without_extension = excel_file_name_with_extension.split(".")[0]

    workbook_sheetnames = workbook.sheetnames
    logger_config.print_and_log_info(
        "Workbook:" + excel_file_name_without_extension + " has following sheets:" + str(workbook_sheetnames)
    )

    if not os.path.exists(excel_file_name_without_extension):
        logger_config.print_and_log_info("Create folder " + excel_file_name_without_extension)
        os.makedirs(excel_file_name_without_extension)

    for workbookSheetName in workbook_sheetnames:
        read_file = pandas.read_excel(excel_file_name_with_extension, sheet_name=workbookSheetName)
        output_csv_file = excel_file_name_without_extension + "/" + workbookSheetName + ".csv"
        logger_config.print_and_log_info("Extract sheet " + workbookSheetName + " to " + output_csv_file)
        read_file.to_csv(output_csv_file, sep=param.csv_separator, index=None, header=True)


def transform_all_excel_files_to_csv_files() -> None:

    list_of_excel_files_names = get_list_of_excel_files_names()

    logger_config.print_and_log_info(
        "Number of excel files found:" + str(len(list_of_excel_files_names)) + " : " + str(list_of_excel_files_names)
    )

    for excel_file_name in list_of_excel_files_names:
        transform_excel_file_to_csv_files(excel_file_name)


def main() -> None:
    log_file_name = "TransformExcelToCsvFiles" + "_" + str(random.randrange(100000)) + ".log"

    # log_file_name = 'TransformCodeToCamelCase' + "." +  str(random.randrange(10000)) + ".log"
    logger_config.configure_logger_with_random_log_file_suffix(log_file_name)

    logger_config.print_and_log_info("Start application. Log file name: " + log_file_name)
    transform_all_excel_files_to_csv_files()
    logger_config.print_and_log_info("End application")


if __name__ == "__main__":
    main()
