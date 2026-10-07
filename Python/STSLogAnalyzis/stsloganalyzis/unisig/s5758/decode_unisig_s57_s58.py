import datetime
from abc import ABC
from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stsloganalyzis.ppn import ppn_profibus_log

from common import bytes_messages, date_time_formats
from logger import logger_config

from stsloganalyzis.unisig import additional_fields_decoder, upper_layer_libraries

SL4_CRC_SIZE_IN_BYTES = 6

SL0_CRC_SIZE_IN_BYTES = 0


STL_TIME_STAMP_SUBSET_56_LENGTH_IN_BYTES = 4
STL_TIME_STAMP_SUBSET_56_LENGTH_IN_BITS = STL_TIME_STAMP_SUBSET_56_LENGTH_IN_BYTES * bytes_messages.NUMBER_OF_BITS_IN_BYTE

MAXIMUM_PADDING_SIZE_IN_BITS_SUBSET_58 = 7

UPPER_LAYER_STM_NID_STM_FIELD_SIZE_IN_BYTES = 1
UPPER_LAYER_STM_NID_STM_FIELD_SIZE_IN_BITS = UPPER_LAYER_STM_NID_STM_FIELD_SIZE_IN_BYTES * bytes_messages.NUMBER_OF_BITS_IN_BYTE
UPPER_LAYER_STM_L_MESSAGE_FIELD_SIZE_IN_BITS = 13


def compute_crc_unisig_32(data: bytes, poly: int = 0x04C11DB7, init: int = 0xFFFFFFFF, xor_out: int = 0xFFFFFFFF) -> int:
    """
    Calcule le CRC 32 bits conforme aux spécifications types des couches UNISIG.
    Par défaut, utilise les paramètres standards (Non-réfléchi).
    """
    crc = init

    for byte in data:
        # Traitement bit à bit (MSB first pour UNISIG)
        crc ^= byte << 24
        for _ in range(8):
            if crc & 0x80000000:
                crc = ((crc << 1) ^ poly) & 0xFFFFFFFF
            else:
                crc = (crc << 1) & 0xFFFFFFFF

    return crc ^ xor_out


def compute_crc_unisig_64(data: bytes, poly: int = 0x6CE707E26B6F9977, init: int = 0xFFFFFFFFFFFFFFFF, xor_out: int = 0x0000000000000000) -> int:
    """
    Calcule le CRC 64 bits parfois requis par les structures de contrôle d'intégrité SLL.
    """
    crc = init
    mask_msb = 1 << 63
    mask_64 = (1 << 64) - 1

    for byte in data:
        crc ^= byte << 56
        for _ in range(8):
            if crc & mask_msb:
                crc = ((crc << 1) ^ poly) & mask_64
            else:
                crc = (crc << 1) & mask_64

    return crc ^ xor_out


class SafetyLevel(IntEnum):
    SL0 = 0
    SL4 = 4


@dataclass
class OnboardUnisigMessage(ABC):
    profibus_log_line: "ppn_profibus_log.ProfibusLogLine|None"
    byte_message_decoded: bytes_messages.DecodedBytesMessage

    def __post_init__(self) -> None:
        self.creational_and_decoding_errors: list[str] = []
        self.crc: UnisigCrc | None = None

    def add_error(self, error: str) -> None:
        self.creational_and_decoding_errors.append(error)


