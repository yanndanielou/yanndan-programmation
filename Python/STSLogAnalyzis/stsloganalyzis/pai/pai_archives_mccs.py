import os
import time
import re
from collections import Counter, OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Self, cast

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
from common import file_name_utils, file_utils, date_time_formats, reports_utils
from logger import logger_config
from stsloganalyzis.common import common_filters

# ex:024 24/02/26 05:14:20:29 - 6609225
MCCS_ARCHIVE_TIMESTAMP_LINE_REGEX_COMPILED = re.compile(r"(\d+) (\d+)/(\d+)/(\d+) (\d+):(\d+):(\d+):(\d+) - (\d+)")
MCCS_ARCHIVE_TIMESTAMP_LINE_REGEX_COMPILED = re.compile(
    r"(?P<unknown_prefix>\d+) (?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+) (?P<hour>\d+):(?P<minute>\d+):(?P<seconds>\d+):(?P<milliseconds>\d+) - (?P<unknown_end>\d+)"
)


@dataclass
class PaiMccsArchivesLibrary:
    directory_path: str
    label: str
    filename_pattern: str = "MCCS*.txt"
    lines_creation_filters: list[common_filters.StringFieldValueBasedFilter] | None = None

    def __post_init__(self) -> None:

        self.last_timestamp_found: PaiMccsArchivesLogTimestamp | None = None
        self.decoded_files: list[PaiMccsArchivesLogFile] = []
        self.decoded_lines: list[PaiMccsArchivesLogLine] = []
        self.all_logs_paths: list[str] = []
        self.returns_to_past_less_than_1_second: list[tuple[datetime, datetime]] = []

        self.all_logs_paths = file_utils.get_files_by_directory_and_file_name_mask(
            directory_path=self.directory_path,
            file_sort_order=file_utils.FileSortOrder.TIMESTAMP_OLDER_TO_NEWER,
            filename_pattern=self.filename_pattern,
        )
        if not self.all_logs_paths:
            all_sub_directories = [f for f in os.listdir(self.directory_path) if os.path.isdir(os.path.join(self.directory_path, f))]
            logger_config.print_and_log_info(f"No file found in {self.directory_path}: look in sub directories ({len(all_sub_directories)} found)")
            for sub_directory in all_sub_directories:
                self.all_logs_paths += file_utils.get_files_by_directory_and_file_name_mask(
                    directory_path=self.directory_path + "\\" + sub_directory,
                    file_sort_order=file_utils.FileSortOrder.TIMESTAMP_OLDER_TO_NEWER,
                    filename_pattern=self.filename_pattern,
                )

        logger_config.print_and_log_info(f"{len(self.all_logs_paths)} files found in {self.directory_path}")

        at_beginning_log_timestamp = time.perf_counter()
        last_chunk_timestamp = None
        for log_path in self.all_logs_paths:

            decoded_file = PaiMccsArchivesLogFile(
                file_full_path=log_path,
                library=self,
            )
            self.decoded_files.append(decoded_file)
            if len(self.decoded_files) % 25 == 0:
                current_time = time.perf_counter()
                current_chunk_duration = current_time - last_chunk_timestamp if last_chunk_timestamp else None
                since_beginning_duration = current_time - at_beginning_log_timestamp
                progress_ratio = len(self.decoded_files) / len(self.all_logs_paths)
                logger_config.print_and_log_info(
                    f"{len(self.decoded_files)}/{len(self.all_logs_paths)} ({round(progress_ratio*100,2)}%) files decoded so far ({len(self.decoded_lines)} lines in total). Elapsed: {date_time_formats.format_duration_to_string(since_beginning_duration)} since beginning, {date_time_formats.format_duration_to_string(current_chunk_duration) if last_chunk_timestamp else "NA"} since previous chunk. Total duration estimation {date_time_formats.format_duration_to_string(since_beginning_duration/progress_ratio)}",
                    print_ram_usage=True,
                )
                last_chunk_timestamp = time.perf_counter()

        self.print_stats()

    def print_stats(self) -> None:
        logger_config.print_and_log_info(f"{len(self.returns_to_past_less_than_1_second)} returns_to_past_less_than_1_second")

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    def create_output_with_frequencies_of_terms(
        self,
        lines_to_use: list["PaiMccsArchivesLogLine"],
        frequency_between_measures: timedelta,
        label: str | None = None,
    ) -> None:
        file_base_name = f"{self.label}_{label}_frequencies"

        rows_as_list_dict: list[dict[str, Any]] = []

        current_measure_begin_timestamp = lines_to_use[0].timestamp.timestamp
        end_data_timestamp = lines_to_use[-1].timestamp.timestamp

        current_measure_end_timestamp = current_measure_begin_timestamp

        while current_measure_end_timestamp < end_data_timestamp:
            current_measure_end_timestamp += frequency_between_measures

            all_lines_in_measure_interval = [
                log_line for log_line in lines_to_use if log_line.timestamp.timestamp >= current_measure_begin_timestamp and log_line.timestamp.timestamp < current_measure_end_timestamp
            ]

            current_row = OrderedDict(
                {
                    "Interval begin": current_measure_begin_timestamp.replace(tzinfo=None),
                    "Interval begin (string)": current_measure_begin_timestamp.isoformat(),
                    "Interval end": current_measure_end_timestamp.replace(tzinfo=None),
                    "Number of lines": len(all_lines_in_measure_interval),
                }
            )

            rows_as_list_dict.append(current_row)

            current_measure_begin_timestamp = current_measure_end_timestamp

        # logger_config.print_and_log_info(f"{len(rows_as_list_dict)} lines changed detected, report created")
        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=rows_as_list_dict,
            file_base_name=file_base_name,
            suffix_file_name_by_date=reports_utils.SuffixFileNameByDate.NO,
            split_big_files=False,
            create_txt_file=False,
            create_csv_file=False,
            create_json_file=False,
        )


