import json
import re
from enum import Enum
from typing import Callable, Dict, List, Optional, Self, cast, Set

from common import file_utils
from logger import logger_config

ArchiveLineFilter = Callable[[str, "ArchiveSource"], bool]


class ArchiveLineFilterOnIdType(Enum):
    BEGIN_WITH_STRING = "BEGIN_WITH_STRING"
    MATCHES_REGEX = "MATCHES_REGEX"
    CONTAINS = "CONTAINS"


from abc import ABC, abstractmethod

from stsloganalyzis import decode_action_set_content, decode_message


class ArchiveLineTag(Enum):
    VERSION = "VERSIONS"
    SQLARCH = "SQLARCH"
    SPMQ = "SPMQ"
    ALARM = "ALARM"


class SqlArchLineSignalType(Enum):
    TRAIN = "TRAIN"
    TCA = "OUTGOING_MESSAGES"
    TSA = "INCOMMING_MESSAGES"
    TG = "TG"
    SY = "Syntheses"
    TS = "TS"
    CR = "ACKNOWLEDGE"
    TB = "TRACKING_BLOCK"


ARCHIVE_VERSION_LINE_PREFIX = '{"' + ArchiveLineTag.VERSION.value + '":{'
ARCHIVE_SQLARCH_LINE_PREFIX = '{"' + ArchiveLineTag.SQLARCH.value + '":{'
ARCHIVE_SPMQ_LINE_PREFIX = '{"' + ArchiveLineTag.SPMQ.value + '":{'
ARCHIVE_ALARM_LINE_PREFIX = '{"' + ArchiveLineTag.ALARM.value + '":{'


class ArchiveDecoder:
    def __init__(self, messages_list_csv_file_full_path: str, xml_directory_path: str, action_set_content_csv_file_path: str) -> None:
        self.message_manager = decode_message.InvariantMessagesManager(messages_list_csv_file_full_path=messages_list_csv_file_full_path)
        self.xml_message_decoder = decode_message.XmlMessageDecoder(xml_directory_path=xml_directory_path)
        self.action_set_content_decoder = decode_action_set_content.ActionSetContentDecoder(csv_file_file_path=action_set_content_csv_file_path)
        self.message_decoder = decode_message.MessageDecoder(xml_directory_path=xml_directory_path, action_set_content_decoder=self.action_set_content_decoder)


