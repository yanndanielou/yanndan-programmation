import re
from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import cast

from common import file_utils, reports_utils, string_utils
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
    label: str
    filename_pattern: str = "profibus*"
    upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary | None = None

    def __post_init__(self) -> None:
        if self.upper_layer_decoding_library is None:
            self.upper_layer_decoding_library = upper_layer_libraries.UpperLayerDecodingLibrary.from_next_json_file_full_path(
                json_file_full_path=r"D:\temp\GenTel\0.1-0-Original_Edition\GenTel\rom\unisig_s58.json"
            )

        self.all_ppn_logs_paths = file_utils.get_files_by_directory_and_file_name_mask(
            directory_path=self.directory_path,
            file_sort_order=file_utils.FileSortOrder.TIMESTAMP_OLDER_TO_NEWER,
            filename_pattern=self.filename_pattern,
        )

        self.decoded_files: list[ProfibusLogFile] = []
        self.decoded_lines: list[ProfibusLogLine] = []
        for ppn_log_path in self.all_ppn_logs_paths:
            decoded_file = ProfibusLogFile(
                file_full_path=ppn_log_path,
                upper_layer_decoding_library=self.upper_layer_decoding_library,
            )
            self.decoded_files.append(decoded_file)

        self._process_files()
        self._decode_sdn_or_sna()

        self.all_unisig_messages = [log_line.unisig_message for decoded_file in self.decoded_files for log_line in decoded_file.decoded_lines if log_line.unisig_message is not None]

        self.all_upper_layer_telegram = [upper_layer_telegram for upper_layer_telegram in self.all_unisig_messages if isinstance(upper_layer_telegram, decode_unisig.SdaForUpperLayerTelegram)]
        self.all_sl4_upper_layer_telegram = [
            upper_layer_telegram
            for upper_layer_telegram in self.all_unisig_messages
            if isinstance(upper_layer_telegram, decode_unisig.SdaForUpperLayerTelegram)
            and upper_layer_telegram.command_type == decode_unisig.SdaUnisigMessage.CommandTypeSubset57.SL4_TELEGRAM_FOR_UPPER_LAYER
        ]
        # [unisig_message for log_line in self.decoded_lines for unisig_message in log_line.unisig_messages]
        self.all_upper_layer_stms = [stm_message for upper_layer_telegram in self.all_upper_layer_telegram for stm_message in upper_layer_telegram.upper_layer_decoded_stms]

        self.unisig_messages_errors = [error for unisig_message in self.all_unisig_messages for error in unisig_message.creational_and_decoding_errors]
        self.stm_messages_errors = [error for stm_message in self.all_upper_layer_stms for error in stm_message.creational_and_decoding_errors]
        self.all_creational_errors = self.unisig_messages_errors + self.stm_messages_errors

        self.all_interlocutors = {log_line.interlocutors for log_line in self.decoded_lines}

        self.occurences_by_creational_error_type: dict[str, list[datetime | None]] = defaultdict(list)

        for unisig_message in self.all_unisig_messages:
            for error in unisig_message.creational_and_decoding_errors:
                self.occurences_by_creational_error_type[error].append(unisig_message.profibus_log_line.timestamp if unisig_message.profibus_log_line else None)

        for stm_message in self.all_upper_layer_stms:
            for error in stm_message.creational_and_decoding_errors:
                self.occurences_by_creational_error_type[error].append(stm_message.upper_layer_telegram.profibus_log_line.timestamp if stm_message.upper_layer_telegram.profibus_log_line else None)

        self._print_stats()

    def get_upper_layer_stms_by_stm_ids(self, allowed_stm_ids: list[int]) -> list[decode_unisig.UpperLayerStm]:
        return [upper_layer_stm for upper_layer_stm in self.all_upper_layer_stms if upper_layer_stm.nid_stm in allowed_stm_ids]

    def save_upper_layer_stms_by_stm_ids(self, allowed_stm_ids: list[int], label: str = "") -> None:
        interesting_stm_messages = self.get_upper_layer_stms_by_stm_ids(allowed_stm_ids)
        self.save_selected_stm_messages(
            interesting_stm_messages,
            file_base_name=f"{self.label} {label} stm messages {' '.join(str(interesting_stm_id) for interesting_stm_id in allowed_stm_ids)}",
        )

    def save_stm_messages_for_each_interlocutor(self) -> None:
        for interlocutors in self.all_interlocutors:
            self.save_selected_stm_messages(
                interesting_stm_messages=[
                    interesting_stm_message
                    for interesting_stm_message in self.all_upper_layer_stms
                    if interesting_stm_message.upper_layer_telegram.profibus_log_line and interesting_stm_message.upper_layer_telegram.profibus_log_line.interlocutors == interlocutors
                ],
                file_base_name=string_utils.format_filename(f"{self.label} {interlocutors}"),
            )

    @logger_config.stopwatch_decorator(monitor_ram_usage=True)
    def save_all_stm_messages_with_errors(self) -> None:
        self.save_selected_stm_messages(
            [stm_message for stm_message in self.all_upper_layer_stms if stm_message.creational_and_decoding_errors or stm_message.upper_layer_telegram.creational_and_decoding_errors],
            file_base_name=f"{self.label} all STM messages with errors",
        )

    @logger_config.stopwatch_decorator(monitor_ram_usage=True)
    def save_all_stm_messages(self) -> None:
        self.save_selected_stm_messages(self.all_upper_layer_stms, file_base_name=f"{self.label} all STM messages")

    @logger_config.stopwatch_decorator(monitor_ram_usage=True)
    def save_selected_stm_messages(self, interesting_stm_messages: list[decode_unisig.UpperLayerStm], file_base_name: str) -> None:
        logger_config.print_and_log_info(f"save_selected_stm_messages {len(interesting_stm_messages)} STM messages to {file_base_name}")

        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=[
                OrderedDict(
                    {
                        "timestamp": interesting_stm_message.upper_layer_telegram.profibus_log_line.timestamp if interesting_stm_message.upper_layer_telegram.profibus_log_line else None,
                        "Line Source": interesting_stm_message.upper_layer_telegram.profibus_log_line.source if interesting_stm_message.upper_layer_telegram.profibus_log_line else None,
                        "Line Target": interesting_stm_message.upper_layer_telegram.profibus_log_line.target if interesting_stm_message.upper_layer_telegram.profibus_log_line else None,
                        "interlocutors": interesting_stm_message.upper_layer_telegram.profibus_log_line.interlocutors if interesting_stm_message.upper_layer_telegram.profibus_log_line else None,
                        "Line Mode": interesting_stm_message.upper_layer_telegram.profibus_log_line.mode.name if interesting_stm_message.upper_layer_telegram.profibus_log_line else None,
                        "Line length": interesting_stm_message.upper_layer_telegram.profibus_log_line.length if interesting_stm_message.upper_layer_telegram.profibus_log_line else None,
                        "file path": interesting_stm_message.upper_layer_telegram.profibus_log_line.file_path if interesting_stm_message.upper_layer_telegram.profibus_log_line else None,
                        "line number": interesting_stm_message.upper_layer_telegram.profibus_log_line.line_number if interesting_stm_message.upper_layer_telegram.profibus_log_line else None,
                        "nid stm": interesting_stm_message.nid_stm,
                        "stm l_message": interesting_stm_message.l_message,
                        "stm data_without_header_size_in_bits": interesting_stm_message.data_without_header_size_in_bits,
                        "Number of errors (only this STM message)": len(interesting_stm_message.creational_and_decoding_errors),
                        "Number of errors (unisig message)": len(interesting_stm_message.upper_layer_telegram.creational_and_decoding_errors),
                        "Number of errors (STM + unisig message)": len(
                            interesting_stm_message.upper_layer_telegram.creational_and_decoding_errors + interesting_stm_message.upper_layer_telegram.creational_and_decoding_errors
                        ),
                        "STM messages decoded in this line": ",".join([str(stm_message.nid_stm) for stm_message in interesting_stm_message.upper_layer_telegram.upper_layer_decoded_stms]),
                        "CRC": interesting_stm_message.upper_layer_telegram.crc.crc_bits_as_string if interesting_stm_message.upper_layer_telegram.crc else None,
                        "Safe time layer timestamp (ms)": interesting_stm_message.upper_layer_telegram.stl_time_stamp_ms,
                        "Safe time layer timestamp (human format)": interesting_stm_message.upper_layer_telegram.stl_time_stamp_datetime,
                        "STM message: number remaining bits to decode": interesting_stm_message.number_remaining_undecoded_bits,
                        "STM message: remaining bits to decode": interesting_stm_message.remaining_undecoded_bits,
                        "log line: number remaining bits to decode": interesting_stm_message.upper_layer_telegram.number_remaining_undecoded_bits,
                        "log line: remaining bits to decode": interesting_stm_message.upper_layer_telegram.remaining_undecoded_bits,
                        "STM message errors": interesting_stm_message.creational_and_decoding_errors,
                        "Unisig message errors": interesting_stm_message.upper_layer_telegram.creational_and_decoding_errors,
                        "All errors (STM message + unisig message)": interesting_stm_message.creational_and_decoding_errors
                        + interesting_stm_message.upper_layer_telegram.creational_and_decoding_errors,
                        **{field_name: field_value for field_name, field_value in interesting_stm_message.fields_names_and_values.items()},
                    }
                )
                for interesting_stm_message in interesting_stm_messages
            ],
            file_base_name=file_base_name,
            create_csv_file=False,
            create_txt_file=False,
            split_big_files=False,
            chunk_size=200000,
        )

    def save_all_unisig_messages(self) -> None:
        logger_config.print_and_log_info(f"save_all_unisig_messages {len(self.all_unisig_messages)} unisig messages")
        self.save_selected_unisig_messages(
            selected_unisig_messages=self.all_unisig_messages,
            file_base_name=f"{self.label} all unisig messages",
        )

    def save_selected_unisig_messages(self, selected_unisig_messages: list[decode_unisig.UnisigMessage], file_base_name: str) -> None:
        with logger_config.stopwatch_with_label(f"save_selected_unisig_messages {len(self.all_unisig_messages)} unisig messages", monitor_ram_usage=True, inform_beginning=True):

            reports_utils.save_rows_to_output_files(
                rows_as_list_dict=[
                    OrderedDict(
                        {
                            "timestamp": unisig_message.profibus_log_line.timestamp if unisig_message.profibus_log_line else None,
                            "Line Source": unisig_message.profibus_log_line.source if unisig_message.profibus_log_line else None,
                            "Line Target": unisig_message.profibus_log_line.target if unisig_message.profibus_log_line else None,
                            "interlocutors": unisig_message.profibus_log_line.interlocutors if unisig_message.profibus_log_line else None,
                            "Line Mode": unisig_message.profibus_log_line.mode.name if unisig_message.profibus_log_line else None,
                            "Line length": unisig_message.profibus_log_line.length if unisig_message.profibus_log_line else None,
                            "file path": unisig_message.profibus_log_line.file_path if unisig_message.profibus_log_line else None,
                            "line number": unisig_message.profibus_log_line.line_number if unisig_message.profibus_log_line else None,
                            "Number of errors": len(unisig_message.creational_and_decoding_errors),
                            "CRC": unisig_message.crc.crc_bits_as_string if isinstance(unisig_message, decode_unisig.SdaUnisigMessage) and unisig_message.crc else None,
                            "Safe time layer timestamp (ms)": unisig_message.stl_time_stamp_ms if isinstance(unisig_message, decode_unisig.SdaUnisigMessage) else None,
                            "Safe time layer timestamp (human format)": unisig_message.stl_time_stamp_datetime if isinstance(unisig_message, decode_unisig.SdaUnisigMessage) else None,
                            "errors": unisig_message.creational_and_decoding_errors,
                        }
                    )
                    for unisig_message in selected_unisig_messages
                ],
                file_base_name=file_base_name,
                create_csv_file=False,
                create_txt_file=False,
                split_big_files=False,
                chunk_size=200000,
            )

    @logger_config.stopwatch_decorator()
    def _process_files(self) -> None:
        for decoded_file in self.decoded_files:
            decoded_file.process()
            self.decoded_lines += decoded_file.decoded_lines

    @logger_config.stopwatch_decorator()
    def _decode_sdn_or_sna(self) -> None:
        for decoded_file in self.decoded_files:
            for decoded_line in decoded_file.decoded_lines:
                decoded_line.decode_sdn_or_sna()

    def _print_stats(self) -> None:
        logger_config.print_and_log_info(f"Stats of {self.directory_path}")
        logger_config.print_and_log_info(f"{len(self.decoded_files)} files")
        logger_config.print_and_log_info(f"{len([log_line for log_file in self.decoded_files for log_line in log_file.decoded_lines])} lines")
        logger_config.print_and_log_info(f"{len(self.all_unisig_messages)} unisig_messages")
        logger_config.print_and_log_info(f"{len(self.all_upper_layer_telegram)} upper layer telegrams")
        logger_config.print_and_log_info(f"{len(self.all_sl4_upper_layer_telegram)} SL4 upper layer telegrams")
        logger_config.print_and_log_info(f"{len(self.all_upper_layer_stms)} STM messages founds")

        logger_config.print_and_log_info(f"{len(self.all_creational_errors)} creational errors")

        for error, all_timestamps in self.occurences_by_creational_error_type.items():
            logger_config.print_and_log_warning(f"{error}: {len(all_timestamps)} occurences")

        self.save_errors()

    @logger_config.stopwatch_decorator
    def save_errors(self) -> None:

        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=[
                OrderedDict(
                    {
                        "Error": error,
                        "Number occurences": len(all_timestamps),
                    }
                )
                for error, all_timestamps in self.occurences_by_creational_error_type.items()
            ],
            file_base_name=f"{self.label} all errors",
            create_csv_file=False,
            create_txt_file=False,
            split_big_files=False,
        )


