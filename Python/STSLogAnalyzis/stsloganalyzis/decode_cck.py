import csv
import os
import datetime
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, cast, Self

import re


from logger import logger_config

# CONTENT_OF_FIELD_IN_CASE_OF_DECODING_ERROR = "!!! Decoding Error !!!"

LIAISON_PATTERN_STR = ".*(?P<liaison_full_name>Liaison (?P<liaison_id>\d+A?B?)).*"
LIAISON_PATTERN = re.compile(LIAISON_PATTERN_STR)


@dataclass
class CckMproTraceLibrary:
    all_processed_lines: List["CckMproTraceLine"] = field(default_factory=list)
    all_processed_files: List["CckMproTraceFile"] = field(default_factory=list)

    def load_folder(self, folder_full_path: str) -> Self:
        for dirpath, dirnames, filenames in os.walk(folder_full_path):
            for file_name in filenames:
                cck_file = CckMproTraceFile(parent_folder_full_path=dirpath, file_name=file_name)
                self.all_processed_files.append(cck_file)
                self.all_processed_lines += cck_file.all_processed_lines
        return self


pass


@dataclass
class CckMproTraceFile:
    parent_folder_full_path: str
    file_name: str
    all_processed_lines: List["CckMproTraceLine"] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.file_full_path = self.parent_folder_full_path + "/" + self.file_name
        with logger_config.stopwatch_with_label(f"Open and read CCK Mpro trace file lines {self.file_full_path}"):
            with open(self.file_full_path, mode="r", encoding="ANSI") as file:
                all_raw_lines = file.readlines()
                logger_config.print_and_log_info(to_print_and_log=f"File {self.file_full_path} has {len(all_raw_lines)} lines", do_not_print=True)
                for line_number, line in enumerate(all_raw_lines):
                    processed_line = CckMproTraceLine(parent_file=self, full_raw_line=line)
                    self.all_processed_lines.append(processed_line)

        logger_config.print_and_log_info(f"{self.file_full_path}: {len(self.all_processed_lines)} lines found")
        assert self.all_processed_lines, f"{self.file_full_path} is empty"


@dataclass
class CckMproTraceLine:
    parent_file: CckMproTraceFile
    full_raw_line: str

    def __post_init__(self) -> None:
        self.raw_date_str = self.full_raw_line[1:23]
        self.year = int(self.raw_date_str[:4])
        self.month = int(self.raw_date_str[5:7])
        self.day = int(self.raw_date_str[8:10])
        self.hour = int(self.raw_date_str[11:13])
        self.minute = int(self.raw_date_str[14:16])
        self.second = int(self.raw_date_str[17:19])
        self.millisecond = int(self.raw_date_str[20:22]) * 10

        match_liaison_pattern = LIAISON_PATTERN.match(self.full_raw_line)
        self.liaison_full_name = match_liaison_pattern.group("liaison_full_name") if match_liaison_pattern else None
        self.liaison_id = match_liaison_pattern.group("liaison_id") if match_liaison_pattern else None
        # self.liaison_name

        # self./
        self.decoded_timestamp = datetime.datetime(year=self.year, month=self.month, day=self.day, hour=self.hour, minute=self.minute, second=self.second, microsecond=self.millisecond * 1000)
        pass
