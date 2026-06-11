import binascii
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from common import bytes_messages

from stsloganalyzis.unisig import decode_unisig


class SendingMode(Enum):
    SDA = "SDA"
    SDN = "SDN"

@dataclass
class ServiceAccessPoint:
    number:int
    name:str

class ServiceAccessPointLibrary:



@dataclass
class ProfibusLogFile:
    file_full_path: str
    encoding: str = "utf-8"

    def __post_init__(self) -> None:
        self.lines: List[ProfibusLogLine] = []

    def process(self) -> None:
        with open(self.file_full_path, "r", encoding=self.encoding) as f:
            lines = f.readlines()
            for line in lines:
                decoded_line = ProfibusLogLine.decode_raw_log_line(line=line)
                if decoded_line is not None:
                    self.lines.append(decoded_line)


@dataclass
class ProfibusLogLine:
    timestamp: datetime
    source: int
    target: int
    sequence: int
    mode: SendingMode
    length: int
    bytes_hexa: str

    @staticmethod
    def decode_raw_log_line(line: str) -> Optional["ProfibusLogLine"]:

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
            )
        else:
            return None

    def decode_sdn_or_sna(self) -> Optional[decode_unisig.UnisigMessage]:
        if self.mode == SendingMode.SDA:
            sda_message = decode_unisig.decode_sda_bytes_hexa(self.bytes_hexa)
            return sda_message
        return None