@dataclass
class SdnOnboardUnisigMessage(OnboardUnisigMessage):

    header: "SdnOnboardUnisigMessage.Header"

    class CommandTypeSubset56(IntEnum):
        SL4_SYNC_AND_REFERENCE_TIME = int("0xa1", 16)
        SL4_SAFE_TIME_LAYER_STARTUP = int("0xa4", 16)
        SL4_APPLICATION_DATA_MULTICAST_TELEGRAM_FOR_UPPER_LAYER = int("0x8d", 16)

    class Header:
        def __init__(self, byte_message_decoded: bytes_messages.DecodedBytesMessage) -> None:

            self.prefixX = byte_message_decoded.get_next_byte_as_single_int_unsigned()
            assert self.prefixX == 3
            self.prefixY = byte_message_decoded.get_next_byte_as_single_int_unsigned()
            assert self.prefixY == 0
            self.prefixZ = byte_message_decoded.get_next_byte_as_single_int_unsigned()
            assert self.prefixZ == 0
            self.command_number = byte_message_decoded.get_next_byte_as_single_int_unsigned()
            self.sequence_number = Unisig32BitsIntWithUnisigBytesOrder(byte_message_decoded)

        @property
        def command_type(self) -> "SdnOnboardUnisigMessage.CommandTypeSubset56":
            return SdnOnboardUnisigMessage.CommandTypeSubset56(self.command_number)

        @property
        def safety_level(self) -> SafetyLevel:
            return SafetyLevel[self.command_type.name[:3]]

        @property
        def telegram_name(self) -> str:
            return self.command_type.name[4:]

    @classmethod
    def decode_sdn_bytes_hexa(
        cls,
        profibus_log_line: "ppn_profibus_log.ProfibusLogLine",
        bytes_hexa: str,
        upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary,
    ) -> OnboardUnisigMessage | None:
        byte_message_decoded = bytes_messages.DecodedBytesMessage.from_hex_string(bytes_hexa)
        header = SdnOnboardUnisigMessage.Header(byte_message_decoded)

        if header.prefixX == int("0x03", 16) and header.prefixZ == 0 and header.prefixZ == 0:
            if header.command_type == SdnOnboardUnisigMessage.CommandTypeSubset56.SL4_SYNC_AND_REFERENCE_TIME:
                return SdnSyncAndReferenceTimeMulticastMessage(
                    profibus_log_line=profibus_log_line,
                    byte_message_decoded=byte_message_decoded,
                    header=header,
                )
            if header.command_type == SdnOnboardUnisigMessage.CommandTypeSubset56.SL4_SAFE_TIME_LAYER_STARTUP:
                return SdnSafeTimeLayerStartupForMulticast(
                    profibus_log_line=profibus_log_line,
                    byte_message_decoded=byte_message_decoded,
                    header=header,
                )

            if header.command_type == SdnOnboardUnisigMessage.CommandTypeSubset56.SL4_APPLICATION_DATA_MULTICAST_TELEGRAM_FOR_UPPER_LAYER:
                return SdnApplicationDataMulticastForUpperLayerTelegram(
                    profibus_log_line=profibus_log_line,
                    byte_message_decoded=byte_message_decoded,
                    header=header,
                )

            nid_stm = byte_message_decoded.get_next_byte_as_single_int_unsigned()
            l_message = byte_message_decoded.get_next_byte_as_single_int_unsigned()

        else:
            logger_config.print_and_log_warning(f"SDN: bad prefix {header.prefixX} {header.prefixY} {header.prefixZ}")

        return None


@dataclass
class SdnSafeTimeLayerStartupForMulticast(SdnOnboardUnisigMessage):

    def __post_init__(self) -> None:
        super().__post_init__()
        self.configuration_data_prefix_x = self.byte_message_decoded.get_next_byte_as_single_int_unsigned()
        assert self.configuration_data_prefix_x == 3
        self.configuration_data_prefix_y = self.byte_message_decoded.get_next_byte_as_single_int_unsigned()
        assert self.configuration_data_prefix_y == 0
        self.configuration_data_prefix_z = self.byte_message_decoded.get_next_byte_as_single_int_unsigned()
        assert self.configuration_data_prefix_z == 0
        self.sender_dynamic_transfer_time = UnisigTimeStamp.from_next_bytes_in_byte_message_decoded(self.byte_message_decoded)
        self.sender_static_transfer_time = UnisigTimeStamp.from_next_bytes_in_byte_message_decoded(self.byte_message_decoded)
        # self.timestamp = UnisigTimeStamp.from_last_bytes_in_byte_message_decoded(self.byte_message_decoded)
        self.remaining_undecoded_bits = self.byte_message_decoded.get_remaining_bits_as_str_of_bit()
        self.number_remaining_undecoded_bits = len(self.remaining_undecoded_bits)
        # assert self.byte_message_decoded.is_correctly_and_completely_decoded
        pass


@dataclass
class SdnApplicationDataMulticastForUpperLayerTelegram(SdnOnboardUnisigMessage):

    def __post_init__(self) -> None:
        super().__post_init__()
        self.remaining_undecoded_bits = self.byte_message_decoded.get_remaining_bits_as_str_of_bit()
        self.number_remaining_undecoded_bits = len(self.remaining_undecoded_bits)
        # assert self.byte_message_decoded.is_correctly_and_completely_decoded
        pass


@dataclass
class SdnSyncAndReferenceTimeMulticastMessage(SdnOnboardUnisigMessage):

    def __post_init__(self) -> None:
        super().__post_init__()
        self.configuration_data_prefix_x = self.byte_message_decoded.get_next_byte_as_single_int_unsigned()
        assert self.configuration_data_prefix_x == 3
        self.configuration_data_prefix_y = self.byte_message_decoded.get_next_byte_as_single_int_unsigned()
        assert self.configuration_data_prefix_y == 0
        self.configuration_data_prefix_z = self.byte_message_decoded.get_next_byte_as_single_int_unsigned()
        assert self.configuration_data_prefix_z == 0

        self.reference_sync_n = Unisig32BitsIntWithUnisigBytesOrder(self.byte_message_decoded).value_in_human_format

        self.reference_time_n_minus_1_utc = UnisigTimeStamp.from_next_bytes_in_byte_message_decoded(self.byte_message_decoded)

        self.crc = UnisigCrc(self.byte_message_decoded.get_and_remove_last_bytes_as_bitset_str(size_bytes=SL4_CRC_SIZE_IN_BYTES))
        assert self.byte_message_decoded.is_correctly_and_completely_decoded
        pass


