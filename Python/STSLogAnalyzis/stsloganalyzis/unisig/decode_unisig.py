import binascii
from enum import Enum, IntEnum
import re
from abc import ABC
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional, Tuple, Union

from common import bytes_messages
from dateutil import parser


class UnisigMessage(ABC):
    pass


class SdnUnisigMessage(UnisigMessage):
    pass

    @staticmethod
    def decode_bytes_hexa(bytes_hexa: str) -> "SdnUnisigMessage":
        pass


class SdaUnisigMessage(UnisigMessage):
    pass

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

    @staticmethod
    def decode_bytes_hexa(bytes_hexa: str) -> "SdaUnisigMessage":
        byte_message_decoded = bytes_messages.DecodedBytesMessage(bytes_hexa)
        mistery_0 = byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=8)
        raw_command = byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=8)
        command_type = SdaUnisigMessage.CommandType(int("0x85", 16))
        return None