@dataclass
class ProfibusLogFile:
    file_full_path: str
    encoding: str = "utf-8"
    upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary | None = None

    def __post_init__(self) -> None:
        self.decoded_lines: list[ProfibusLogLine] = []
        if self.upper_layer_decoding_library is None:
            self.upper_layer_decoding_library = upper_layer_libraries.UpperLayerDecodingLibrary.from_next_json_file_full_path(
                json_file_full_path=r"D:\temp\GenTel\0.1-0-Original_Edition\GenTel\rom\unisig_s58.json"
            )

    def process(self) -> None:

        with logger_config.stopwatch_with_label(f"Process {self.file_full_path}", monitor_ram_usage=True, inform_beginning=True) and open(self.file_full_path, "r", encoding=self.encoding) as f:
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
                    logger_config.print_and_log_error(f"Could not decode line {line} in file {self.file_full_path} line {line_number+1}")

    @property
    def unisig_messages(self) -> list[decode_unisig.UnisigMessage]:
        return [log_line.unisig_message for log_line in self.decoded_lines if log_line.unisig_message is not None]


@dataclass
class ProfibusLogLine:
    timestamp: datetime
    source: str
    target: str
    interlocutors: str
    sequence: int
    mode: SendingMode
    length: int
    bytes_hexa_str: str
    upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary
    file_path: str | None
    line_number: int | None

    def __post_init__(self) -> None:
        self.unisig_message: decode_unisig.UnisigMessage | None = None

    @staticmethod
    def get_equipment_name_from_address(address: int) -> str:

        equipment_name_dictionnary_by_sap = {
            2: "EVC",
            3: "JRU",
            5: "DMI",
            99: "STM",
            127: "MCast",
        }

        return equipment_name_dictionnary_by_sap.get(address) or f"Unknown {address}"

    @staticmethod
    def get_function_name_from_sap(sap: int) -> str:
        function_name_dictionnary_by_sap = {
            2: "/JD",
            4: "/CH 1",
            10: "/CH 1",
            32: "/Time",
            33: "/STM control",
            37: "/Train",
            38: "/Break",
            39: "/Odometer",
            44: "/CH 1 derog",
        }

        return function_name_dictionnary_by_sap.get(sap) or f"Unknown {sap}"

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

        line = line.lstrip("\x00")

        line = line.strip()

        fields = line.split(" ")
        if len(fields) <= 4:
            print(f"-> bad line format\n{line}")
            return None

        # Extract time: 1970-01-01 02:18:14:652
        timestamp = datetime.strptime(f"{fields[0]} {fields[1]}", "%Y-%m-%d %H:%M:%S:%f")  # noqa: DTZ007

        # Extract source and target: [99:37 <= 2:37]
        sap_pattern = re.compile(r"\[(\d+):(\d+) (<=|=>) (\d+):(\d+)\]")
        match = sap_pattern.search(line)
        if match:
            left_part_address = int(match.group(1))
            left_part_sap = int(match.group(2))

            right_part_address = int(match.group(4))
            right_part_sap = int(match.group(5))

            if match.group(3) == "=>":
                source_address = left_part_address
                source_sap = left_part_sap
                target_address = right_part_address
                target_sap = right_part_sap
            else:
                source_address = right_part_address
                source_sap = right_part_sap
                target_address = left_part_address
                target_sap = left_part_sap
        else:
            source_address = target_address = -1
            source_sap = target_sap = -1

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

        source = f"{ProfibusLogLine.get_equipment_name_from_address(source_address)}/{ProfibusLogLine.get_function_name_from_sap(source_sap)}"
        target = f"{ProfibusLogLine.get_equipment_name_from_address(target_address)}/{ProfibusLogLine.get_function_name_from_sap(target_sap)}"

        interlocutors = min([source, target]) + " <=> " + max([source, target])

        if mode in ("SDA", "SDN"):
            return ProfibusLogLine(
                timestamp=timestamp,
                source=f"{ProfibusLogLine.get_equipment_name_from_address(source_address)}/{ProfibusLogLine.get_function_name_from_sap(source_sap)}",
                target=f"{ProfibusLogLine.get_equipment_name_from_address(target_address)}/{ProfibusLogLine.get_function_name_from_sap(target_sap)}",
                interlocutors=interlocutors,
                sequence=sequence,
                mode=SendingMode[mode],
                length=length,
                bytes_hexa_str=bytes_hexa,
                upper_layer_decoding_library=upper_layer_decoding_library,
                file_path=file_path,
                line_number=line_number,
            )
        else:
            return None

    def decode_sdn_or_sna(self) -> None:
        if self.mode == SendingMode.SDA:
            try:
                self.unisig_message = decode_unisig.SdaUnisigMessage.from_sda_hexa_bytes_str(
                    profibus_log_line=self,
                    bytes_hexa_str=self.bytes_hexa_str,
                    upper_layer_decoding_library=self.upper_layer_decoding_library,
                )

                assert cast(decode_unisig.SdaUnisigMessage, self.unisig_message).byte_message_decoded.is_correctly_and_completely_decoded

            except (AssertionError, ValueError) as ass_err:
                logger_config.print_and_log_exception(ass_err)
                logger_config.print_and_log_error(
                    f"Could not decode SDA message at {self.timestamp} between {self.interlocutors} in file {self.file_path} line {self.line_number}, bytes_hexa_str:{self.bytes_hexa_str}"
                )

        else:
            try:
                self.unisig_message = decode_unisig.SdnUnisigMessage.decode_sdn_bytes_hexa(
                    profibus_log_line=self,
                    bytes_hexa=self.bytes_hexa_str,
                    upper_layer_decoding_library=self.upper_layer_decoding_library,
                )
            except (AssertionError, ValueError) as ass_err:
                logger_config.print_and_log_exception(ass_err)
