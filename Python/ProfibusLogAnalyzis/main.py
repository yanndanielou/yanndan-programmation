# -*-coding:Utf-8 -*
"""Main"""

from dataclasses import dataclass, field
import os
import gzip
import datetime
from typing import List, Optional

from logger import logger_config

import logging
import param

from shutthebox.application import Application, SimulationRequest
from shutthebox.dices import Dice
from shutthebox.gui import TreeViewApp

import numpy


import os
import gzip
import datetime
from typing import List


@dataclass
class CabLogs:
    log_files_directory_path: str
    log_files_prefix: str
    label: str = ""
    encoding: str = "utf-8"


@dataclass
class ProfibusLogFile:
    unusedt: int


@dataclass
class ProfibusLogSession:
    log_lines: list["ProfibusLogLine"] = field(default_factory=list)


@dataclass
class ProfibusLogLine:
    timestamp: datetime.datetime
    log_value: str
    file_name: str
    file_line_number: int
    log_session: ProfibusLogSession


def read_log_file(file_path: str, encoding: str) -> List[ProfibusLogSession]:
    log_sessions: List[ProfibusLogSession] = []
    log_session: Optional[ProfibusLogSession] = None
    logger_config.print_and_log_info(f"read_log_file: {file_path}")
    if file_path.endswith(".gz"):
        with gzip.open(file_path, "rt") as f:
            lines = f.readlines()
    else:
        with open(file_path, "r", encoding=encoding) as f:
            lines = f.readlines()

    logger_config.print_and_log_info(f"{len(lines)} lines to process in {file_path}")
    for file_line_number, line in enumerate(lines, start=1):

        file_name = os.path.basename(file_path)

        if line.startswith("\x00"):
            logger_config.print_and_log_error(f"Null characters found at beginning of {file_name} : {file_line_number}. Line: {line}")
            line = line.lstrip("\x00")

        parts = line.split(" ", 3)
        if len(parts) < 4:
            continue
        timestamp_str = f"{parts[0]} {parts[1]}"
        try:
            timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S:%f")
            log_value = parts[3].strip()
            profibus_log_line = ProfibusLogLine(timestamp=timestamp, log_value=log_value, file_name=file_name, file_line_number=file_line_number, log_session=log_session)
            if log_session is None:
                log_session = ProfibusLogSession()
                log_sessions.append(log_session)
            log_session.log_lines.append(profibus_log_line)
        except ValueError:
            logger_config.print_and_log_error(f"Skipping line with invalid timestamp: {line.strip()}")
            log_session = None

    return log_sessions


def detect_missing_logs(all_log_sessions: List[ProfibusLogSession]):
    if not all_log_sessions:
        logger_config.print_and_log_error("No log session found.")
        return

    # log_lines.sort(key=lambda x: x.timestamp)

    for log_session in all_log_sessions:
        if not all_log_sessions:
            logger_config.print_and_log_error("No log lines found.")
            break

        previous_time = log_session.log_lines[0].timestamp

        for log_line in log_session.log_lines:
            if log_line.timestamp - previous_time > param.PERIOD_TO_DETECT_LACK_OF_LOGS:
                logger_config.print_and_log_info(f"Missing logs detected between {previous_time} and {log_line.timestamp}")
            previous_time = log_line.timestamp


def process_all_cabs_logs(cabs_logs: List[CabLogs]):
    for cab_logs in cabs_logs:
        logger_config.print_and_log_info(f"Process cabs logs {cab_logs.label}")
        process_all_logs(cab_logs)


def process_all_logs(cab_log: CabLogs) -> None:
    all_log_sessions: List[ProfibusLogSession] = []

    log_folder = cab_log.log_files_directory_path

    for root, _, files in os.walk(log_folder):
        for file in files:
            if file.startswith(cab_log.log_files_prefix):
                file_path = os.path.join(root, file)
                all_log_sessions.extend(read_log_file(file_path, cab_log.encoding))

    detect_missing_logs(all_log_sessions)


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application duration"):
        logger_config.configure_logger_with_random_log_file_suffix("ProfibusLogAnalyzis", log_file_extension="log", logger_level=logging.DEBUG)

        # Example usage

        process_all_cabs_logs(
            cabs_logs=[
                CabLogs(
                    log_files_directory_path=r"D:\GitHub\yanndanielou-programmation\Python\ProfibusLogAnalyzis\Input\ppn_250210\ppn\cab 1A", log_files_prefix="cab", label="cab 1A", encoding="ANSI"
                ),
                CabLogs(
                    log_files_directory_path=r"D:\GitHub\yanndanielou-programmation\Python\ProfibusLogAnalyzis\Input\ppn_250210\ppn\cab 1B", log_files_prefix="cab", label="cab 1B", encoding="ANSI"
                ),
                CabLogs(
                    log_files_directory_path=r"D:\GitHub\yanndanielou-programmation\Python\ProfibusLogAnalyzis\Input\ppn_250210\ppn\cab 2A", log_files_prefix="cab", label="cab 2A", encoding="ANSI"
                ),
                CabLogs(
                    log_files_directory_path=r"D:\GitHub\yanndanielou-programmation\Python\ProfibusLogAnalyzis\Input\ppn_250210\ppn\cab 2B", log_files_prefix="cab", label="cab 2B", encoding="ANSI"
                ),
            ]
        )

        # log_files_directory_path=r"C:\Users\fr232487\Downloads\2025-04-05 passerelle profibus\plateforme_bord\log_ppn_cab2_A\log", log_files_prefix="debug.log", label="Bord log_ppn_cab2_A"

        logger_config.print_and_log_info("End. Nominal end of application")


if __name__ == "__main__":
    # sys.argv[1:]
    main()
