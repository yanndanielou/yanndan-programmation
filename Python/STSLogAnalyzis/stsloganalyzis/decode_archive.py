import json
import re
from abc import ABC, abstractmethod
from collections import OrderedDict
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Self, Set, cast

from datetime import datetime
import humanize
from common import date_time_formats, file_name_utils, file_utils
from dateutil import parser
from logger import logger_config

from stsloganalyzis import (
    decode_action_set_content,
    decode_message,
    line_topology,
    decode_xml_message,
    constants,
    helpers,
)

ArchiveLineFilter = Callable[[str, "ArchiveSource"], bool]


class WhiteOrBlackListFilterType(Enum):
    WHITELIST = "WHITELIST"
    BLACKLIST = "BLACKLIST"


class ArchiveLineTag(Enum):
    VERSIONS = "VERSIONS"
    SQLARCH = "SQLARCH"
    SPMQ = "SPMQ"
    ALARM = "ALARM"


class SqlArchLineSignalType:

    def __init__(self, identifier: str, label: Optional[str] = None) -> None:
        self.identifier = identifier
        self.label = label if label else identifier

    class Library:
        def __init__(self) -> None:
            self.all_types: List[SqlArchLineSignalType] = []
            for type_str in [
                "TRAIN",
                "TCA",
                "TSA",
                "TG",
                "SY",
                "TS",
                "TSI",
                "MSG",
                "TE",
                "TC",
                "TCCR",
                "DEF_IMG",
                "CR",
                "TB",
                "AIGUILLE",
                "CDV",
                "SQCR",
                "ARS_AD",
                "PARC",
                "TCSCR",
                "CICR",
                "LOGIN",
                "TR",
                "TRCR",
                "TCS",
                "CI",
                "HMI_NAVIGATION",
            ]:
                self.all_types.append(SqlArchLineSignalType(type_str))

        def get_by_identifier(self, identifier: str) -> "SqlArchLineSignalType":
            types_found = [type_it for type_it in self.all_types if type_it.identifier == identifier]
            if not types_found:
                new_type = SqlArchLineSignalType(identifier)
                logger_config.print_and_log_error(new_type.identifier)
                self.all_types.append(new_type)
                return self.get_by_identifier(identifier)
            return types_found[0]


sql_arch_line_signal_type_library = SqlArchLineSignalType.Library()


class SqlArchFilter(ABC):
    def __init__(self) -> None:
        self.rejected_count: int = 0
        self.rejected_count_by_item: Dict[str, int] = dict()

    def get_sqlarch_section(self, raw_sql_arch_line: str) -> Any:
        line_json = json.loads(raw_sql_arch_line)
        sqlarch_section = line_json.get("SQLARCH", {})
        return sqlarch_section

    @abstractmethod
    def do_passes(self, raw_sql_arch_line: str, parent: "ArchiveSource") -> bool:
        pass

    def passes(self, raw_sql_arch_line: str, parent: "ArchiveSource") -> bool:
        ret = self.do_passes(raw_sql_arch_line=raw_sql_arch_line, parent=parent)
        if not ret:
            self.rejected_count += 1
        return ret

    def print_stats(self) -> None:
        logger_config.print_and_log_info(f"  Filter {self}: ' - rejected {self.rejected_count} lines")

    @abstractmethod
    def __str__(self) -> str:
        pass