@dataclass
class Unisig32BitsIntWithUnisigBytesOrder:

    def __init__(self, byte_message_decoded: bytes_messages.DecodedBytesMessage) -> None:

        low_word_low_byte = byte_message_decoded.get_next_byte_as_single_int_unsigned()
        low_word_high_byte = byte_message_decoded.get_next_byte_as_single_int_unsigned()
        high_word_low_byte = byte_message_decoded.get_next_byte_as_single_int_unsigned()
        high_word_high_byte = byte_message_decoded.get_next_byte_as_single_int_unsigned()

        self.value_in_human_format = bytes_messages.DecodedBytesMessage.from_bytes_as_list_int(
            [high_word_high_byte, high_word_low_byte, low_word_high_byte, low_word_low_byte]
        ).get_remaining_bits_as_unsigned_int()


@dataclass
class UnisigCrc:
    crc_bits_as_string: str

    def __post_init__(self) -> None:
        pass


@dataclass
class UnisigTimeStamp:

    in_ms: int

    def __post_init__(self) -> None:
        self.human_format = date_time_formats.format_duration_to_string(self.in_ms / 1000)

    @classmethod
    def from_next_bytes_in_byte_message_decoded(cls, byte_message_decoded: bytes_messages.DecodedBytesMessage) -> "UnisigTimeStamp":
        in_ms = Unisig32BitsIntWithUnisigBytesOrder(byte_message_decoded).value_in_human_format
        return UnisigTimeStamp(in_ms)

    @classmethod
    def from_last_bytes_in_byte_message_decoded(cls, byte_message_decoded: bytes_messages.DecodedBytesMessage) -> "UnisigTimeStamp":
        byte_message_extracted = bytes_messages.DecodedBytesMessage.from_bit_string(
            byte_message_decoded.extract_and_remove_last_next_bits_to_str_of_bit(number_of_bits=STL_TIME_STAMP_SUBSET_56_LENGTH_IN_BITS)
        )
        in_ms = Unisig32BitsIntWithUnisigBytesOrder(byte_message_extracted).value_in_human_format
        return UnisigTimeStamp(in_ms)


