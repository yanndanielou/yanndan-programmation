import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

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
            for line in lines:
                try:
                    decoded_line = ProfibusLogLine.decode_raw_log_line(line=line, upper_layer_decoding_library=self.upper_layer_decoding_library)
                    if decoded_line is not None:
                        self.decoded_lines.append(decoded_line)

                except ValueError as val_err:
                    logger_config.print_and_log_exception(val_err)


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

    def __post_init__(self) -> None:
        self.unisig_messages: list[decode_unisig.UnisigMessage] = []

    @staticmethod
    def decode_raw_log_line(line: str, upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary | None = None) -> "ProfibusLogLine|None":
        if upper_layer_decoding_library is None:
            upper_layer_decoding_library = upper_layer_libraries.UpperLayerDecodingLibrary.from_next_json_file_full_path(
                json_file_full_path=r"D:\temp\GenTel\0.1-0-Original_Edition\GenTel\rom\unisig_s58.json"
            )

        while line.startswith("\x00"):
            line = line[1:]

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
            )
        else:
            return None

    def decode_sdn_or_sna(self) -> None:
        if self.mode == SendingMode.SDA:
            try:
                self.unisig_messages = decode_unisig.SdaUnisigMessage.from_sda_hexa_bytes_str(self.timestamp, self.bytes_hexa, self.upper_layer_decoding_library)
            except (AssertionError, ValueError) as ass_err:
                logger_config.print_and_log_exception(ass_err)
                logger_config.print_and_log_error(f"Could not decode SDA message at {self.timestamp}")

        else:
            try:
                self.unisig_messages = decode_unisig.SdnUnisigMessage.decode_sdn_bytes_hexa(self.timestamp, self.bytes_hexa, self.upper_layer_decoding_library)
            except (AssertionError, ValueError) as ass_err:
                logger_config.print_and_log_exception(ass_err)