class SqlArchLineStringFieldValueBasedFilter(SqlArchFilter):
    class ArchiveLineStringFilterType(Enum):
        EQUALS_TO = "EQUALS_TO"
        BEGIN_WITH_STRING = "BEGIN_WITH_STRING"
        MATCHES_REGEX = "MATCHES_REGEX"
        CONTAINS = "CONTAINS"

    def __init__(self, white_or_black_list: WhiteOrBlackListFilterType, field_name: str, field_values: List[str], filter_type: ArchiveLineStringFilterType) -> None:
        super().__init__()
        self.white_or_black_list = white_or_black_list
        self.is_whitelist = white_or_black_list == WhiteOrBlackListFilterType.WHITELIST
        self.field_name = field_name
        self.filter_type = filter_type
        self.filter_field_values = field_values

    def do_passes(self, raw_sql_arch_line: str, parent: "ArchiveSource") -> bool:
        try:
            sqlarch_section = self.get_sqlarch_section(raw_sql_arch_line)
            field_raw_value = str(sqlarch_section.get(self.field_name, ""))

            ret: bool
            match = False
            if self.filter_type == SqlArchLineStringFieldValueBasedFilter.ArchiveLineStringFilterType.EQUALS_TO:
                match = field_raw_value in self.filter_field_values
            elif self.filter_type == SqlArchLineStringFieldValueBasedFilter.ArchiveLineStringFilterType.CONTAINS:
                match = any(filter_field_value in field_raw_value for filter_field_value in self.filter_field_values)
            elif self.filter_type == SqlArchLineStringFieldValueBasedFilter.ArchiveLineStringFilterType.BEGIN_WITH_STRING:
                match = any(field_raw_value.startswith(filter_field_value) for filter_field_value in self.filter_field_values)
            elif self.filter_type == SqlArchLineStringFieldValueBasedFilter.ArchiveLineStringFilterType.MATCHES_REGEX:
                match = any(bool(re.search(filter_field_value, field_raw_value)) for filter_field_value in self.filter_field_values)
            else:
                assert False, f"Not handled {self.filter_type}"

            ret = match if self.is_whitelist else not match
            if not ret:
                if field_raw_value not in self.rejected_count_by_item:
                    self.rejected_count_by_item[field_raw_value] = 0

                self.rejected_count_by_item[field_raw_value] += 1

            return ret
        except (TypeError, ValueError, json.JSONDecodeError, KeyError):
            return False

    def print_stats(self) -> None:
        logger_config.print_and_log_info(f"  Filter {self}: ' - rejected {self.rejected_count} lines. Details {self.rejected_count_by_item}")

    def __str__(self) -> str:
        return f"{self.filter_type.value} {self.field_name} {','.join(self.filter_field_values)} {'Whitelist' if self.is_whitelist else 'Blacklist'} "


class IdFilter(SqlArchLineStringFieldValueBasedFilter):
    def __init__(self, field_values: List[str], filter_type: SqlArchLineStringFieldValueBasedFilter.ArchiveLineStringFilterType, white_or_black_list: WhiteOrBlackListFilterType) -> None:
        super().__init__(white_or_black_list=white_or_black_list, field_name="id", field_values=field_values, filter_type=filter_type)


class SignalTypeFilter(SqlArchLineStringFieldValueBasedFilter):
    def __init__(self, white_or_black_list: WhiteOrBlackListFilterType, field_values: List[str], filter_type: SqlArchLineStringFieldValueBasedFilter.ArchiveLineStringFilterType) -> None:
        super().__init__(white_or_black_list=white_or_black_list, field_values=field_values, field_name="sigT", filter_type=filter_type)


class DatesFilter(SqlArchFilter):
    class DateFilter(SqlArchFilter):

        def get_line_date(self, raw_sql_arch_line: str) -> datetime:
            line_json = json.loads(raw_sql_arch_line)
            raw_date = line_json.get("date")
            parsed_date = parser.parse(raw_date)
            offset_naive_date = parsed_date.replace(tzinfo=None)
            return offset_naive_date

    class DateBetweenFilter(DateFilter):

        def __init__(self, date_min: datetime, date_max: datetime) -> None:
            super().__init__()
            self.date_min = date_min
            self.date_max = date_max

        def do_passes(self, raw_sql_arch_line: str, parent: "ArchiveSource") -> bool:
            line_date = self.get_line_date(raw_sql_arch_line)
            return line_date > self.date_min and line_date < self.date_max

        def __str__(self) -> str:
            return f"{self.__class__.__name__} {self.date_min} {self.date_max} "


ARCHIVE_VERSION_LINE_PREFIX = '{"' + ArchiveLineTag.VERSIONS.value + '":{'
ARCHIVE_SQLARCH_LINE_PREFIX = '{"' + ArchiveLineTag.SQLARCH.value + '":{'
ARCHIVE_SPMQ_LINE_PREFIX = '{"' + ArchiveLineTag.SPMQ.value + '":{'
ARCHIVE_ALARM_LINE_PREFIX = '{"' + ArchiveLineTag.ALARM.value + '":{'


class ArchiveDecoder:
    def __init__(
        self,
        message_manager: decode_message.InvariantMessagesManager,
        xml_message_decoder: decode_xml_message.XmlMessageDecoder,
        action_set_content_decoder: decode_action_set_content.ActionSetContentDecoder,
        railway_line: line_topology.Line,
    ) -> None:
        self.message_manager = message_manager
        self.action_set_content_decoder = action_set_content_decoder
        self.xml_message_decoder = (xml_message_decoder,)
        self.message_decoder = decode_message.MessageDecoder(xml_message_decoder=xml_message_decoder, action_set_content_decoder=self.action_set_content_decoder, railway_line=railway_line)