@dataclass
class OnboardSdaUnisigMessage(OnboardUnisigMessage):
    safety_level: SafetyLevel
    telegram_name: str
    command_type: "OnboardSdaUnisigMessage.CommandTypeSubset57"
    lowest_order_byte_sequence_number: int

    def __post_init__(self) -> None:
        super().__post_init__()
        self.stl_time_stamp: UnisigTimeStamp | None = None

    class Header:
        def __init__(self, byte_message_decoded: bytes_messages.DecodedBytesMessage) -> None:
            self.lowest_order_byte_sequence_number = byte_message_decoded.get_next_byte_as_single_int_unsigned()
            self.command_number = byte_message_decoded.get_next_byte_as_single_int_unsigned()

        @property
        def command_type(self) -> "OnboardSdaUnisigMessage.CommandTypeSubset57":
            return OnboardSdaUnisigMessage.CommandTypeSubset57(self.command_number)

        @property
        def safety_level(self) -> SafetyLevel:
            return SafetyLevel[self.command_type.name[:3]]

        @property
        def telegram_name(self) -> str:
            return self.command_type.name[4:]

    @classmethod
    def from_sda_hexa_bytes_str(
        cls,
        profibus_log_line: "ppn_profibus_log.ProfibusLogLine",
        bytes_hexa_str: str,
        upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary,
    ) -> OnboardUnisigMessage:
        byte_message_decoded = bytes_messages.DecodedBytesMessage.from_hex_string(bytes_hexa_str)
        sda_header = OnboardSdaUnisigMessage.Header(byte_message_decoded)

        if (
            sda_header.command_type == OnboardSdaUnisigMessage.CommandTypeSubset57.SL0_DISCONNECT_TELEGRAM
            or sda_header.command_type == OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_DISCONNECT_TELEGRAM
        ):
            return SdaDisconnectTelegram(
                profibus_log_line=profibus_log_line,
                command_type=sda_header.command_type,
                safety_level=sda_header.safety_level,
                telegram_name=sda_header.telegram_name,
                byte_message_decoded=byte_message_decoded,
                lowest_order_byte_sequence_number=sda_header.lowest_order_byte_sequence_number,
            )

        elif sda_header.command_type == OnboardSdaUnisigMessage.CommandTypeSubset57.SL0_IDLE_TELEGRAM or sda_header.command_type == OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_IDLE_TELEGRAM:
            return SdaIdleTelegram(
                profibus_log_line=profibus_log_line,
                command_type=sda_header.command_type,
                safety_level=sda_header.safety_level,
                telegram_name=sda_header.telegram_name,
                byte_message_decoded=byte_message_decoded,
                lowest_order_byte_sequence_number=sda_header.lowest_order_byte_sequence_number,
            )

        elif (
            sda_header.command_type == OnboardSdaUnisigMessage.CommandTypeSubset57.SL0_CONNECT_REQUEST_TELEGRAM
            or sda_header.command_type == OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_CONNECT_REQUEST_TELEGRAM
            or sda_header.command_type == OnboardSdaUnisigMessage.CommandTypeSubset57.SL0_CONNECT_CONFIRM_TELEGRAM
            or sda_header.command_type == OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_CONNECT_CONFIRM_TELEGRAM
        ):
            return SdaConnectRequestOrConfirmTelegram(
                profibus_log_line=profibus_log_line,
                command_type=sda_header.command_type,
                safety_level=sda_header.safety_level,
                telegram_name=sda_header.telegram_name,
                byte_message_decoded=byte_message_decoded,
                lowest_order_byte_sequence_number=sda_header.lowest_order_byte_sequence_number,
            )
        elif (
            sda_header.command_type == OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_AUTHENTICATION_TELEGRAM
            or sda_header.command_type == OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_AUTHENTICATION_ACKNOWLEDGEMENT_TELEGRAM
        ):
            return SdaAuthenticationOrAuthenticationAcknowledgementTelegram(
                profibus_log_line=profibus_log_line,
                command_type=sda_header.command_type,
                safety_level=sda_header.safety_level,
                telegram_name=sda_header.telegram_name,
                byte_message_decoded=byte_message_decoded,
                lowest_order_byte_sequence_number=sda_header.lowest_order_byte_sequence_number,
            )

        elif (
            sda_header.command_type == OnboardSdaUnisigMessage.CommandTypeSubset57.SL0_READY_TO_RUN
            or sda_header.command_type == OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_READY_TO_RUN
            or sda_header.command_type == OnboardSdaUnisigMessage.CommandTypeSubset57.SL0_RUN
            or sda_header.command_type == OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_RUN
        ):
            return SdaRunOrReadyToRunTelegram(
                profibus_log_line=profibus_log_line,
                command_type=sda_header.command_type,
                safety_level=sda_header.safety_level,
                telegram_name=sda_header.telegram_name,
                byte_message_decoded=byte_message_decoded,
                lowest_order_byte_sequence_number=sda_header.lowest_order_byte_sequence_number,
            )

        elif (
            sda_header.command_type == OnboardSdaUnisigMessage.CommandTypeSubset57.SL0_TELEGRAM_FOR_UPPER_LAYER
            or sda_header.command_type == OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_TELEGRAM_FOR_UPPER_LAYER
        ):
            return SdaForUpperLayerTelegram(
                profibus_log_line=profibus_log_line,
                safety_level=sda_header.safety_level,
                telegram_name=sda_header.telegram_name,
                byte_message_decoded=byte_message_decoded,
                lowest_order_byte_sequence_number=sda_header.lowest_order_byte_sequence_number,
                command_type=sda_header.command_type,
                upper_layer_decoding_library=upper_layer_decoding_library,
            )

        assert False

    class CommandTypeSubset57(IntEnum):  # index026_-_subset-057_v310.pdf
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
class SdaDisconnectTelegram(OnboardSdaUnisigMessage):

    def __post_init__(self) -> None:
        super().__post_init__()

        self.new_setup_desired = self.byte_message_decoded.get_next_bits_as_bool_0_or_1(size_bits=bytes_messages.NUMBER_OF_BITS_IN_BYTE)
        self.disconnect_reason_raw = self.byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=bytes_messages.NUMBER_OF_BITS_IN_BYTE)
        disconnect_reason_text_length_in_bits = self.byte_message_decoded.number_of_bits_remaining_to_decode
        self.disconnect_reason_text = self.byte_message_decoded.get_next_bits_as_ascii_char(number_of_chars=disconnect_reason_text_length_in_bits // bytes_messages.NUMBER_OF_BITS_IN_BYTE)


@dataclass
class SdaConnectRequestOrConfirmTelegram(OnboardSdaUnisigMessage):

    def __post_init__(self) -> None:
        super().__post_init__()
        self.random_number_representing_sequence_number = self.byte_message_decoded.get_next_bytes_as_single_int_unsigned(size_bytes=4)
        self.idle_cycle_timeout_in_100ms = self.byte_message_decoded.get_next_bytes_as_single_int_unsigned(size_bytes=2)
        self.configuration_data_prefix_x = self.byte_message_decoded.get_next_byte_as_single_int_unsigned()
        # assert self.configuration_data_prefix_x == 3
        self.configuration_data_prefix_y = self.byte_message_decoded.get_next_byte_as_single_int_unsigned()
        # assert self.configuration_data_prefix_y == 0
        self.configuration_data_prefix_z = self.byte_message_decoded.get_next_byte_as_single_int_unsigned()

        if self.safety_level == SafetyLevel.SL4:
            self.crc = UnisigCrc(self.byte_message_decoded.get_and_remove_last_bytes_as_bitset_str(size_bytes=SL4_CRC_SIZE_IN_BYTES))

        # assert self.configuration_data_prefix_z == 0
        dual_bus_length_in_bits = self.byte_message_decoded.number_of_bits_remaining_to_decode

        # if dual_bus_length_in_bits < 0:
        #    self.add_error(
        #        f"{self.telegram_name} {self.command_type} Invalid dual_bus_length_in_bits {dual_bus_length_in_bits}",
        #    )
        # else:

        self.dual_bus = (
            self.byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=dual_bus_length_in_bits)
            if self.byte_message_decoded.number_of_bits_remaining_to_decode >= dual_bus_length_in_bits
            else None
        )


