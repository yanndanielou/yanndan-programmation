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
class ProfibusLogFile:
    file_full_path: str
    encoding: str = "utf-8"

    def __post_init__(self) -> None:
        self.lines: List[ProfibusLogLine] = []

    def process(self) -> None:
        with open(self.file_full_path, "r", encoding=self.encoding) as f:
            lines = f.readlines()
            for line in lines:
                decoded_line = ProfibusLogLine.decode_frame(line=line)
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
    def decode_frame(line: str) -> Optional["ProfibusLogLine"]:

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

    def decode_sdn_or_sna(self) -> None:
        if self.mode == SendingMode.SDA:
            sda_message = decode_unisig.SdaUnisigMessage.decode_bytes_hexa(self.bytes_hexa)
            pass


def main() -> None:

    line = "2026-06-02 17:38:09:961 kppn 1.3.3: [99:33 <= 2:33] Received PROFIBUS message [num:169690][mode:SDA][len:28] 1e 85 01 05 49 64 6c 65 20 63 79 63 6c 65 20 74 69 6d 65 6f 75 74 bc 0b 17 6d 17 78"

    decoded_frame = ProfibusLogLine.decode_frame(line)

    print(f"Valid frame: {decoded_frame is not None}")
    if decoded_frame:
        # Affichage des résultats
        print(f"Time: {decoded_frame.timestamp}")
        print(f"Source: {decoded_frame.source}")
        print(f"Target: {decoded_frame.target}")
        print(f"Sequence: {decoded_frame.sequence}")
        print(f"Mode: {decoded_frame.mode}")
        print(f"Length: {decoded_frame.length}")
        print(f"Bytes: {decoded_frame.bytes_hexa}")
        # Trame d'exemple donnée par l'utilisateur

        decoded_frame.decode_sdn_or_sna()


# Exemple d'utilisation
if __name__ == "__main__":
    main()