class ArchiveLibrary:
    class Builder:
        def __init__(self) -> None:
            self._library = ArchiveLibrary()

            self.archive_inputs: List[ArchiveSource] = []
            self.archive_decoder: Optional[ArchiveDecoder] = None
            self.sqlarch_archive_lines_filters: List[SqlArchFilter] = []

            self._label_is_forced = False

        def with_label(self, label: str) -> Self:
            self._library.label = label
            self._label_is_forced = True
            return self

        def add_raw_archives_json_lines(self, raw_archives_json_lines: List[str]) -> Self:
            self.archive_inputs.append(ArchiveLinesSet(raw_archives_json_lines=raw_archives_json_lines))
            return self

        def add_archive_files(self, directory_path: str, filename_pattern: str) -> Self:
            for file_full_path in file_utils.get_files_by_directory_and_file_name_mask(directory_path, filename_pattern, file_sort_order=file_utils.FileSortOrder.TIMESTAMP_OLDER_TO_NEWER):
                self.add_archive_file(file_full_path=file_full_path)
            if not self._label_is_forced:
                self._library.label = f"Folder{file_name_utils.get_directory_name_from_directory_full_path(directory_path)}"

            return self

        def add_archive_file(self, file_full_path: str) -> Self:
            self.archive_inputs.append(ArchiveFile(file_full_path=file_full_path))
            if not self._label_is_forced:
                self._library.label += f"{file_name_utils.get_file_name_without_extension_from_full_path(file_full_path)} "

            return self

        def add_sqlarch_archive_lines_filter(self, sql_arch_filter: SqlArchFilter) -> Self:
            self.sqlarch_archive_lines_filters.append(sql_arch_filter)
            return self

        def add_archive_decoder(self, archive_decoder: ArchiveDecoder) -> Self:
            assert self.archive_decoder is None
            self.archive_decoder = archive_decoder
            return self

        def build(self) -> "ArchiveLibrary":
            self._library.sqlarch_archive_lines_filters = self.sqlarch_archive_lines_filters

            for archive_input in self.archive_inputs:
                self._library.handle_input(archive_input)
                self._library.decode_all_lines(archive_input, archive_decoder=self.archive_decoder)

            # if self.archive_decoder:
            #    self._library.decode_all_lines(archive_decoder=self.archive_decoder)

            self._library.print_filter_stats_and_info()
            return self._library

    def __init__(self) -> None:
        self.label = ""

        self.archive_inputs: List["ArchiveSource"] = []
        self.all_archive_lines: List[ArchiveLine] = []
        self.all_archive_lines_by_type: Dict[ArchiveLineTag, List[ArchiveLine]] = dict()
        self._last_sqlarch_line_by_id: Dict[str, SqlArchArchiveLine] = dict()
        self.all_sqlarch_lines: List[SqlArchArchiveLine] = []
        self.all_version_lines: List[VersionArchiveLine] = []
        self.all_spmq_lines: List[ArchiveLine] = []
        self.all_alarm_lines: List[ArchiveLine] = []
        self.sqlarch_archive_lines_filters: List[SqlArchFilter] = []
        self.total_sqlarch_lines_processed: int = 0

    def handle_input(self, archive_input: "ArchiveSource") -> int:
        self.archive_inputs.append(archive_input)

        line_number = 0
        for line_number, line in enumerate(archive_input.get_all_archive_file_lines()):
            self._process_archive_raw_line(line_number=line_number, line=line, parent=archive_input)

        return line_number

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    def decode_all_lines(self, archive_input: "ArchiveSource", archive_decoder: ArchiveDecoder) -> int:
        number_of_lines_decoded = 0
        with logger_config.stopwatch_with_label(f"{self.label}: Decode all {len(archive_input.all_sqlarch_lines)} lines", monitor_ram_usage=True, inform_beginning=True):

            for sqlarch_line in archive_input.all_sqlarch_lines:
                sqlarch_line.decode_message(archive_decoder)

        return number_of_lines_decoded

    def _passes_sqlarch_archive_line_filters(self, raw_sql_arch_line: str, parent: "ArchiveSource") -> bool:
        self.total_sqlarch_lines_processed += 1

        # Check ID filters
        for f in self.sqlarch_archive_lines_filters:
            if not f.do_passes(raw_sql_arch_line, parent):
                return False

        return True

    def _process_archive_raw_line(self, line_number: int, line: str, parent: "ArchiveSource") -> None:

        archive_line: ArchiveLine

        if line.startswith(ARCHIVE_VERSION_LINE_PREFIX):
            archive_line = VersionArchiveLine(full_raw_archive_line=line, parent=parent)
            self.all_version_lines.append(archive_line)
        elif line.startswith(ARCHIVE_SQLARCH_LINE_PREFIX):

            if not self._passes_sqlarch_archive_line_filters(raw_sql_arch_line=line, parent=parent):
                return

            archive_line = SqlArchArchiveLine(full_raw_archive_line=line, parent=parent)
            self._last_sqlarch_line_by_id[archive_line.id_field] = archive_line

            parent.all_sqlarch_lines.append(archive_line)
            self.all_sqlarch_lines.append(archive_line)
        elif line.startswith(ARCHIVE_SPMQ_LINE_PREFIX):
            archive_line = ArchiveLine(full_raw_archive_line=line, parent=parent)
            self.all_spmq_lines.append(archive_line)
        elif line.startswith(ARCHIVE_ALARM_LINE_PREFIX):
            archive_line = ArchiveLine(full_raw_archive_line=line, parent=parent)
            self.all_alarm_lines.append(archive_line)
        else:
            logger_config.print_and_log_error(f"{self.label}: Unsupported line {line_number}:" + line)

        self.all_archive_lines.append(archive_line)
        archive_line_type = archive_line.tag

        if archive_line_type not in self.all_archive_lines_by_type:
            self.all_archive_lines_by_type[ArchiveLineTag[archive_line_type]] = []

        self.all_archive_lines_by_type[ArchiveLineTag[archive_line_type]].append(archive_line)

    def get_all_signal_types(self) -> Set[str]:
        return {line.signal_type_raw for line in self.all_sqlarch_lines}

    def print_filter_stats_and_info(self) -> None:
        logger_config.print_and_log_info(f"{self.label}: === ArchiveLibrary Filter Statistics and Info ===")
        logger_config.print_and_log_info(f"{self.label}: Total SQLARCH lines processed: {self.total_sqlarch_lines_processed}")
        logger_config.print_and_log_info(f"{self.label}: Lines kept after filtering: {len(self.all_sqlarch_lines)}")

        logger_config.print_and_log_info(f"{self.label}: ID Filters:")
        for f in self.sqlarch_archive_lines_filters:
            f.print_stats()

        logger_config.print_and_log_info(f"{self.label}: === End Filter Statistics ===")


