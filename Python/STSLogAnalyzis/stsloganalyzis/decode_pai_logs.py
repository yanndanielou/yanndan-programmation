import datetime
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Self, Tuple, cast

import matplotlib.pyplot as plt
import plotly.graph_objects as go
from common import file_name_utils, string_utils, custom_iterator
from logger import logger_config
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

# CONTENT_OF_FIELD_IN_CASE_OF_DECODING_ERROR = "!!! Decoding Error !!!"


class AlarmLineType(Enum):
    EVT_ALA = auto()
    DEB_ALA = auto()
    FIN_ALA = auto()
    CSI = auto()


@dataclass
class TerminalTechniqueAlarm:
    raise_line: "TerminalTechniqueArchivesMaintLogLine"
    full_text: str
    alarm_type: AlarmLineType

    def __post_init__(self) -> None:
        self.end_alarm_line: Optional["TerminalTechniqueArchivesMaintLogLine"] = None
        self.equipment_name = self.full_text.split(" ")[0]
        pass


@dataclass
class TerminalTechniqueCsiAlarm(TerminalTechniqueAlarm):
    pass


@dataclass
class TerminalTechniqueEventAlarm(TerminalTechniqueAlarm):
    pass


@dataclass
class TerminalTechniqueClosableAlarm(TerminalTechniqueAlarm):

    def __post_init__(self) -> None:
        super().__post_init__()
        self.end_alarm_line: Optional["TerminalTechniqueArchivesMaintLogLine"] = None


@dataclass
class SaatMissingAcknowledgmentTerminalTechniqueAlarm(TerminalTechniqueEventAlarm):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.chaine = self.raise_line.alarm_full_text.split(",")[3]
        self.repetition = int(self.raise_line.alarm_full_text.split(",")[4][0])


@dataclass
class TerminalTechniqueArchivesMaintLibrary:
    name: str

    def __post_init__(self) -> None:
        self.all_processed_lines: List["TerminalTechniqueArchivesMaintLogLine"] = []
        self.all_processed_files: List["TerminalTechniqueArchivesMaintFile"] = []
        self.currently_opened_alarms: List[TerminalTechniqueClosableAlarm] = []
        self.ignored_end_alarm_lines_without_alarm_begin: List[TerminalTechniqueArchivesMaintLogLine] = []

    def load_folder(self, folder_full_path: str) -> Self:

        for dirpath, dirnames, filenames in os.walk(folder_full_path):
            for file_name in filenames:
                file = TerminalTechniqueArchivesMaintFile(parent_folder_full_path=dirpath, file_name=file_name, library=self)
                self.all_processed_files.append(file)
                self.all_processed_lines += file.all_processed_lines

                assert self.all_processed_lines
        assert self.all_processed_lines

        logger_config.print_and_log_info(f"{self.name}: currently_opened_alarms:{len(self.currently_opened_alarms)}")
        assert len(self.ignored_end_alarm_lines_without_alarm_begin) < 10

        return self


@dataclass
class TerminalTechniqueArchivesMaintFile:
    parent_folder_full_path: str
    file_name: str
    library: "TerminalTechniqueArchivesMaintLibrary"
    all_processed_lines: List["TerminalTechniqueArchivesMaintLogLine"] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.file_full_path = self.parent_folder_full_path + "\\" + self.file_name

        with logger_config.stopwatch_with_label(f"Open and read file  {self.file_full_path}", inform_beginning=False, enable_print=False, enabled=False):
            with open(self.file_full_path, mode="r", encoding="ANSI") as file:
                all_raw_lines = file.readlines()
                # logger_config.print_and_log_info(to_print_and_log=f"File {self.file_full_path} has {len(all_raw_lines)} lines")
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

        self.full_raw_line_split_by_tab = self.full_raw_line.split("\t")
        self.alarm_type = AlarmLineType[self.full_raw_line_split_by_tab[2]]

        # 2025-12-29	01:45:53.30
        self.raw_date_str_with_microseconds = self.raw_date_str + "0000"
        self.decoded_timestamp = datetime.datetime.strptime(self.raw_date_str_with_microseconds, "%Y-%m-%d	%H:%M:%S.%f")

        assert len(self.full_raw_line_split_by_tab) == 4
        self.alarm_full_text = self.full_raw_line_split_by_tab[3]

        self.alarm: Optional[TerminalTechniqueAlarm] = None

        if self.alarm_type == AlarmLineType.FIN_ALA:
            found_unclosed_alarms = [alarm for alarm in self.parent_file.library.currently_opened_alarms if alarm.full_text == self.alarm_full_text]
            if found_unclosed_alarms:
                assert len(found_unclosed_alarms) == 1
                found_unclosed_alarm = found_unclosed_alarms[0]
                assert found_unclosed_alarm.end_alarm_line is None
                self.alarm = found_unclosed_alarm
                self.alarm.end_alarm_line = self
            else:
                self.parent_file.library.ignored_end_alarm_lines_without_alarm_begin.append(self)

        elif "Absence acquittement SAAT" in self.alarm_full_text:
            self.alarm = SaatMissingAcknowledgmentTerminalTechniqueAlarm(raise_line=self, full_text=self.alarm_full_text, alarm_type=self.alarm_type)
        elif self.alarm_type == AlarmLineType.DEB_ALA:
            self.alarm = TerminalTechniqueClosableAlarm(raise_line=self, full_text=self.alarm_full_text, alarm_type=self.alarm_type)
        elif self.alarm_type == AlarmLineType.EVT_ALA:
            self.alarm = TerminalTechniqueAlarm(raise_line=self, full_text=self.alarm_full_text, alarm_type=self.alarm_type)
        elif self.alarm_type == AlarmLineType.CSI:
            self.alarm = TerminalTechniqueCsiAlarm(raise_line=self, full_text=self.alarm_full_text, alarm_type=self.alarm_type)
        else:
            assert False, f"Alarm type {self.alarm_type} for {self.parent_file.file_name} {self.line_number} {self.alarm_full_text}"