@dataclass
class SdaAuthenticationOrAuthenticationAcknowledgementTelegram(OnboardSdaUnisigMessage):

    def __post_init__(self) -> None:
        super().__post_init__()
        self.authentication_number = self.byte_message_decoded.get_next_bytes_as_single_int_unsigned(size_bytes=4)
        if self.safety_level == SafetyLevel.SL4:
            self.crc = UnisigCrc(self.byte_message_decoded.extract_next_bytes_to_str_of_bit(size_bytes=SL4_CRC_SIZE_IN_BYTES))


@dataclass
class SdaRunOrReadyToRunTelegram(OnboardSdaUnisigMessage):

    def __post_init__(self) -> None:
        super().__post_init__()
        self.stl_time_stamp = UnisigTimeStamp.from_next_bytes_in_byte_message_decoded(self.byte_message_decoded)
        if self.safety_level == SafetyLevel.SL4:
            self.crc = UnisigCrc(self.byte_message_decoded.extract_next_bytes_to_str_of_bit(size_bytes=SL4_CRC_SIZE_IN_BYTES))


@dataclass
class SdaIdleTelegram(OnboardSdaUnisigMessage):

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.safety_level == SafetyLevel.SL4:
            self.crc = UnisigCrc(self.byte_message_decoded.extract_next_bytes_to_str_of_bit(size_bytes=SL4_CRC_SIZE_IN_BYTES))