class ArchiveLine:
    def __init__(self, full_raw_archive_line: str, parent: "ArchiveSource") -> None:
        self.parent = parent
        self.full_raw_archive_line = full_raw_archive_line
        # Parsing JSON string
        self.full_archive_line_as_json: Dict = json.loads(full_raw_archive_line)

        # Access global fields
        self.date_raw = self.full_archive_line_as_json["date"]
        self.date = parser.parse(self.date_raw)
        self.tags: List[str] = self.full_archive_line_as_json["tags"]
        self.tag: str = self.tags[0]

        self.all_fields_dict: Dict[str, constants.HUMAN_READABLE_FIELD_TYPE] = self.full_archive_line_as_json.get(self.tag, {})
        self.all_fields_dict["date_raw"] = self.date_raw

    def get_date_raw_str(self) -> str:
        return cast(str, self.date_raw)


class VersionArchiveLine(ArchiveLine):
    def __init__(self, full_raw_archive_line: str, parent: "ArchiveSource") -> None:
        super().__init__(full_raw_archive_line=full_raw_archive_line, parent=parent)


class SqlArchArchiveLine(ArchiveLine):
    def __init__(self, full_raw_archive_line: str, parent: "ArchiveSource") -> None:
        super().__init__(full_raw_archive_line=full_raw_archive_line, parent=parent)

        # Accessing specific fields
        self.sqlarch_json_section: Dict[str, str | int] = self.full_archive_line_as_json["SQLARCH"]

        # Accessing specific fields
        self.caller = self.sqlarch_json_section.get("caller")
        self.cat_ala = self.sqlarch_json_section.get("catAla")
        self.eqp = str(self.sqlarch_json_section.get("eqp"))
        assert isinstance(self.eqp, str)
        self.eqp_id = self.sqlarch_json_section.get("eqpId")
        self.exe_st = self.sqlarch_json_section.get("exeSt")
        self.id_field = str(self.sqlarch_json_section.get("id"))
        self.signal_type_raw = str(self.sqlarch_json_section.get("sigT"))

        self.signal_type = sql_arch_line_signal_type_library.get_by_identifier(self.signal_type_raw) if self.signal_type_raw else None

        assert self.id_field is not None
        assert isinstance(self.id_field, str)

        self.jdb = self.sqlarch_json_section.get("jdb")
        self.label = self.sqlarch_json_section.get("label")
        self.loc = self.sqlarch_json_section.get("loc")

        self.sqlarch_fields_dict_raw: dict[str, constants.HUMAN_READABLE_FIELD_TYPE] = dict()
        self.invariant_message: Optional[decode_message.InvariantMessage] = None
        self.decoded_message: Optional[decode_message.DecodedMessage] = None

    def decode_message(self, archive_decoder: ArchiveDecoder) -> None:
        # Directly copy all items from SQLARCH section into a new dictionary
        self.sqlarch_fields_dict_raw = {f"{key}_raw": value for key, value in self.all_fields_dict.items()}
        self.invariant_message = archive_decoder.message_manager.get_message_by_id(self.get_id())
        if self.invariant_message:
            self.decoded_message = archive_decoder.message_decoder.decode_raw_hexadecimal_message(message_number=self.invariant_message.message_number, hexadecimal_content=self.get_new_state_str())

    def get_id(self) -> str:
        return cast(str, self.all_fields_dict.get("id"))

    def get_new_state_str(self) -> str:
        return cast(str, self.all_fields_dict.get("newSt"))

    def print_all(self) -> None:
        # Print extracted fields
        print("Caller:", self.caller)
        print("CatAla:", self.cat_ala)
        print("Eqp:", self.eqp)
        print("EqpId:", self.eqp_id)
        print("ExeSt:", self.exe_st)
        print("ID:", self.id_field)
        print("Jdb:", self.jdb)
        print("Label:", self.label)
        print("Loc:", self.loc)

        # Print the dictionary for SQLARCH fields
        for key, value in self.all_fields_dict.items():
            print(f"{key}: {value}")

        print("Date:", self.date_raw)
        print("Tags:", self.tags)

    def _get_print_prefix(self) -> str:
        return f"{self.date_raw}\t{self.id_field}\t"

    def get_all_changes_since_previous(self, previous_line_for_this_id: Optional["SqlArchArchiveLine"]) -> List[OrderedDict[str, Any]]:
        to_ret: List[OrderedDict[str, Any]] = []

        previous_date = previous_line_for_this_id.date if previous_line_for_this_id else None
        exact_time_delta = date_time_formats.format_duration_timedelta_to_string(self.date - previous_line_for_this_id.date) if previous_line_for_this_id else "NA"
        approximative_time_delta = humanize.precisedelta(self.date - previous_date, minimum_unit="milliseconds") if previous_date else "NA"
        old_timestamp = previous_line_for_this_id.date_raw if previous_line_for_this_id else None

        if self.decoded_message is None:
            # If no decoded message, only show newSt change
            previous_new_st = previous_line_for_this_id.get_new_state_str() if previous_line_for_this_id else "No previous"
            new_new_st = self.get_new_state_str()
            if previous_new_st != new_new_st:

                to_ret.append(
                    OrderedDict(
                        {
                            "date": self.get_date_raw_str(),
                            "id": self.id_field,
                            "field": constants.STATE_FIELD_NAME,
                            "old_value": previous_new_st,
                            "new_value": new_new_st,
                            "change_value": f"{previous_new_st} -> {new_new_st}",
                            "exact_time_delta": exact_time_delta,
                            "approximative_time_delta": approximative_time_delta,
                            "old_timestamp": old_timestamp,
                        }
                    )
                )

        else:

            # If decoded message exists, show only decoded message fields that changed
            for field_name in self.decoded_message.decoded_fields_flat_directory.keys():

                # if field_name not in constants.FIELD_FULL_NAMES_TO_EXCLUDE_IN_REPORTS and not any(field_name.startswith(prefix) for prefix in constants.FIELD_NAMES_PREFIXES_TO_EXCLUDE_IN_REPORTS):
                if not helpers.is_field_name_to_be_ignored(field_name=field_name):

                    new_value = self.decoded_message.get_field_value_human_readable(field_name)
                    previous_value = (
                        previous_line_for_this_id.decoded_message.get_field_value_human_readable(field_name)
                        if previous_line_for_this_id and previous_line_for_this_id.decoded_message
                        else "No previous"
                    )

                    if new_value != previous_value:
                        to_ret.append(
                            OrderedDict(
                                {
                                    "date": self.get_date_raw_str(),
                                    "id": self.id_field,
                                    "id_msg": self.decoded_message.message_number,
                                    "field": field_name,
                                    "old_value": previous_value,
                                    "new_value": new_value,
                                    "change_value": f"{previous_value} -> {new_value}",
                                    "exact_time_delta": exact_time_delta,
                                    "approximative_time_delta": approximative_time_delta,
                                    "old_timestamp": old_timestamp,
                                }
                            )
                        )

        return to_ret

    def print_all_changes_since_previous(self, white_list_signal_types: Optional[List[SqlArchLineSignalType]], previous_line_for_this_id: "SqlArchArchiveLine") -> None:

        field_names_to_ignore = ["Time"]

        if white_list_signal_types is None or self.signal_type in white_list_signal_types:

            if not previous_line_for_this_id:
                if self.decoded_message is None:
                    logger_config.print_and_log_info(f"{self.date_raw} No previous line for ID {self.id_field}, now {self.get_new_state_str()}")
                else:
                    logger_config.print_and_log_info(f"{self.date_raw} No previous line for ID {self.id_field}")
                return

            previous_date = previous_line_for_this_id.get_date_raw_str()

            if self.decoded_message is None:
                # If no decoded message, only show newSt change
                previous_new_st = previous_line_for_this_id.get_new_state_str()
                new_new_st = self.get_new_state_str()
                if previous_new_st != new_new_st:
                    logger_config.print_and_log_info(f"{previous_date}\t{self.id_field}\tnewSt\t{previous_new_st} -> {new_new_st}")
            else:
                # If decoded message exists, show only decoded message fields that changed
                if previous_line_for_this_id.decoded_message:
                    for field_name in self.decoded_message.decoded_fields_flat_directory.keys():
                        if field_name not in field_names_to_ignore:
                            new_field = self.decoded_message.decoded_fields_flat_directory.get(field_name)
                            previous_field = previous_line_for_this_id.decoded_message.decoded_fields_flat_directory.get(field_name)

                            if new_field and previous_field:
                                new_value = self.decoded_message.get_field_value_human_readable(field_name)
                                previous_value = previous_line_for_this_id.decoded_message.get_field_value_human_readable(field_name)

                                if new_value != previous_value:
                                    logger_config.print_and_log_info(f"{previous_date}\t{self.id_field}\t(id_msg:{self.decoded_message.message_number})\t{field_name}\t{previous_value} -> {new_value}")


