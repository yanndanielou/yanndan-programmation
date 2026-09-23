import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from common import file_utils
from logger import logger_config

from stsloganalyzis.unisig import decode_unisig, upper_layer_libraries


class SendingMode(Enum):
    SDA = "SDA"
    SDN = "SDN"


@dataclass
class ServiceAccessPoint:
    number: int
    name: str


@dataclass
class ProfibusLogLibrary:
    directory_path: str
    filename_pattern: str = "profibus*"
    upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary | None = None

    def __post_init__(self) -> None:
        if self.upper_layer_decoding_library is None:
            self.upper_layer_decoding_library = upper_layer_libraries.UpperLayerDecodingLibrary.from_next_json_file_full_path(json_file_full_path=r"C:\Tools\GenTel\GenTel\rom\unisig_s58.json")

        self.all_ppn_logs_paths = file_utils.get_files_by_directory_and_file_name_mask(
            directory_path=self.directory_path,
            file_sort_order=file_utils.FileSortOrder.TIMESTAMP_OLDER_TO_NEWER,
            filename_pattern=self.filename_pattern,
        )

        self.decoded_files: list[ProfibusLogFile] = []
        for ppn_log_path in self.all_ppn_logs_paths:
            decoded_file = ProfibusLogFile(
                file_full_path=ppn_log_path,
                upper_layer_decoding_library=self.upper_layer_decoding_library,
            )
            self.decoded_files.append(decoded_file)

        self._process_files()
        self._decode_sdn_or_sna()

        self.unisig_messages = [unisig_message for decoded_file in self.decoded_files for log_line in decoded_file.decoded_lines for unisig_message in log_line.unisig_messages]

        self.all_upper_layer_telegram = [upper_layer_telegram for upper_layer_telegram in self.unisig_messages if isinstance(upper_layer_telegram, decode_unisig.UpperLayerTelegram)]
        self.all_sl4_upper_layer_telegram = [
            upper_layer_telegram
            for upper_layer_telegram in self.unisig_messages
            if isinstance(upper_layer_telegram, decode_unisig.UpperLayerTelegram)
            and upper_layer_telegram.command_type == decode_unisig.SdaUnisigMessage.CommandTypeSubset57.SL4_TELEGRAM_FOR_UPPER_LAYER
        ]
        # [unisig_message for log_line in self.decoded_lines for unisig_message in log_line.unisig_messages]
        self.all_upper_layer_stms = [stm_message for upper_layer_telegram in self.all_upper_layer_telegram for stm_message in upper_layer_telegram.upper_layer_decoded_stms]

        self.unisig_messages_errors = [error for unisig_message in self.unisig_messages for error in unisig_message.creational_and_decoding_errors]
        self.stm_messages_errors = [error for stm_message in self.all_upper_layer_stms for error in stm_message.creational_and_decoding_errors]
        self.all_creational_errors = self.unisig_messages_errors + self.stm_messages_errors

        self.occurences_by_creational_error_type: dict[str, list[datetime]] = defaultdict(list)

        for unisig_message in self.unisig_messages:
            for error in unisig_message.creational_and_decoding_errors:
                self.occurences_by_creational_error_type[error].append(unisig_message.profibus_log_line.timestamp)

        for stm_message in self.all_upper_layer_stms:
            for error in stm_message.creational_and_decoding_errors:
                self.occurences_by_creational_error_type[error].append(stm_message.upper_layer_telegram.profibus_log_line.timestamp)

        self._print_stats()

    def get_upper_layer_stms_by_stm_ids(self, allowed_stm_ids: list[int]) -> list[decode_unisig.UpperLayerStm]:
        return [upper_layer_stm for upper_layer_stm in self.all_upper_layer_stms if upper_layer_stm.nid_stm in allowed_stm_ids]

    @logger_config.stopwatch_decorator()
    def _process_files(self) -> None:
        for decoded_file in self.decoded_files:
            decoded_file.process()

    @logger_config.stopwatch_decorator()
    def _decode_sdn_or_sna(self) -> None:
        for decoded_file in self.decoded_files:
            for decoded_line in decoded_file.decoded_lines:
                decoded_line.decode_sdn_or_sna()

    def _print_stats(self) -> None:
        logger_config.print_and_log_info(f"Stats of {self.directory_path}")
        logger_config.print_and_log_info(f"{len(self.decoded_files)} files")
        logger_config.print_and_log_info(f"{len([log_line for log_file in self.decoded_files for log_line in log_file.decoded_lines])} lines")
        logger_config.print_and_log_info(f"{len(self.unisig_messages)} unisig_messages")
        logger_config.print_and_log_info(f"{len(self.all_upper_layer_telegram)} upper layer telegrams")
        logger_config.print_and_log_info(f"{len(self.all_sl4_upper_layer_telegram)} SL4 upper layer telegrams")
        logger_config.print_and_log_info(f"{len(self.all_upper_layer_stms)} STM messages founds")

        logger_config.print_and_log_info(f"{len(self.all_creational_errors)} creational errors")

        for error, all_timestamps in self.occurences_by_creational_error_type.items():
            logger_config.print_and_log_warning(f"{error}: {len(all_timestamps)} occurences")


