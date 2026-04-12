from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field
from enum import Enum

from stsloganalyzis import line_topology, decode_archive

from logger import logger_config


@dataclass
class Train:
    cc_id_with_offset: int


@dataclass
class SqlArchArchiveLineWithContext:
    sql_arch_line: decode_archive.SqlArchArchiveLine

    def __post_init__(self) -> None:
        pass


@dataclass
class ArchiveAnalyzis:
    topology_line: line_topology.Line
    archive_library: decode_archive.ArchiveLibrary

    def __post_init__(self) -> None:
        self.trains: List[Train] = []
        self.parsed_sql_arch_lines: List[Train] = []
        self.previous_line_by_id: Dict[str, decode_archive.SqlArchArchiveLine] = dict()

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    def create_reports_all_sqlarch_changes_since_previous(
        self, white_list_signal_types: Optional[List[decode_archive.SqlArchLineSignalType]], output_directory_path: str, also_print_and_log: bool, file_base_name: Optional[str] = None
    ) -> int:
        if file_base_name is None:
            file_base_name = f"{self.label}_all_changes"

        rows_as_list_dict: List[Dict[str, Any]] = []

        for line in self.all_sqlarch_lines:
            all_changes_since_previous = line.get_all_changes_since_previous(
                white_list_signal_types=white_list_signal_types, also_print_and_log=also_print_and_log, previous_line_for_this_id=previous_line_for_this_id
            )
            if all_changes_since_previous:
                rows_as_list_dict.append(all_changes_since_previous)

        # logger_config.print_and_log_info(f"{len(rows_as_list_dict)} lines changed detected, report created")
        reports_utils.save_rows_to_output_files(rows_as_list_dict=rows_as_list_dict, file_base_name=file_base_name, output_directory_path=output_directory_path, suffix_file_name_by_date=False)
        reports_utils.save_rows_to_output_files(rows_as_list_dict=rows_as_list_dict, file_base_name=file_base_name, output_directory_path=output_directory_path, suffix_file_name_by_date=True)
        return len(rows_as_list_dict)
