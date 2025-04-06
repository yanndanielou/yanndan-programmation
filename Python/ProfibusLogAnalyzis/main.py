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
    log_unsupported_lines = False


@dataclass
class ProfibusLogFile:
    unusedt: int


@dataclass
class ProfibusLogSession:
    log_lines: list["ProfibusLogLine"] = field(default_factory=list)
    going_back_to_past_events: List["GoingBackToPast"] = field(default_factory=list)
    missing_logs_events: List["MissingLogs"] = field(default_factory=list)


@dataclass
class GoingBackToPast:
    before_going_back_to_past_log_line: "ProfibusLogLine"
    after_going_back_to_past_log_line: "ProfibusLogLine"


@dataclass
class MissingLogs:
    previous_log_line: "ProfibusLogLine"
    next_log_line: "ProfibusLogLine"
    missing_log_period: datetime.timedelta


@dataclass
class ProfibusLogLine:
    timestamp: datetime.datetime
    log_value: str
    file_name: str
    file_line_number: int
    log_session: ProfibusLogSession


def read_log_file(file_path: str, cab_log: CabLogs) -> List[ProfibusLogSession]:
    log_sessions: List[ProfibusLogSession] = []
    log_session: Optional[ProfibusLogSession] = None
    logger_config.print_and_log_info(f"read_log_file: {file_path}")
    if file_path.endswith(".gz"):
        with gzip.open(file_path, "rt") as f:
            lines = f.readlines()
    else:
        with open(file_path, "r", encoding=cab_log.encoding) as f:
            lines = f.readlines()

    logger_config.print_and_log_info(f"{len(lines)} lines to process in {file_path}")
    for file_line_number, line in enumerate(lines, start=1):

        file_name = os.path.basename(file_path)

        if line.startswith("\x00"):
            if cab_log.log_unsupported_lines:
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
            if cab_log.log_unsupported_lines:
                logger_config.print_and_log_error(f"Skipping line {file_line_number} in file {file_path} with invalid timestamp: {line.strip()}")
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

        previous_line = None

        for log_line in log_session.log_lines:

            if previous_line:
                if log_line.timestamp < previous_line.timestamp:
                    # logger_config.print_and_log_info(f"Going back to past logs detected between {previous_line.timestamp} and {log_line.timestamp}")
                    log_session.going_back_to_past_events.append(GoingBackToPast(before_going_back_to_past_log_line=previous_line, after_going_back_to_past_log_line=log_line))

                if log_line.timestamp - previous_line.timestamp > param.PERIOD_TO_DETECT_LACK_OF_LOGS:
                    # logger_config.print_and_log_info(f"Missing logs detected between {previous_line.timestamp} and {log_line.timestamp}")
                    log_session.missing_logs_events.append(MissingLogs(previous_log_line=previous_line, next_log_line=log_line, missing_log_period=log_line.timestamp - previous_line.timestamp))
            previous_line = log_line


def process_all_cabs_logs(cabs_logs: List[CabLogs]) -> List[ProfibusLogSession]:
    all_log_sessions: List[ProfibusLogSession] = []
    for cab_logs in cabs_logs:
        logger_config.print_and_log_info(f"Process cabs logs {cab_logs.label}")
        all_log_sessions.extend(process_all_logs(cab_logs))
    return all_log_sessions


def process_all_logs(cab_log: CabLogs) -> List[ProfibusLogSession]:
    all_log_sessions: List[ProfibusLogSession] = []

    log_folder = cab_log.log_files_directory_path

    for root, _, files in os.walk(log_folder):
        for file in files:
            if file.startswith(cab_log.log_files_prefix):
                file_path = os.path.join(root, file)
                all_log_sessions.extend(read_log_file(file_path, cab_log))

    detect_missing_logs(all_log_sessions)

    return all_log_sessions


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application duration"):
        logger_config.configure_logger_with_random_log_file_suffix("ProfibusLogAnalyzis", log_file_extension="log", logger_level=logging.DEBUG)

        # Example usage

        log_sessions: List[ProfibusLogSession] = process_all_cabs_logs(
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

        all_going_back_to_past_events: List[GoingBackToPast] = [event for session in log_sessions for event in session.going_back_to_past_events]
        all_missing_logs_events: List[MissingLogs] = [event for session in log_sessions for event in session.missing_logs_events]

        logger_config.print_and_log_info(f"{len(all_going_back_to_past_events) } GoingBackToPast events and {len(all_missing_logs_events)} MissingLogs")

        # log_files_directory_path=r"C:\Users\fr232487\Downloads\2025-04-05 passerelle profibus\plateforme_bord\log_ppn_cab2_A\log", log_files_prefix="debug.log", label="Bord log_ppn_cab2_A"

        logger_config.print_and_log_info("End. Nominal end of application")


if __name__ == "__main__":
    # sys.argv[1:]
    main()