@dataclass
class ProfibusLogFile:
    file_full_path: str
    encoding: str = "utf-8"
    upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary | None = None

    def __post_init__(self) -> None:
        self.decoded_lines: list[ProfibusLogLine] = []
        if self.upper_layer_decoding_library is None:
            self.upper_layer_decoding_library = upper_layer_libraries.UpperLayerDecodingLibrary.from_next_json_file_full_path(json_file_full_path=r"C:\Tools\GenTel\GenTel\rom\unisig_s58.json")

    def process(self) -> None:
        logger_config.print_and_log_info(f"Process {self.file_full_path}")
        with open(self.file_full_path, "r", encoding=self.encoding) as f:
            lines = f.readlines()
            for line_number, line in enumerate(lines):
                try:
                    decoded_line = ProfibusLogLine.decode_raw_log_line(
                        line=line,
                        upper_layer_decoding_library=self.upper_layer_decoding_library,
                        file_path=self.file_full_path,
                        line_number=line_number + 1,
                    )
                    if decoded_line is not None:
                        self.decoded_lines.append(decoded_line)

                except ValueError as val_err:
                    logger_config.print_and_log_exception(val_err)
                    logger_config.print_and_log_error(f"Could not decode line {line} in file {self.file_full_path}")

    @property
    def unisig_messages(self) -> list[decode_unisig.UnisigMessage]:
        return [unisig_message for log_line in self.decoded_lines for unisig_message in log_line.unisig_messages]


@dataclass
class ProfibusLogLine:
    timestamp: datetime
    source: int
    target: int
    sequence: int
    mode: SendingMode
    length: int
    bytes_hexa: str
    upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary
    file_path: str | None
    line_number: int | None

    def __post_init__(self) -> None:
        self.unisig_messages: list[decode_unisig.UnisigMessage] = []

    @staticmethod
    def decode_raw_log_line(
        line: str,
        upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary | None = None,
        file_path: str | None = None,
        line_number: int | None = None,
    ) -> "ProfibusLogLine|None":
        if upper_layer_decoding_library is None:
            upper_layer_decoding_library = upper_layer_libraries.UpperLayerDecodingLibrary.from_next_json_file_full_path(
                json_file_full_path=r"D:\temp\GenTel\0.1-0-Original_Edition\GenTel\rom\unisig_s58.json"
            )

        while line.startswith("\x00"):
            line = line[1:]

        line = line.strip()

        fields = line.split(" ")
        if len(fields) <= 4:
            print(f"-> bad line format\n{line}")
            return None

        # Extract time: 1970-01-01 02:18:14:652
        timestamp = datetime.strptime(f"{fields[0]} {fields[1]}", "%Y-%m-%d %H:%M:%S:%f")

        # Extract source and target: [99:37 <= 2:37]
        sap_pattern = re.compile(r"\[(\d+):(\d+) (<=|=>) (\d+):(\d+)\]")
        match = sap_pattern.search(line)
        if match:
            if match.group(3) == "=>":
                source = (int(match.group(1)) << 16) | int(match.group(2))
                target = (int(match.group(4)) << 16) | int(match.group(5))
            else:
                source = (int(match.group(4)) << 16) | int(match.group(5))
                target = (int(match.group(1)) << 16) | int(match.group(2))
        else:
            source = target = 0

        # Extract sequence: [num:43548]
        seq_pattern = re.compile(r"\[num:(\d+)\]")
        match = seq_pattern.search(line)
        if match:
            sequence = int(match.group(1))
        else:
            sequence = 0

        # Extract mode: [mode:SDA]
        mode_pattern = re.compile(r"\[mode:(SDN|SDA)\]")
        match = mode_pattern.search(line)
        if match:
            mode = match.group(1)
        else:
            mode = ""

        # Extract length: [len:51]
        len_pattern = re.compile(r"\[len:(\d+)\]")
        match = len_pattern.search(line)
        if match:
            length = int(match.group(1))
        else:
            length = 0

        # Extract trailing bytes
        bytes_hexa = line.split("]")[-1].strip()

        if mode in ("SDA", "SDN"):
            return ProfibusLogLine(
                timestamp=timestamp,
                source=source,
                target=target,
                sequence=sequence,
                mode=SendingMode[mode],
                length=length,
                bytes_hexa=bytes_hexa,
                upper_layer_decoding_library=upper_layer_decoding_library,
                file_path=file_path,
                line_number=line_number,
            )
        else:
            return None

    def decode_sdn_or_sna(self) -> None:
        if self.mode == SendingMode.SDA:
            try:
                self.unisig_messages = decode_unisig.SdaUnisigMessage.from_sda_hexa_bytes_str(
                    profibus_log_line=self,
                    bytes_hexa=self.bytes_hexa,
                    upper_layer_decoding_library=self.upper_layer_decoding_library,
                )
            except (AssertionError, ValueError) as ass_err:
                logger_config.print_and_log_exception(ass_err)
                logger_config.print_and_log_error(f"Could not decode SDA message at {self.timestamp}")

        else:
            try:
                self.unisig_messages = decode_unisig.SdnUnisigMessage.decode_sdn_bytes_hexa(
                    profibus_log_line=self,
                    bytes_hexa=self.bytes_hexa,
                    upper_layer_decoding_library=self.upper_layer_decoding_library,
                )
            except (AssertionError, ValueError) as ass_err:
                logger_config.print_and_log_exception(ass_err)