class ArchiveLibrary:
    class Builder:
        def __init__(self) -> None:
            self._library = ArchiveLibrary()

            self.archive_inputs: List[ArchiveSource] = []
            self.archive_decoder: Optional[ArchiveDecoder] = None
            self.sqlarch_archive_lines_whitelist_filters: List[ArchiveLineFilter] = []
            self.sqlarch_archive_lines_blacklist_filters: List[ArchiveLineFilter] = []
            self.signal_type_whitelist: List[SqlArchLineSignalType] = []
            self.signal_type_blacklist: List[SqlArchLineSignalType] = []

        def add_raw_archives_json_lines(self, raw_archives_json_lines: List[str]) -> Self:
            self.archive_inputs.append(ArchiveLinesSet(raw_archives_json_lines=raw_archives_json_lines))
            return self

        def add_archive_files(self, directory_path: str, filename_pattern: str) -> Self:
            for file_full_path in file_utils.get_files_by_directory_and_file_name_mask(directory_path, filename_pattern, file_sort_order=file_utils.FileSortOrder.TIMESTAMP_OLDER_TO_NEWER):
                self.add_archive_file(file_full_path=file_full_path)
            return self

        def add_archive_file(self, file_full_path: str) -> Self:
            self.archive_inputs.append(ArchiveFile(file_full_path=file_full_path))
            return self

        def add_sqlarch_archive_lines_whitelist_filter_based_on_id_term(self, filter_text: str, filterOnIdType: ArchiveLineFilterOnIdType) -> Self:
            self.sqlarch_archive_lines_whitelist_filters.append(self._build_id_filter(filter_text, filterOnIdType))
            return self

        def add_sqlarch_archive_lines_blacklist_filter_based_on_id_term(self, filter_text: str, filterOnIdType: ArchiveLineFilterOnIdType) -> Self:
            self.sqlarch_archive_lines_blacklist_filters.append(self._build_id_filter(filter_text, filterOnIdType))
            return self

        def add_sqlarch_archive_lines_signal_type_whitelist(self, signal_types: List[SqlArchLineSignalType]) -> Self:
            self.signal_type_whitelist.extend(signal_types)
            return self

        def add_sqlarch_archive_lines_signal_type_blacklist(self, signal_types: List[SqlArchLineSignalType]) -> Self:
            self.signal_type_blacklist.extend(signal_types)
            return self

        def _build_id_filter(self, filter_text: str, filterOnIdType: ArchiveLineFilterOnIdType) -> ArchiveLineFilter:
            def archive_line_filter(line: str, _parent: "ArchiveSource") -> bool:
                if not line.startswith(ARCHIVE_SQLARCH_LINE_PREFIX):
                    return True
                try:
                    line_json = json.loads(line)
                    sqlarch_section = line_json.get("SQLARCH", {})
                    id_value = str(sqlarch_section.get("id", ""))
                except (TypeError, ValueError, json.JSONDecodeError):
                    return False

                if filterOnIdType == ArchiveLineFilterOnIdType.BEGIN_WITH_STRING:
                    return id_value.startswith(filter_text)
                elif filterOnIdType == ArchiveLineFilterOnIdType.MATCHES_REGEX:
                    return re.search(filter_text, id_value) is not None
                elif filterOnIdType == ArchiveLineFilterOnIdType.CONTAINS:
                    return filter_text in id_value

            return archive_line_filter

        def add_archive_decoder(self, archive_decoder: ArchiveDecoder) -> Self:
            assert self.archive_decoder is None
            self.archive_decoder = archive_decoder
            return self

        def build(self) -> "ArchiveLibrary":
            self._library.sqlarch_archive_lines_whitelist_filters = self.sqlarch_archive_lines_whitelist_filters
            self._library.sqlarch_archive_lines_blacklist_filters = self.sqlarch_archive_lines_blacklist_filters
            self._library.signal_type_whitelist = self.signal_type_whitelist
            self._library.signal_type_blacklist = self.signal_type_blacklist

            for archive_input in self.archive_inputs:
                self._library.handle_input(archive_input)

            if self.archive_decoder:
                self._library.decode_all_lines(archive_decoder=self.archive_decoder)
            return self._library

    def __init__(self) -> None:
        self.archive_inputs: List["ArchiveSource"] = []
        self.all_archive_lines: List[ArchiveLine] = []
        self.all_archive_lines_by_type: Dict[ArchiveLineTag, List[ArchiveLine]] = dict()
        self._last_sqlarch_line_by_id: Dict[str, SqlArchArchiveLine] = dict()
        self.all_sqlarch_lines: List[SqlArchArchiveLine] = []
        self.all_version_lines: List[VersionArchiveLine] = []
        self.all_spmq_lines: List[ArchiveLine] = []
        self.all_alarm_lines: List[ArchiveLine] = []
        self.sqlarch_archive_lines_whitelist_filters: List[ArchiveLineFilter] = []
        self.sqlarch_archive_lines_blacklist_filters: List[ArchiveLineFilter] = []
        self.signal_type_whitelist: List[SqlArchLineSignalType] = []
        self.signal_type_blacklist: List[SqlArchLineSignalType] = []

        self.previous_line_by_id: Dict[str, SqlArchArchiveLine] = dict()

    def handle_input(self, archive_input: "ArchiveSource") -> int:
        self.archive_inputs.append(archive_input)

        line_number = 0
        for line_number, line in enumerate(archive_input.get_all_archive_file_lines()):
            self._process_archive_raw_line(line_number=line_number, line=line, parent=archive_input)

        return line_number

    def decode_all_lines(self, archive_decoder: ArchiveDecoder) -> int:
        number_of_lines_decoded = 0
        with logger_config.stopwatch_with_label(f"Decode all {len(self.all_sqlarch_lines)} lines"):

            for sqlarch_line in self.all_sqlarch_lines:
                sqlarch_line.decode_message(archive_decoder)

        return number_of_lines_decoded

    def _passes_sqlarch_archive_line_filters(self, line: str, parent: "ArchiveSource") -> bool:
        # Parse the line to get id and signal_type
        try:
            line_json = json.loads(line)
            sqlarch_section = line_json.get("SQLARCH", {})
            id_value = str(sqlarch_section.get("id", ""))
            signal_type_raw = str(sqlarch_section.get("sigT", ""))
            signal_type = SqlArchLineSignalType[signal_type_raw] if signal_type_raw else None
        except (TypeError, ValueError, json.JSONDecodeError, KeyError):
            return False

        # Check whitelist: all whitelist filters must pass (return True)
        if self.sqlarch_archive_lines_whitelist_filters and not all(f(line, parent) for f in self.sqlarch_archive_lines_whitelist_filters):
            return False

        # Check blacklist: all blacklist filters must pass (return True, meaning no match)
        if self.sqlarch_archive_lines_blacklist_filters and not all(f(line, parent) for f in self.sqlarch_archive_lines_blacklist_filters):
            return False

        # Check signal_type whitelist
        if self.signal_type_whitelist and signal_type not in self.signal_type_whitelist:
            return False

        # Check signal_type blacklist
        if self.signal_type_blacklist and signal_type in self.signal_type_blacklist:
            return False

        return True

    def _process_archive_raw_line(self, line_number: int, line: str, parent: "ArchiveSource") -> None:

        archive_line: ArchiveLine

        if line.startswith(ARCHIVE_VERSION_LINE_PREFIX):
            archive_line = VersionArchiveLine(full_raw_archive_line=line, parent=parent)
            self.all_version_lines.append(archive_line)
        elif line.startswith(ARCHIVE_SQLARCH_LINE_PREFIX):

            if not self._passes_sqlarch_archive_line_filters(line=line, parent=parent):
                return

            archive_line = SqlArchArchiveLine(full_raw_archive_line=line, parent=parent, last_sqlarch_line_by_id=self._last_sqlarch_line_by_id)
            self._last_sqlarch_line_by_id[archive_line.id_field] = archive_line

            self.all_sqlarch_lines.append(archive_line)
        elif line.startswith(ARCHIVE_SPMQ_LINE_PREFIX):
            archive_line = ArchiveLine(full_raw_archive_line=line, parent=parent)
            self.all_spmq_lines.append(archive_line)
        elif line.startswith(ARCHIVE_ALARM_LINE_PREFIX):
            archive_line = ArchiveLine(full_raw_archive_line=line, parent=parent)
            self.all_alarm_lines.append(archive_line)
        else:
            logger_config.print_and_log_error(f"Unsupported line {line_number}:" + line)

        self.all_archive_lines.append(archive_line)
        archive_line_type = archive_line.tag

        if archive_line_type not in self.all_archive_lines_by_type:
            self.all_archive_lines_by_type[ArchiveLineTag[archive_line_type]] = []

        self.all_archive_lines_by_type[ArchiveLineTag[archive_line_type]].append(archive_line)

    def get_all_signal_types(self) -> Set[str]:
        return {line.signal_type_raw for line in self.all_sqlarch_lines}