@dataclass
class UpperLayerStm:
    upper_layer_telegram: "SdaForUpperLayerTelegram"
    byte_message_decoded: bytes_messages.DecodedBytesMessage

    def __post_init__(self) -> None:

        self.fields_names_and_values: dict[str, str | datetime.datetime | int | None] = {}

        self.nid_stm = self.byte_message_decoded.get_next_byte_as_single_int_unsigned()
        self.l_message = self.byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=UPPER_LAYER_STM_L_MESSAGE_FIELD_SIZE_IN_BITS)
        self.data_without_header_size_in_bits = self.l_message - UPPER_LAYER_STM_NID_STM_FIELD_SIZE_IN_BITS - UPPER_LAYER_STM_L_MESSAGE_FIELD_SIZE_IN_BITS

        self.creational_and_decoding_errors: list[str] = []
        if self.byte_message_decoded.number_of_bits_remaining_to_decode < self.data_without_header_size_in_bits:
            self.add_error(
                f"NotEnoughBitsToDecodeNidContent for STM {self.nid_stm} nid_content_length_in_bits={self.data_without_header_size_in_bits}, byte_message_number_of_remaining_bits_to_decode={self.byte_message_decoded.number_of_bits_remaining_to_decode}, upper_layer_already_decoded_stms_ids={','.join(str(stm.nid_stm) for stm in self.upper_layer_telegram.upper_layer_decoded_stms)}",
            )
            self.remaining_undecoded_bits = self.byte_message_decoded.get_remaining_bits_as_str_of_bit()

        else:
            nid_content_as_bit_str = self.byte_message_decoded.extract_next_bits_to_str_of_bit(number_of_bits=self.data_without_header_size_in_bits)
            self.stm_message_content_byte_message_decoded = bytes_messages.DecodedBytesMessage.from_bit_string(nid_content_as_bit_str)

            packets_definitions: list[upper_layer_libraries.PacketDefinition] = [
                packet_definition for packet_definition in self.upper_layer_telegram.upper_layer_decoding_library.packets_definitions if packet_definition.identifier == self.nid_stm
            ]
            if packets_definitions:
                assert len(packets_definitions) == 1
                packet_definition = packets_definitions[0]

                # logger_config.print_and_log_info(f"STM found:{upper_layer_decoded_stm.nid_stm}, packet length:{upper_layer_decoded_stm.l_message}", do_not_print=True)

                for field_definition in packet_definition.fields_or_variants:
                    self.handle_packet_field_or_variants_definition(field_definition)

                self.remaining_undecoded_bits = self.stm_message_content_byte_message_decoded.get_remaining_bits_as_str_of_bit()
                if self.number_remaining_undecoded_bits > 0:
                    self.add_error(
                        # f"RemainingBitsUndecodedAtEndStmMessage number_of_undecoded_bits={stm_byte_message_decoded.number_of_bits_remaining_to_decode}, undecoded_bits_as_str={stm_byte_message_decoded.extract_next_bits_to_str_of_bit(number_of_bits=stm_byte_message_decoded.number_of_bits_remaining_to_decode)}, upper_layer_already_decoded_stms_ids={','.join([str(stm.nid_stm) for stm in self.upper_layer_decoded_stms])}",
                        f"RemainingBitsUndecodedAtEndStmMessage at end of STM {self.nid_stm}. number_of_undecoded_bits={self.number_remaining_undecoded_bits}. remaining_undecoded_bits:{self.remaining_undecoded_bits}",
                    )
            else:
                self.add_error(
                    f"Unsupported STM {self.nid_stm}",
                )

    def get_field_int_value_or_assert(self, field_name: str) -> int:
        assert field_name in self.fields_names_and_values, f"STM {self.nid_stm}. Field {field_name} not found in {' ' .join(self.fields_names_and_values)}"
        raw_value = self.fields_names_and_values[field_name]
        assert raw_value is not None
        assert isinstance(raw_value, int)
        return raw_value

    def handle_variants_field(self, variants_definition: upper_layer_libraries.PacketVariantsDefinition, prefix: str = "") -> None:
        prefix_with_space = f"{prefix} " if prefix else ""

        if variants_definition.trigger_variable_name == "NID_EVENT":
            variant_trigger_value = self.stm_message_content_byte_message_decoded.get_next_byte_as_single_int_unsigned()
            self.add_field(field_name=prefix_with_space + "NID_EVENT", value=variant_trigger_value)
            l_event = self.stm_message_content_byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=10)
            self.add_field(field_name=prefix_with_space + "L_EVENT", value=l_event)
        else:
            variant_trigger_value = self.fields_names_and_values[variants_definition.trigger_variable_name]
        trigger_variable_name = variants_definition.trigger_variable_name

        variants_matching_trigger = [variant for variant in variants_definition.variants if variant.trigger_variable_value == variant_trigger_value]

        if variants_matching_trigger:

            if len(variants_matching_trigger) > 1 and variants_definition.trigger_variable_name == "NID_STMEVENT" and self.fields_names_and_values[variants_definition.trigger_variable_name] == 2:
                all_variants_definitions_with_same_field = [
                    variant
                    for variant in variants_matching_trigger
                    if isinstance(variant.fields_or_variants[0], upper_layer_libraries.PacketFieldDefinition)
                    and variant.fields_or_variants[0].name == "NID_STMPACKET"
                    and variant.fields_or_variants[0].size_in_bits is None
                ]
                if len(all_variants_definitions_with_same_field) == len(variants_matching_trigger):
                    assert isinstance(variants_matching_trigger[0].fields_or_variants[0], upper_layer_libraries.PacketFieldDefinition)
                    self.handle_packet_field(
                        field_definition=upper_layer_libraries.PacketFieldDefinition(
                            name=variants_matching_trigger[0].fields_or_variants[0].name,
                            size_in_bits=8,
                        ),
                        prefix=prefix,
                    )
                    stm_packet = self.get_field_int_value_or_assert("NID_STMPACKET")
                    variants_matching_trigger = [variant for variant in variants_definition.variants if variant.name == f"STM-{stm_packet}"]
                    # variants_matching_trigger[0].fields_or_variants[0].name,
                    pass

                pass

            assert len(variants_matching_trigger) == 1, f"STM {self.nid_stm}: too many {len(variants_matching_trigger)} variants match {trigger_variable_name}"
            # assert logger_config.print_and_log_error_if(
            #    len(variants_matching_trigger) > 1,
            #    f"STM {self.nid_stm}: too many {len(variants_matching_trigger)} variants match {trigger_variable_name}",
            # )
            variant_matching_trigger = variants_matching_trigger[0]
            self.add_field(f"Variant {trigger_variable_name} name", variant_matching_trigger.name)
            self.add_field(f"Variant {trigger_variable_name} alias", variant_matching_trigger.alias)
            for field_or_variants in variant_matching_trigger.fields_or_variants:
                self.handle_packet_field_or_variants_definition(
                    field_or_variants, prefix=f"{prefix_with_space}{variant_matching_trigger.name} {variant_matching_trigger.alias if variant_matching_trigger.alias else ''}"
                )

    def handle_packet_field(self, field_definition: upper_layer_libraries.PacketFieldDefinition, prefix: str = "") -> None:
        prefix_with_space = f"{prefix} " if prefix else ""

        decoded_field_name = field_definition.name
        decoded_field_size_in_bits = field_definition.size_in_bits

        if field_definition.fields_or_variants:
            if field_definition.name == "N_ITER":
                n_iter = self.stm_message_content_byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=field_definition.size_in_bits)
                self.add_field(prefix_with_space + field_definition.name, n_iter)

                if self.nid_stm == 161:
                    pass
                    # logger_config.print_and_log_debug(
                    #    f"Ignore fields {','.join([sub_field.name for sub_field in field_definition.fields_or_variants if isinstance(sub_field,upper_layer_libraries.PacketFieldDefinition)])} in STM {self.nid_stm} under {field_definition.name}"
                    # )
                else:
                    for i in range(n_iter):
                        for sub_field in field_definition.fields_or_variants:
                            assert isinstance(sub_field, upper_layer_libraries.PacketFieldDefinition)
                            self.handle_packet_field_or_variants_definition(
                                upper_layer_libraries.PacketFieldDefinition(
                                    name=f"{sub_field.name}",
                                    size_in_bits=sub_field.size_in_bits,
                                    enum_type_definition=sub_field.enum_type_definition,
                                    fields_or_variants=sub_field.fields_or_variants,
                                ),
                                prefix=f"{prefix_with_space}N_ITER_{i}_",
                            )
            elif field_definition.name.startswith(("L_TEXT", "L_CAPTION", "L_VALUE")):
                text_length = self.stm_message_content_byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=field_definition.size_in_bits)
                self.add_field(prefix_with_space + field_definition.name, text_length)
                for sub_field in field_definition.fields_or_variants:
                    assert isinstance(sub_field, upper_layer_libraries.PacketFieldDefinition)
                    assert sub_field.size_in_bits == bytes_messages.SIZE_BITS_PER_CHAR

                    if self.stm_message_content_byte_message_decoded.number_of_bits_remaining_to_decode < text_length * bytes_messages.NUMBER_OF_BITS_IN_BYTE:
                        self.add_error(
                            f"Not enough remaining bits {self.stm_message_content_byte_message_decoded.number_of_bits_remaining_to_decode} to decode text {sub_field.name} of {text_length} characters (requiring {text_length*bytes_messages.NUMBER_OF_BITS_IN_BYTE}) bits"
                        )
                        sub_field_string_value = "Not enough bits"
                    else:
                        sub_field_string_value = self.stm_message_content_byte_message_decoded.get_next_bits_as_ascii_char(number_of_chars=text_length)

                    self.add_field(prefix_with_space + sub_field.name, sub_field_string_value)

            else:

                for sub_field in field_definition.fields_or_variants:
                    self.handle_packet_field_or_variants_definition(
                        sub_field,
                        prefix=prefix,
                    )
        else:
            if decoded_field_size_in_bits is None:

                if decoded_field_name != "NID_STMPACKET":
                    self.add_error(f"STM {self.nid_stm} no size defined for field {decoded_field_name}")
                    self.add_field(decoded_field_name, "Error!!! No size defined")
                    self.add_field(prefix_with_space + decoded_field_name, "Error!!! No size defined")

            elif self.stm_message_content_byte_message_decoded.number_of_bits_remaining_to_decode >= decoded_field_size_in_bits:

                field_raw_unsigned_int_value = self.stm_message_content_byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=decoded_field_size_in_bits)

                if field_definition.enum_type_definition:
                    self.add_field(prefix_with_space + decoded_field_name, field_definition.enum_type_definition.states_ordered_by_value_from_zero[field_raw_unsigned_int_value])
                else:
                    self.add_field(prefix_with_space + decoded_field_name, field_raw_unsigned_int_value)
            else:
                self.add_error(
                    f"Not enough data for STM {self.nid_stm} {decoded_field_name}. {self.stm_message_content_byte_message_decoded.number_of_bits_remaining_to_decode} bits remaining, decoded_field_size_in_bits:{decoded_field_size_in_bits}"
                )
                self.add_field(prefix + decoded_field_name, "Error!!! No enough data")

    def handle_packet_field_or_variants_definition(
        self, field_or_variants_definition: upper_layer_libraries.PacketFieldDefinition | upper_layer_libraries.PacketVariantsDefinition, prefix: str = ""
    ) -> None:

        if isinstance(field_or_variants_definition, upper_layer_libraries.PacketFieldDefinition):
            self.handle_packet_field(field_or_variants_definition, prefix)
        elif isinstance(field_or_variants_definition, upper_layer_libraries.PacketVariantsDefinition):
            self.handle_variants_field(field_or_variants_definition, prefix)
        else:
            assert False

    def add_error(self, error: str) -> None:
        self.creational_and_decoding_errors.append(error)

    @property
    def number_remaining_undecoded_bits(self) -> int:
        return len(self.remaining_undecoded_bits)

    def add_field(self, field_name: str, value: str | datetime.datetime | int | None) -> None:
        assert field_name not in self.fields_names_and_values, f"{field_name} is already defined with value {self.fields_names_and_values[field_name]}. Cannot set value {value}"
        self.fields_names_and_values[field_name] = value
        additional_fields_decoder.manual_additional_fields_decoding(self, field_name)