@dataclass
class PaiMccsArchivesLogTimestamp:
    library: PaiMccsArchivesLibrary
    file_path: str
    line_number_in_file: int
    timestamp: datetime
    previous_timestamp: "PaiMccsArchivesLogTimestamp | None"

    def __post_init__(self) -> None:

        if self.previous_timestamp:
            if self.previous_timestamp.timestamp > self.timestamp:
                error_duration = self.previous_timestamp.timestamp - self.timestamp

                logger_config.print_and_log_error_if(
                    error_duration.seconds >= 1,
                    to_print_and_log=f"Return to past ({error_duration.seconds} seconds) at {self.file_path}:{self.line_number_in_file} from {self.previous_timestamp.timestamp } to {self.timestamp} defined in {self.previous_timestamp.file_path}",
                )
                if error_duration.seconds < 1:
                    self.library.returns_to_past_less_than_1_second.append((self.previous_timestamp.timestamp, self.timestamp))


@dataclass
class PaiMccsArchivesLogFile:
    file_full_path: str
    library: PaiMccsArchivesLibrary

    @staticmethod
    def get_timestamp_if_timestamp_line(raw_line: str) -> datetime | None:

        if "/" not in raw_line:
            return None

        match = MCCS_ARCHIVE_TIMESTAMP_LINE_REGEX_COMPILED.match(raw_line)
        if match is None:
            return None

        unknown_prefix = match.group("unknown_prefix")
        day = int(match.group("day"))
        month = int(match.group("month"))
        year = int(match.group("year"))
        hour = int(match.group("hour"))
        minute = int(match.group("minute"))
        seconds = int(match.group("seconds"))
        milliseconds = int(match.group("milliseconds"))
        unknown_end = int(match.group("unknown_end"))

        timestamp = datetime.strptime(f"{year+2000}-{month}-{day} {hour}:{minute}:{seconds}:{milliseconds}", "%Y-%m-%d %H:%M:%S:%f").replace(tzinfo=None)

        return timestamp

    def __post_init__(self) -> None:
        self.decoded_lines: list[PaiMccsArchivesLogLine] = []
        self.file_name = file_name_utils.get_file_name_without_extension_from_full_path(self.file_full_path)

        with logger_config.stopwatch_with_label(f"Handle file {self.file_full_path}", monitor_ram_usage=True, inform_beginning=False, enable_print=False):
            lines = file_utils.open_text_file_and_get_read_lines(self.file_full_path)
            for line_number, raw_line in enumerate(lines):
                timestamp_found = self.get_timestamp_if_timestamp_line(raw_line)
                if timestamp_found is not None:
                    self.library.last_timestamp_found = PaiMccsArchivesLogTimestamp(
                        library=self.library,
                        file_path=self.file_full_path,
                        line_number_in_file=line_number + 1,
                        timestamp=timestamp_found,
                        previous_timestamp=self.library.last_timestamp_found,
                    )
                else:
                    if self.library.last_timestamp_found is None:
                        logger_config.print_and_log_warning(f"Ignored line because no previous timestamp found: Line number {line_number+1} in {self.file_full_path}. Content: {raw_line}")
                    else:

                        if common_filters.must_be_kept_after_string_filters(raw_line, self.library.lines_creation_filters):
                            log_line = PaiMccsArchivesLogLine(
                                timestamp=self.library.last_timestamp_found,
                                raw_log_line=raw_line,
                                file=self,
                                line_number=line_number + 1,
                            )
                            self.decoded_lines.append(log_line)
                            self.library.decoded_lines.append(log_line)


@dataclass
class PaiMccsArchivesLogLine:
    timestamp: PaiMccsArchivesLogTimestamp
    raw_log_line: str
    file: PaiMccsArchivesLogFile
    line_number: int

    def __post_init__(self) -> None:
        pass
