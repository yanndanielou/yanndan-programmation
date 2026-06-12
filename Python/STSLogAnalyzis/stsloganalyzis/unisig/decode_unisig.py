import binascii
import re
from abc import ABC
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum, IntEnum, auto
from typing import Optional, cast, List

from common import bytes_messages
from dateutil import parser

from logger import logger_config

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


@dataclass
class SdaUnisigMessage(UnisigMessage):
    safety_level: SafetyLevel
    telegram_name: str
    byte_message_decoded: bytes_messages.DecodedBytesMessage
    lowest_order_byte_sequence_number: int
    command_type: "SdaUnisigMessage.CommandType"

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
        return cast(int, self.crc_size_in_bits // bytes_messages.NUMBER_OF_BITS_IN_BYTE)

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
        disconnect_reason_text_length_in_bits = self.byte_message_decoded.number_of_bits_remaining_to_decode - self.crc_size_in_bits
        self.disconnect_reason_text = self.byte_message_decoded.get_next_bits_as_ascii_char(number_of_chars=disconnect_reason_text_length_in_bits // bytes_messages.NUMBER_OF_BITS_IN_BYTE)
        self.crc = self.byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=self.crc_size_in_bits) if self.crc_size_in_bits > 0 else None
        pass


@dataclass
class SdaConnectRequestOrConfirmTelegram(SdaUnisigMessage):

    def __post_init__(self) -> None:
        self.random_number_representing_sequence_number = self.byte_message_decoded.get_next_bytes_as_single_int_unsigned(size_bytes=4)
        self.idle_cycle_timeout_in_100ms = self.byte_message_decoded.get_next_bytes_as_single_int_unsigned(size_bytes=2)
        self.configuration_data_prefix_x = self.byte_message_decoded.get_next_byte_as_single_int_unsigned()
        assert self.configuration_data_prefix_x == 3
        self.configuration_data_prefix_y = self.byte_message_decoded.get_next_byte_as_single_int_unsigned()
        assert self.configuration_data_prefix_y == 0
        self.configuration_data_prefix_z = self.byte_message_decoded.get_next_byte_as_single_int_unsigned()
        assert self.configuration_data_prefix_z == 0
        dual_bus_length_in_bits = self.byte_message_decoded.number_of_bits_remaining_to_decode - self.crc_size_in_bits
        self.dual_bus = self.byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=dual_bus_length_in_bits)
        self.crc = self.byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=self.crc_size_in_bits) if self.crc_size_in_bits > 0 else None
        pass


@dataclass
class SdaAuthenticationOrAuthenticationAcknowledgementTelegram(SdaUnisigMessage):

    def __post_init__(self) -> None:
        self.authentication_number = self.byte_message_decoded.get_next_bytes_as_single_int_unsigned(size_bytes=4)
        self.crc = self.byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=self.crc_size_in_bits)


@dataclass
class SdaRunOrReadyToRunTelegram(SdaUnisigMessage):

    def __post_init__(self) -> None:
        self.stl_time_stamp_ms = self.byte_message_decoded.get_next_bytes_as_single_int_unsigned(size_bytes=4)


@dataclass
class SdaGenericTelegram(SdaUnisigMessage):

    def __post_init__(self) -> None:
        self.crc = self.byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=self.crc_size_in_bits) if self.crc_size_in_bits > 0 else None
        pass