class ArchiveSource(ABC):

    def __init__(self) -> None:
        self.all_sqlarch_lines: List[SqlArchArchiveLine] = []

    @abstractmethod
    def get_all_archive_file_lines(self) -> List[str]:
        pass


class ArchiveLinesSet(ArchiveSource):
    def __init__(self, raw_archives_json_lines: List[str]) -> None:
        super().__init__()
        logger_config.print_and_log_info(f"Archive lines set has {len(raw_archives_json_lines)} lines")
        self.raw_archives_json_lines = raw_archives_json_lines

    def get_all_archive_file_lines(self) -> List[str]:
        return self.raw_archives_json_lines


class ArchiveFile(ArchiveSource):
    def __init__(self, file_full_path: str) -> None:
        super().__init__()
        self.file_full_path = file_full_path

    def get_all_archive_file_lines(self) -> List[str]:
        return self._open_and_get_all_archive_file_lines()

    def _open_and_get_all_archive_file_lines(self) -> List[str]:

        with logger_config.stopwatch_with_label(f"Open and read archive file lines {self.file_full_path}", monitor_ram_usage=True):
            with open(self.file_full_path, mode="r", encoding="utf-8") as file:
                all_raw_lines = file.readlines()
                logger_config.print_and_log_info(f"Archive file {self.file_full_path} has {len(all_raw_lines)} lines")
                return all_raw_lines
