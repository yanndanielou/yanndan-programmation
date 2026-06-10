import binascii
import re
from abc import ABC
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum, IntEnum, auto
from typing import Dict, Optional, Tuple, Union

from common import bytes_messages
from dateutil import parser

SL4_CRC_SIZE_IN_BYTES = 6
SL4_CRC_SIZE_IN_BITES = SL4_CRC_SIZE_IN_BYTES * bytes_messages.NUMBER_OF_BITS_IN_BYTE

SL0_CRC_SIZE_IN_BYTES = 0
SL0_CRC_SIZE_IN_BITES = SL0_CRC_SIZE_IN_BYTES * bytes_messages.NUMBER_OF_BITS_IN_BYTE


class SafetyLevel(IntEnum):
    SL0 = 0
    SL4 = 4


class UnisigMessage(ABC):
    pass


class SdnUnisigMessage(UnisigMessage):
    pass

    @staticmethod
    def decode_bytes_hexa(bytes_hexa: str) -> "SdnUnisigMessage":
        pass


@dataclass
class SdaUnisigMessage(UnisigMessage):
    safety_level: SafetyLevel
    byte_message_decoded: bytes_messages.DecodedBytesMessage
    lowest_order_byte_sequence_number: int

    @property
    def crc_size_in_bits(self) -> int:
        if self.safety_level == SafetyLevel.SL4:
            return int(SL4_CRC_SIZE_IN_BITES)
        elif self.safety_level == SafetyLevel.SL0:
            return int(SL0_CRC_SIZE_IN_BITES)
        else:
            assert False

    @property
    def crc_size_in_bytes(self) -> int:
        return self.crc_size_in_bits // bytes_messages.NUMBER_OF_BITS_IN_BYTE

    class CommandType(IntEnum):
        SL4_IDLE_TELEGRAM = int("0x86", 16)
        SL0_IDLE_TELEGRAM = int("0xC6", 16)
        SL4_CONNECT_REQUEST_TELEGRAM = int("0x80", 16)
        SL0_CONNECT_REQUEST_TELEGRAM = int("0xC0", 16)
        SL4_CONNECT_CONFIRM_TELEGRAM = int("0x82", 16)
        SL0_CONNECT_CONFIRM_TELEGRAM = int("0xC2", 16)
        SL4_AUTHENTICATION_TELEGRAM = int("0x83", 16)
        SL4_AUTHENTICATION_ACKNOWLEDGEMENT_TELEGRAM = int("0x84", 16)
        SL4_READY_TO_RUN = int("0xA2", 16)
        SL0_READY_TO_RUN = int("0xE2", 16)
        SL4_RUN = int("0xA3", 16)
        SL0_RUN = int("0xE3", 16)
        SL4_DISCONNECT_TELEGRAM = int("0x85", 16)
        SL0_DISCONNECT_TELEGRAM = int("0xC5", 16)
        SL4_TELEGRAM_FOR_UPPER_LAYER = int("0x89", 16)
        SL0_TELEGRAM_FOR_UPPER_LAYER = int("0xC9", 16)


@dataclass
class SdaDisconnectTelegram(SdaUnisigMessage):

    def __post_init__(self) -> None:
        self.new_setup_desired = self.byte_message_decoded.get_next_bits_as_bool_0_or_1(size_bits=bytes_messages.NUMBER_OF_BITS_IN_BYTE)
        self.disconnect_reason_raw = self.byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=bytes_messages.NUMBER_OF_BITS_IN_BYTE)
        disconnect_reason_text_length_in_bits = len(self.byte_message_decoded.hex_bytes) * bytes_messages.NUMBER_OF_BITS_IN_BYTE - self.byte_message_decoded.current_bit_index - self.crc_size_in_bits
        self.disconnect_reason_text = self.byte_message_decoded.get_next_bits_as_ascii_char(
            number_of_chars=disconnect_reason_text_length_in_bits // bytes_messages.NUMBER_OF_BITS_IN_BYTE, size_bits_per_char=bytes_messages.NUMBER_OF_BITS_IN_BYTE
        )
        self.crc = self.byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=self.crc_size_in_bits) if self.crc_size_in_bits > 0 else None
        pass


@dataclass
class SdaIdleTelegram(SdaUnisigMessage):

    def __post_init__(self) -> None:
        self.crc = self.byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=self.crc_size_in_bits) if self.crc_size_in_bits > 0 else None
        pass


@staticmethod
def decode_sda_bytes_hexa(bytes_hexa: str) -> Optional[SdaUnisigMessage]:
    byte_message_decoded = bytes_messages.DecodedBytesMessage(bytes_hexa)
    mistery_0 = byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=bytes_messages.NUMBER_OF_BITS_IN_BYTE)
    raw_command = byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=bytes_messages.NUMBER_OF_BITS_IN_BYTE)
    command_type = SdaUnisigMessage.CommandType(raw_command)

    if command_type == SdaUnisigMessage.CommandType.SL0_DISCONNECT_TELEGRAM or command_type == SdaUnisigMessage.CommandType.SL4_DISCONNECT_TELEGRAM:
        return SdaDisconnectTelegram(
            safety_level=SafetyLevel[command_type.name[:3]],
            byte_message_decoded=byte_message_decoded,
            lowest_order_byte_sequence_number=mistery_0,
        )

    if command_type == SdaUnisigMessage.CommandType.SL0_IDLE_TELEGRAM or command_type == SdaUnisigMessage.CommandType.SL4_IDLE_TELEGRAM:
        return SdaIdleTelegram(
            safety_level=SafetyLevel[command_type.name[:3]],
            byte_message_decoded=byte_message_decoded,
            lowest_order_byte_sequence_number=mistery_0,
        )
    return None