def decode_sda_bytes_hexa(bytes_hexa: str) -> List[UnisigMessage]:
    byte_message_decoded = bytes_messages.DecodedBytesMessage.from_hex_string(bytes_hexa)
    mistery_0 = byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=bytes_messages.NUMBER_OF_BITS_IN_BYTE)
    raw_command = byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=bytes_messages.NUMBER_OF_BITS_IN_BYTE)
    command_type = SdaUnisigMessage.CommandType(raw_command)

    safety_level = SafetyLevel[command_type.name[:3]]
    telegram_name = command_type.name[4:]

    ret: List[SdaUnisigMessage] = []

    if command_type == SdaUnisigMessage.CommandType.SL0_DISCONNECT_TELEGRAM or command_type == SdaUnisigMessage.CommandType.SL4_DISCONNECT_TELEGRAM:
        ret.append(
            SdaDisconnectTelegram(
                command_type=command_type,
                safety_level=safety_level,
                telegram_name=telegram_name,
                byte_message_decoded=byte_message_decoded,
                lowest_order_byte_sequence_number=mistery_0,
            )
        )

    elif command_type == SdaUnisigMessage.CommandType.SL0_IDLE_TELEGRAM or command_type == SdaUnisigMessage.CommandType.SL4_IDLE_TELEGRAM:
        ret.append(
            SdaGenericTelegram(
                command_type=command_type,
                safety_level=safety_level,
                telegram_name=telegram_name,
                byte_message_decoded=byte_message_decoded,
                lowest_order_byte_sequence_number=mistery_0,
            )
        )
    elif (
        command_type == SdaUnisigMessage.CommandType.SL0_CONNECT_REQUEST_TELEGRAM
        or command_type == SdaUnisigMessage.CommandType.SL4_CONNECT_REQUEST_TELEGRAM
        or command_type == SdaUnisigMessage.CommandType.SL0_CONNECT_CONFIRM_TELEGRAM
        or command_type == SdaUnisigMessage.CommandType.SL4_CONNECT_CONFIRM_TELEGRAM
    ):
        ret.append(
            SdaConnectRequestOrConfirmTelegram(
                command_type=command_type,
                safety_level=safety_level,
                telegram_name=telegram_name,
                byte_message_decoded=byte_message_decoded,
                lowest_order_byte_sequence_number=mistery_0,
            )
        )
    elif command_type == SdaUnisigMessage.CommandType.SL4_AUTHENTICATION_TELEGRAM or command_type == SdaUnisigMessage.CommandType.SL4_AUTHENTICATION_ACKNOWLEDGEMENT_TELEGRAM:
        ret.append(
            SdaConnectRequestOrConfirmTelegram(
                command_type=command_type,
                safety_level=safety_level,
                telegram_name=telegram_name,
                byte_message_decoded=byte_message_decoded,
                lowest_order_byte_sequence_number=mistery_0,
            )
        )
    elif (
        command_type == SdaUnisigMessage.CommandType.SL0_READY_TO_RUN
        or command_type == SdaUnisigMessage.CommandType.SL4_READY_TO_RUN
        or command_type == SdaUnisigMessage.CommandType.SL0_RUN
        or command_type == SdaUnisigMessage.CommandType.SL4_RUN
    ):
        ret.append(
            SdaRunOrReadyToRunTelegram(
                command_type=command_type,
                safety_level=safety_level,
                telegram_name=telegram_name,
                byte_message_decoded=byte_message_decoded,
                lowest_order_byte_sequence_number=mistery_0,
            )
        )
    elif command_type == SdaUnisigMessage.CommandType.SL0_TELEGRAM_FOR_UPPER_LAYER or command_type == SdaUnisigMessage.CommandType.SL4_TELEGRAM_FOR_UPPER_LAYER:
        mistery_1 = byte_message_decoded.get_next_byte_as_single_int_unsigned()
        raw_command_1 = byte_message_decoded.get_next_byte_as_single_int_unsigned()
        nid_stm = byte_message_decoded.get_next_byte_as_single_int_unsigned()
        l_packet = byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=13)

        nid_content_as_bit_str = byte_message_decoded.extract_next_bits_to_str_of_bit(number_of_bits=l_packet)

        stm_byte_message_decoded = bytes_messages.DecodedBytesMessage.from_bit_string(nid_content_as_bit_str)
        logger_config.print_and_log_info(f"STM found:{nid_stm}, packet length:{l_packet}")
        nid_stm_state_order = stm_byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=4)
        crc = stm_byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=SL4_CRC_SIZE_IN_BITES) if safety_level == SafetyLevel.SL4 else None
        assert stm_byte_message_decoded.is_correctly_and_completely_decoded()
        # remaining  =

        assert byte_message_decoded.is_correctly_and_completely_decoded()

        pass

    return ret