@dataclass
class SdaForUpperLayerTelegram(OnboardSdaUnisigMessage):
    upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary

    def __post_init__(self) -> None:
        super().__post_init__()
        self.header = OnboardSdaUnisigMessage.Header(self.byte_message_decoded)

        self.stl_time_stamp = UnisigTimeStamp.from_last_bytes_in_byte_message_decoded(self.byte_message_decoded)

        if self.safety_level == SafetyLevel.SL4:
            self.crc = UnisigCrc(self.byte_message_decoded.get_and_remove_last_bytes_as_bitset_str(size_bytes=SL4_CRC_SIZE_IN_BYTES))

        self.upper_layer_decoded_stms: list[UpperLayerStm] = []

        while self.byte_message_decoded.number_of_bits_remaining_to_decode > MAXIMUM_PADDING_SIZE_IN_BITS_SUBSET_58:

            if self.byte_message_decoded.number_of_bits_remaining_to_decode >= UPPER_LAYER_STM_NID_STM_FIELD_SIZE_IN_BITS + UPPER_LAYER_STM_L_MESSAGE_FIELD_SIZE_IN_BITS:
                upper_layer_decoded_stm = UpperLayerStm(self, byte_message_decoded=self.byte_message_decoded)
                self.upper_layer_decoded_stms.append(upper_layer_decoded_stm)
                assert len(self.upper_layer_decoded_stms) < 100
            else:
                self.add_error(
                    f"NotEnoughBitsToDecodeUpperLayerStm nid_content_length_in_bits={upper_layer_decoded_stm.data_without_header_size_in_bits}, byte_message_number_of_remaining_bits_to_decode={self.byte_message_decoded.number_of_bits_remaining_to_decode}, upper_layer_already_decoded_stms_ids={','.join([str(stm.nid_stm) for stm in self.upper_layer_decoded_stms])}",
                )
                break

        self.padding = (
            self.byte_message_decoded.get_next_bits_as_single_int_unsigned(self.byte_message_decoded.number_of_bits_remaining_to_decode)
            if self.byte_message_decoded.number_of_bits_remaining_to_decode > 0 and self.byte_message_decoded.number_of_bits_remaining_to_decode < 8
            else None if self.byte_message_decoded.number_of_bits_remaining_to_decode == 0 else f"Error, too many bits ({self.byte_message_decoded.number_of_bits_remaining_to_decode}) for padding"
        )

        self.remaining_undecoded_bits = self.byte_message_decoded.get_remaining_bits_as_str_of_bit()
        self.number_remaining_undecoded_bits = len(self.remaining_undecoded_bits)

        if self.number_remaining_undecoded_bits >= 8:
            self.add_error(
                # f"RemainingBitsUndecodedAtEndOfSdaDelegate number_of_undecoded_bits={self.byte_message_decoded.number_of_bits_remaining_to_decode}, undecoded_bits_as_str={self.byte_message_decoded.extract_next_bits_to_str_of_bit(number_of_bits=self.byte_message_decoded.number_of_bits_remaining_to_decode)}, upper_layer_already_decoded_stms_ids={','.join([str(stm.nid_stm) for stm in self.upper_layer_decoded_stms])}",
                f"RemainingBitsUndecodedAtEndOfSdaDelegate number_of_undecoded_bits={self.number_remaining_undecoded_bits}, upper_layer_already_decoded_stms_ids={','.join([str(stm.nid_stm) for stm in self.upper_layer_decoded_stms])}",
            )
