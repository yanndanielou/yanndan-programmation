import datetime
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Self, Tuple

import matplotlib.pyplot as plt
import plotly.graph_objects as go
from common import file_name_utils, string_utils, custom_iterator
from logger import logger_config
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

# CONTENT_OF_FIELD_IN_CASE_OF_DECODING_ERROR = "!!! Decoding Error !!!"


@dataclass
class TerminalTechniqueArchivesMaintLibrary:
    name: str
    all_processed_lines: List["TerminalTechniqueArchivesMaintLogLine"] = field(default_factory=list)
    all_processed_files: List["TerminalTechniqueArchivesMaintFile"] = field(default_factory=list)

    def load_folder(self, folder_full_path: str) -> Self:
        for dirpath, dirnames, filenames in os.walk(folder_full_path):
            for file_name in filenames:
                file = TerminalTechniqueArchivesMaintFile(parent_folder_full_path=dirpath, file_name=file_name, library=self)
                self.all_processed_files.append(file)
                self.all_processed_lines += file.all_processed_lines

                assert self.all_processed_lines
        assert self.all_processed_lines

        return self


@dataclass
class TerminalTechniqueArchivesMaintFile:
    parent_folder_full_path: str
    file_name: str
    library: "TerminalTechniqueArchivesMaintLibrary"
    all_processed_lines: List["TerminalTechniqueArchivesMaintLogLine"] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.file_full_path = self.parent_folder_full_path + "/" + self.file_name

        with logger_config.stopwatch_with_label(f"Open and read file  {self.file_full_path}", inform_beginning=True):
            with open(self.file_full_path, mode="r", encoding="ANSI") as file:
                all_raw_lines = file.readlines()
                logger_config.print_and_log_info(to_print_and_log=f"File {self.file_full_path} has {len(all_raw_lines)} lines")
                for line_number, line in enumerate(all_raw_lines):
                    if len(line) > 3:
                        processed_line = TerminalTechniqueArchivesMaintLogLine(parent_file=self, full_raw_line=line, line_number=line_number)
                        self.all_processed_lines.append(processed_line)


@dataclass
class TerminalTechniqueArchivesMaintLogLine:
    parent_file: TerminalTechniqueArchivesMaintFile
    full_raw_line: str
    line_number: int

    def __post_init__(self) -> None:
        self.raw_date_str = self.full_raw_line[0:22]

        # 2025-12-29	01:45:53.30
        self.raw_date_str_with_microseconds = self.raw_date_str + "0000"
        self.decoded_timestamp = datetime.datetime.strptime(self.raw_date_str_with_microseconds + "0", "%Y-%m-%d	%H:%M:%S.%f")