class ArchiveSource(ABC):
    @abstractmethod
    def get_all_archive_file_lines(self) -> List[str]:
        pass


class ArchiveLinesSet(ArchiveSource):
    def __init__(self, raw_archives_json_lines: List[str]) -> None:
        logger_config.print_and_log_info(f"Archive lines set has {len(raw_archives_json_lines)} lines")
        self.raw_archives_json_lines = raw_archives_json_lines

    def get_all_archive_file_lines(self) -> List[str]:
        return self.raw_archives_json_lines


class ArchiveFile(ArchiveSource):
    def __init__(self, file_full_path: str) -> None:
        self.file_full_path = file_full_path

    def get_all_archive_file_lines(self) -> List[str]:
        return self._open_and_get_all_archive_file_lines()

    def _open_and_get_all_archive_file_lines(self) -> List[str]:

        with logger_config.stopwatch_with_label(f"Open and read archive file lines {self.file_full_path}"):
            with open(self.file_full_path, mode="r", encoding="utf-8") as file:
                all_raw_lines = file.readlines()
                logger_config.print_and_log_info(f"Archive file {self.file_full_path} has {len(all_raw_lines)} lines")
                return all_raw_lines


class ArchiveLine:
    def __init__(self, full_raw_archive_line: str, parent: ArchiveSource) -> None:
        self.parent = parent
        self.full_raw_archive_line = full_raw_archive_line
        # Parsing JSON string
        self.full_archive_line_as_json: Dict = json.loads(full_raw_archive_line)

        # Access global fields
        self.date_raw = self.full_archive_line_as_json["date"]
        self.tags: List[str] = self.full_archive_line_as_json["tags"]
        self.tag: str = self.tags[0]

        self.all_fields_dict: Dict[str, str | int | bool] = self.full_archive_line_as_json.get(self.tag, {})
        self.all_fields_dict["date_raw"] = self.date_raw

    def get_date_raw_str(self) -> str:
        return cast(str, self.date_raw)


class VersionArchiveLine(ArchiveLine):
    def __init__(self, full_raw_archive_line: str, parent: ArchiveSource) -> None:
        super().__init__(full_raw_archive_line=full_raw_archive_line, parent=parent)


