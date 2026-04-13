from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Optional, Dict, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

from stsloganalyzis import line_topology, decode_archive

from common import reports_utils

from logger import logger_config


@dataclass
class Train:
    cc_id_with_offset: int


@dataclass
class SqlArchArchiveLineWithContext:
    sql_arch_line: decode_archive.SqlArchArchiveLine
    previous_line_for_this_id: Optional[SqlArchArchiveLineWithContext]

    def __post_init__(self) -> None:
        pass


@dataclass
class ArchiveAnalyzis:
    railway_line: line_topology.Line
    archive_library: decode_archive.ArchiveLibrary

    label: str

    def __post_init__(self) -> None:
        self.trains: List[Train] = []

        self.all_sql_arch_lines_with_context: List[SqlArchArchiveLineWithContext] = []
        self.current_latest_line_by_id: Dict[str, SqlArchArchiveLineWithContext] = dict()

        self.handle_lines()

    def handle_lines(self) -> None:
        for sql_arch_line in self.archive_library.all_sqlarch_lines:
            previous_line_for_this_id = self.current_latest_line_by_id.get(sql_arch_line.id_field)
            line_with_context = SqlArchArchiveLineWithContext(sql_arch_line=sql_arch_line, previous_line_for_this_id=previous_line_for_this_id)
            self.all_sql_arch_lines_with_context.append(line_with_context)
            self.current_latest_line_by_id[sql_arch_line.id_field] = line_with_context

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    def create_reports_all_sqlarch_changes_since_previous(self, output_directory_path: str, also_print_and_log: bool, file_base_name: Optional[str] = None) -> int:
        if file_base_name is None:
            file_base_name = f"{self.label}_all_changes"

        rows_as_list_dict: List[Dict[str, Any]] = []

        for line_with_context in self.all_sql_arch_lines_with_context:
            all_changes_since_previous = line_with_context.sql_arch_line.get_all_changes_since_previous(
                also_print_and_log=also_print_and_log, previous_line_for_this_id=line_with_context.previous_line_for_this_id.sql_arch_line if line_with_context.previous_line_for_this_id else None
            )
            if all_changes_since_previous:
                rows_as_list_dict.append(all_changes_since_previous)

        # logger_config.print_and_log_info(f"{len(rows_as_list_dict)} lines changed detected, report created")
        reports_utils.save_rows_to_output_files(rows_as_list_dict=rows_as_list_dict, file_base_name=file_base_name, output_directory_path=output_directory_path, suffix_file_name_by_date=False)
        reports_utils.save_rows_to_output_files(rows_as_list_dict=rows_as_list_dict, file_base_name=file_base_name, output_directory_path=output_directory_path, suffix_file_name_by_date=True)
        return len(rows_as_list_dict)
