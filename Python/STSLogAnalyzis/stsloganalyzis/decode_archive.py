import json
from typing import Dict, cast, List, Optional

from logger import logger_config

from stsloganalyzis import decode_message, decode_action_set_content


ARCHIVE_VERSION_LINE_TAG = "VERSIONS"
ARCHIVE_SQLARCH_LINE_TAG = "SQLARCH"
ARCHIVE_SPMQ_LINE_TAG = "SPMQ"
ARCHIVE_ALARM_LINE_TAG = "ALARM"

ARCHIVE_VERSION_LINE_PREFIX = '{"' + ARCHIVE_VERSION_LINE_TAG + '":{'
ARCHIVE_SQLARCH_LINE_PREFIX = '{"' + ARCHIVE_SQLARCH_LINE_TAG + '":{'
ARCHIVE_SPMQ_LINE_PREFIX = '{"' + ARCHIVE_SPMQ_LINE_TAG + '":{'
ARCHIVE_ALARM_LINE_PREFIX = '{"' + ARCHIVE_ALARM_LINE_TAG + '":{'


class ArchiveDecoder:
    def __init__(self, messages_list_csv_file_full_path: str, xml_directory_path: str, action_set_content_csv_file_path: str) -> None:
        self.message_manager = decode_message.InvariantMessagesManager(messages_list_csv_file_full_path=messages_list_csv_file_full_path)
        self.xml_message_decoder = decode_message.XmlMessageDecoder(xml_directory_path=xml_directory_path)
        self.action_set_content_decoder = decode_action_set_content.ActionSetContentDecoder(csv_file_file_path=action_set_content_csv_file_path)
        self.message_decoder = decode_message.MessageDecoder(
            xml_directory_path=xml_directory_path, invariant_message_manager=self.message_manager, action_set_content_decoder=self.action_set_content_decoder
        )


class ArchiveExtract:
    def __init__(self) -> None:
        pass


class ArchiveFile:
    def __init__(self, file_full_path: str) -> None:
        self.file_full_path = file_full_path
        self.all_archive_lines: List[ArchiveLine] = []
        self.all_archive_lines_by_type: Dict[str, List[ArchiveLine]] = dict()
        self.all_sqlarch_lines: List[SqlArchArchiveLine] = []
        self.all_version_lines: List[VersionArchiveLine] = []
        self.all_spmq_lines: List[ArchiveLine] = []
        self.all_alarm_lines: List[ArchiveLine] = []

    def decode_all_lines(self, archive_decoder: ArchiveDecoder) -> int:
        number_of_lines_decoded = 0
        with logger_config.stopwatch_with_label(f"Decode all lines {self.file_full_path}"):

            for sqlarch_line in self.all_sqlarch_lines:
                sqlarch_line.decode_message(archive_decoder)

        return number_of_lines_decoded

    def open_and_read_archive_file_lines(self) -> None:

        with logger_config.stopwatch_with_label(f"Open and read archive file lines {self.file_full_path}"):
            with open(self.file_full_path, mode="r", encoding="utf-8") as file:
                all_raw_lines = file.readlines()
                logger_config.print_and_log_info(f"Archive file {self.file_full_path} has {len(all_raw_lines)} lines")
                for line_number, line in enumerate(all_raw_lines):
                    archive_line = ArchiveLine(full_raw_archive_line=line)

                    if line.startswith(ARCHIVE_VERSION_LINE_PREFIX):
                        archive_line = VersionArchiveLine(full_raw_archive_line=line)
                        self.all_version_lines.append(archive_line)
                    elif line.startswith(ARCHIVE_SQLARCH_LINE_PREFIX):
                        archive_line = SqlArchArchiveLine(full_raw_archive_line=line)
                        self.all_sqlarch_lines.append(archive_line)
                    elif line.startswith(ARCHIVE_SPMQ_LINE_PREFIX):
                        archive_line = ArchiveLine(full_raw_archive_line=line)
                        self.all_spmq_lines.append(archive_line)
                    elif line.startswith(ARCHIVE_ALARM_LINE_PREFIX):
                        archive_line = ArchiveLine(full_raw_archive_line=line)
                        self.all_alarm_lines.append(archive_line)
                    else:
                        logger_config.print_and_log_error(f"Unsupported line {line_number}:" + line)

                    self.all_archive_lines.append(archive_line)
                    archive_line_type = archive_line.tag

                    if archive_line_type not in self.all_archive_lines_by_type:
                        self.all_archive_lines_by_type[archive_line_type] = []

                    self.all_archive_lines_by_type[archive_line_type].append(archive_line)


class ArchiveLine:
    def __init__(self, full_raw_archive_line: str) -> None:

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
    def __init__(self, full_raw_archive_line: str) -> None:
        super().__init__(full_raw_archive_line=full_raw_archive_line)


class SqlArchArchiveLine(ArchiveLine):
    def __init__(self, full_raw_archive_line: str) -> None:
        super().__init__(full_raw_archive_line=full_raw_archive_line)

        # Accessing specific fields
        self.sqlarch_json_section: Dict = self.full_archive_line_as_json["SQLARCH"]

        # Accessing specific fields
        self.caller = self.sqlarch_json_section.get("caller")
        self.cat_ala = self.sqlarch_json_section.get("catAla")
        self.eqp = self.sqlarch_json_section.get("eqp")
        self.eqp_id = self.sqlarch_json_section.get("eqpId")
        self.exe_st = self.sqlarch_json_section.get("exeSt")
        self.id_field = self.sqlarch_json_section.get("id")
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