class SqlArchArchiveLine(ArchiveLine):
    def __init__(self, full_raw_archive_line: str, parent: ArchiveSource, last_sqlarch_line_by_id: Dict[str, "SqlArchArchiveLine"]) -> None:
        super().__init__(full_raw_archive_line=full_raw_archive_line, parent=parent)

        # Accessing specific fields
        self.sqlarch_json_section: Dict[str, str | int] = self.full_archive_line_as_json["SQLARCH"]

        # Accessing specific fields
        self.caller = self.sqlarch_json_section.get("caller")
        self.cat_ala = self.sqlarch_json_section.get("catAla")
        self.eqp = self.sqlarch_json_section.get("eqp")
        self.eqp_id = self.sqlarch_json_section.get("eqpId")
        self.exe_st = self.sqlarch_json_section.get("exeSt")
        self.id_field = str(self.sqlarch_json_section.get("id"))
        self.signal_type_raw = str(self.sqlarch_json_section.get("sigT"))
        self.signal_type = SqlArchLineSignalType[self.signal_type_raw] if self.signal_type_raw else None
        assert self.id_field is not None
        assert isinstance(self.id_field, str)

        self.previous_line_for_this_id = last_sqlarch_line_by_id[self.id_field] if self.id_field in last_sqlarch_line_by_id else None

        self.jdb = self.sqlarch_json_section.get("jdb")
        self.label = self.sqlarch_json_section.get("label")
        self.loc = self.sqlarch_json_section.get("loc")

        self.sqlarch_fields_dict_raw: dict[str, str | int | bool] = dict()
        self.invariant_message: Optional[decode_message.InvariantMessage] = None
        self.decoded_message: Optional[decode_message.DecodedMessage] = None

    def decode_message(self, archive_decoder: ArchiveDecoder) -> None:
        # Directly copy all items from SQLARCH section into a new dictionary
        self.sqlarch_fields_dict_raw = {f"{key}_raw": value for key, value in self.all_fields_dict.items()}
        self.invariant_message = archive_decoder.message_manager.get_message_by_id(self.get_id())
        if self.invariant_message:
            self.decoded_message = archive_decoder.xml_message_decoder.decode_xml_fields_in_message_hexadecimal(
                message_number=self.invariant_message.message_number, hexadecimal_content=self.get_new_state_str()
            )

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

    def print_and_log_with_following_fields(self, fields_names_to_print: List[str]) -> None:
        to_print_and_log = self._get_print_prefix()
        assert self.decoded_message
        assert self.decoded_message.all_fields_by_name
        for field_name_to_print in fields_names_to_print:
            assert self.decoded_message.all_fields_by_name[field_name_to_print]
            # to_print_and_log += f"{field_name_to_print}:{self.decoded_message.all_fields_by_name[field_name_to_print].value}"
            to_print_and_log += f", {field_name_to_print}:{self.decoded_message.get_field_value_human_readable(field_name_to_print)}"

        logger_config.print_and_log_info(to_print_and_log=to_print_and_log)

    def print_and_log_with_all_fields(self) -> None:
        fields_names_to_print: List[str] = []
        if self.decoded_message:
            fields_names_to_print += self.decoded_message.all_fields_by_name.keys()
            self.print_and_log_with_following_fields(fields_names_to_print)
        else:
            to_print_and_log = self._get_print_prefix()
            to_print_and_log += ", new state=" + self.get_new_state_str()
            logger_config.print_and_log_info(to_print_and_log=to_print_and_log)

    def print_all_changes_since_previous(self, white_list_signal_types: Optional[List[SqlArchLineSignalType]]) -> None:

        field_names_to_ignore = ["Time"]

        if white_list_signal_types is None or self.signal_type in white_list_signal_types:

            if not self.previous_line_for_this_id:
                if self.decoded_message is None:
                    logger_config.print_and_log_info(f"{self.date_raw} No previous line for ID {self.id_field}, now {self.get_new_state_str()}")
                else:
                    logger_config.print_and_log_info(f"{self.date_raw} No previous line for ID {self.id_field}")
                return

            previous_date = self.previous_line_for_this_id.get_date_raw_str()

            if self.decoded_message is None:
                # If no decoded message, only show newSt change
                previous_new_st = self.previous_line_for_this_id.get_new_state_str()
                new_new_st = self.get_new_state_str()
                if previous_new_st != new_new_st:
                    logger_config.print_and_log_info(f"{previous_date}\t{self.id_field}\tnewSt\t{previous_new_st} -> {new_new_st}")
            else:
                # If decoded message exists, show only decoded message fields that changed
                if self.previous_line_for_this_id.decoded_message:
                    for field_name in self.decoded_message.all_fields_by_name.keys():
                        if field_name not in field_names_to_ignore:
                            new_field = self.decoded_message.all_fields_by_name.get(field_name)
                            previous_field = self.previous_line_for_this_id.decoded_message.all_fields_by_name.get(field_name)

                            if new_field and previous_field:
                                new_value = self.decoded_message.get_field_value_human_readable(field_name)
                                previous_value = self.previous_line_for_this_id.decoded_message.get_field_value_human_readable(field_name)

                                if new_value != previous_value:
                                    logger_config.print_and_log_info(f"{previous_date}\t{self.id_field}\t(id_msg:{self.decoded_message.message_number})\t{field_name}\t{previous_value} -> {new_value}")
