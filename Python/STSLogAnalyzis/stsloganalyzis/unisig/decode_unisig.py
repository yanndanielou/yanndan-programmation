import binascii
import re
from abc import ABC
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum, IntEnum, auto
from typing import Optional, cast, List, Dict

from common import bytes_messages
from dateutil import parser

from stsloganalyzis.unisig import upper_layer_libraries

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
    class CommandType(IntEnum):
        SL4_SYNC_AND_REFERENCE_TIME = int("0xa1", 16)
        SL4_SAFE_TIME_LAYER_STARTUP = int("0xa4", 16)
        SL4_MULTICAST_TELEGRAM_FOR_UPPER_LAYER = int("0x8d", 16)

    @classmethod
    def decode_sdn_bytes_hexa(cls, bytes_hexa: str, upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary) -> List[UnisigMessage]:
        byte_message_decoded = bytes_messages.DecodedBytesMessage.from_hex_string(bytes_hexa)
        prefixX = byte_message_decoded.get_next_byte_as_single_int_unsigned()
        prefixY = byte_message_decoded.get_next_byte_as_single_int_unsigned()
        prefixZ = byte_message_decoded.get_next_byte_as_single_int_unsigned()
        command = byte_message_decoded.get_next_byte_as_single_int_unsigned()
        sequenceNumber = byte_message_decoded.get_next_bytes_as_single_int_unsigned(size_bytes=4)
        nid_stm = byte_message_decoded.get_next_byte_as_single_int_unsigned()
        l_message = byte_message_decoded.get_next_byte_as_single_int_unsigned()

        if prefixX == int("0x03", 16) and prefixZ == 0 and prefixZ == 0:
            pass

        return []


@dataclass
class SdaUnisigMessage(UnisigMessage):
    safety_level: SafetyLevel
    telegram_name: str
    byte_message_decoded: bytes_messages.DecodedBytesMessage
    lowest_order_byte_sequence_number: int
    command_type: "SdaUnisigMessage.CommandType"

    @classmethod
    def from_sda_hexa_bytes_str(cls, bytes_hexa: str, upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary) -> List[UnisigMessage]:
        byte_message_decoded = bytes_messages.DecodedBytesMessage.from_hex_string(bytes_hexa)
        mistery_0 = byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=bytes_messages.NUMBER_OF_BITS_IN_BYTE)
        raw_command_number = byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=bytes_messages.NUMBER_OF_BITS_IN_BYTE)
        command_type = SdaUnisigMessage.CommandType(raw_command_number)

        safety_level = SafetyLevel[command_type.name[:3]]
        telegram_name = command_type.name[4:]

        ret: List[UnisigMessage] = []

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
            ret.append(
                UpperLayerTelegram(
                    safety_level=safety_level,
                    telegram_name=telegram_name,
                    byte_message_decoded=byte_message_decoded,
                    lowest_order_byte_sequence_number=mistery_0,
                    command_type=command_type,
                    upper_layer_decoding_library=upper_layer_decoding_library,
                )
            )
            pass

        return ret

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
class UpperLayerStm:
    fields_names_and_values: Dict[str, str | int]
    bit_message_decoded: bytes_messages.DecodedBytesMessage
    size_in_bits: int


@dataclass
class UpperLayerTelegram(SdaUnisigMessage):
    upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary

    def __post_init__(self) -> None:
        self.stl_time_stamp_ms = self.byte_message_decoded.get_next_bytes_as_single_int_unsigned(size_bytes=4)

        mistery_1 = self.byte_message_decoded.get_next_byte_as_single_int_unsigned()
        raw_command_1 = self.byte_message_decoded.get_next_byte_as_single_int_unsigned()
        nid_stm = self.byte_message_decoded.get_next_byte_as_single_int_unsigned()
        l_packet = self.byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=13)

        self.upper_layer_decoded_stm: List[UpperLayerStm] = []
        packets_definitions = [packet_definition for packet_definition in self.upper_layer_decoding_library.packets_definitions if packet_definition.identifier == nid_stm]
        if packets_definitions:

            packet_definition = packets_definitions[0]
            nid_content_as_bit_str = self.byte_message_decoded.extract_next_bits_to_str_of_bit(number_of_bits=l_packet)
            stm_byte_message_decoded = bytes_messages.DecodedBytesMessage.from_bit_string(nid_content_as_bit_str)
            logger_config.print_and_log_info(f"STM found:{nid_stm}, packet length:{l_packet}")

            fields_names_and_values: Dict[str, str | int] = {}
            for field_definition in packet_definition.fields:
                decoded_field_name = field_definition.name
                decoded_field_size_in_bits = field_definition.size_in_bits

                field_raw_unsigned_int_value = stm_byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=decoded_field_size_in_bits)

                if field_definition.enum_type_definition:
                    fields_names_and_values[decoded_field_name] = field_definition.enum_type_definition.states_ordered_by_value_from_zero[field_raw_unsigned_int_value]

                else:
                    fields_names_and_values[decoded_field_name] = field_raw_unsigned_int_value

            self.upper_layer_decoded_stm.append(
                UpperLayerStm(
                    fields_names_and_values=fields_names_and_values,
                    bit_message_decoded=stm_byte_message_decoded,
                    size_in_bits=decoded_field_size_in_bits,
                )
            )

            crc = stm_byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=SL4_CRC_SIZE_IN_BITES) if self.safety_level == SafetyLevel.SL4 else None
            assert stm_byte_message_decoded.is_correctly_and_completely_decoded()
            # remaining  =


@dataclass
class SdaGenericTelegram(SdaUnisigMessage):

    def __post_init__(self) -> None:
        self.crc = self.byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=self.crc_size_in_bits) if self.crc_size_in_bits > 0 else None
