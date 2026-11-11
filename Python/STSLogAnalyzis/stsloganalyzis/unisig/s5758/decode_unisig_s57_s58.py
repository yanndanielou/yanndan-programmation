import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stsloganalyzis.ppn import ppn_profibus_log

from common import bytes_messages, bytes_utils, date_time_formats
from logger import logger_config

from stsloganalyzis.unisig import upper_layer_libraries
from stsloganalyzis.unisig.s5758 import additional_fields_decoder_s5758

SL4_CRC_SIZE_IN_BYTES = 6

SL0_CRC_SIZE_IN_BYTES = 0


STL_TIME_STAMP_SUBSET_56_LENGTH_IN_BYTES = 4
STL_TIME_STAMP_SUBSET_56_LENGTH_IN_BITS = STL_TIME_STAMP_SUBSET_56_LENGTH_IN_BYTES * bytes_messages.NUMBER_OF_BITS_IN_BYTE

MAXIMUM_PADDING_SIZE_IN_BITS_SUBSET_58 = 7

UPPER_LAYER_STM_NID_STM_FIELD_SIZE_IN_BYTES = 1
UPPER_LAYER_STM_NID_STM_FIELD_SIZE_IN_BITS = UPPER_LAYER_STM_NID_STM_FIELD_SIZE_IN_BYTES * bytes_messages.NUMBER_OF_BITS_IN_BYTE
UPPER_LAYER_STM_L_MESSAGE_FIELD_SIZE_IN_BITS = 13


def crc48_unisig_s57_as_bytes(data: bytes | bytearray, verbose: bool = False) -> bytes:
    as_int = crc48_unisig_s57_as_int(data, verbose)
    return as_int.to_bytes(length=6)


def crc48_unisig_s57_as_int(data: bytes | bytearray, verbose: bool = False) -> int:
    """Calcule un CRC-4

    Paramètres:
        data : Les données d'entrée sous forme de bytes ou bytearray.
        debug : Si True, affiche les étapes intermédiaires (équivalent aux
          couts).

    Retourne:
        int : La valeur du CRC sur 48 bits.
    """
    POLY: int = 0x0000D28DB3FA4AAD
    MASK: int = 0x0000FFFFFFFFFFFF

    crc: int = 0

    if verbose:
        print(f"crc_init={crc}")

    for i, byte in enumerate(data):
        # Aligner l'octet sur le MSB (bit 40 de l'espace 48-bit avant décalage/traitement)
        crc ^= (byte & 0xFF) << 40

        if verbose:
            print(f"data[{i}]={byte}")
            print(f"crc_temp_pre={crc}")

        for bit in range(8):
            if crc & 0x0000800000000000:  # Test du bit 47
                if verbose:
                    print(f"crc_temp0(bit{bit})={crc}")
                crc = (crc << 1) ^ POLY
            else:
                crc <<= 1

            crc &= MASK  # Forcer à 48 bits
            if verbose:
                print(f"crc_temp(bit{bit})={crc}")

        if verbose:
            print(f"crc_temp_new={crc}")

    return crc


class SafetyLevel(IntEnum):
    SL0 = 0
    SL4 = 4


@dataclass
class OnboardUnisigMessage(ABC):
    profibus_log_line: "ppn_profibus_log.ProfibusLogLine|None"
    byte_message_decoded: bytes_messages.DecodedBytesMessage
    ppn_connections_library: "ppn_profibus_log.PpnConnectionsLibrary"

    def __post_init__(self) -> None:
        self.creational_and_decoding_errors: list[str] = []
        self.crc: UnisigCrc | None = None
        self.recomputed_crc: RecomputedUnisigCrc | None = None
        self.recomputed_crc_and_transmitted_crc_are_equals: bool | None = None
        self.recomputed_crc_as_string_base_16: str | None = None
        self.sequence_number_is_continuous_with_previous: bool | None = None
        self.current_connection_session_before_this_message = (
            self.ppn_connections_library.get_existing_current_connection_by_profibus_log_line(self.profibus_log_line) if self.profibus_log_line else None
        )
        self.transmitter_interlocutor = (
            self.current_connection_session_before_this_message.get_interlocutor_by_address(self.profibus_log_line.source_address)
            if self.current_connection_session_before_this_message and self.profibus_log_line
            else None
        )

        logger_config.print_and_log_error_if(
            self.current_connection_session_before_this_message is not None and self.transmitter_interlocutor is None, f"No transmitter but connection session for {self}"
        )

    def add_error(self, error: str) -> None:
        self.creational_and_decoding_errors.append(error)

    def recompute_crc_from_data_as_bytes_except_length(
        self,
        implicit_data_except_length: "UnisigCrc.ImplicitDataExceptLength",
        telegram_header: "UnisigCrc.TelegramHeaderForDataTransmissionWithErrorDetection",
        net_data: "OnboardSdaUnisigMessage.NetData | None" = None,
    ) -> None:

        self.recomputed_crc = RecomputedUnisigCrc.compute_from_data(implicit_data_except_length, telegram_header, net_data)

        self.recomputed_crc_as_string_base_16 = self.recomputed_crc.as_base_16_str

        if self.crc:
            compare_as_byte_array = self.recomputed_crc.as_bytearray == self.crc.as_bytearray
            self.recomputed_crc_and_transmitted_crc_are_equals = compare_as_byte_array
            assert self.profibus_log_line
            logger_config.print_and_log_error_if(
                not self.recomputed_crc_and_transmitted_crc_are_equals,
                f"{self} : transmitted CRC is incorrect ({self.profibus_log_line.file_path}:{self.profibus_log_line.line_number}) {self.profibus_log_line.interlocutors_with_translation}. Is {self.crc.as_base_16_str}, should be {self.recomputed_crc_as_string_base_16}",
            )

    @abstractmethod
    def get_crc_implicit_data_except_length(self) -> "UnisigCrc.ImplicitDataExceptLength":
        pass

    @abstractmethod
    def can_src_be_computed(self) -> bool:
        pass

    @abstractmethod
    def prepare_data_and_recompute_crc(self) -> None:
        pass


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

    def get_crc_implicit_data_except_length(self) -> "UnisigCrc.ImplicitDataExceptLength":
        raise NotImplementedError()

    @classmethod
    def decode_sdn_bytes_hexa(
        cls,
        profibus_log_line: "ppn_profibus_log.ProfibusLogLine",
        bytes_hexa: str,
        upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary,
        ppn_connections_library: "ppn_profibus_log.PpnConnectionsLibrary",
    ) -> OnboardUnisigMessage | None:
        byte_message_decoded = bytes_messages.DecodedBytesMessage.from_hex_string(bytes_hexa)
        header = SdnOnboardUnisigMessage.Header(byte_message_decoded)

        if header.prefixX == int("0x03", 16) and header.prefixZ == 0 and header.prefixZ == 0:
            if header.command_type == SdnOnboardUnisigMessage.CommandTypeSubset56.SL4_SYNC_AND_REFERENCE_TIME:
                return SdnSyncAndReferenceTimeMulticastMessage(
                    ppn_connections_library=ppn_connections_library,
                    profibus_log_line=profibus_log_line,
                    byte_message_decoded=byte_message_decoded,
                    header=header,
                )
            if header.command_type == SdnOnboardUnisigMessage.CommandTypeSubset56.SL4_SAFE_TIME_LAYER_STARTUP:
                return SdnSafeTimeLayerStartupForMulticast(
                    ppn_connections_library=ppn_connections_library,
                    profibus_log_line=profibus_log_line,
                    byte_message_decoded=byte_message_decoded,
                    header=header,
                )

            if header.command_type == SdnOnboardUnisigMessage.CommandTypeSubset56.SL4_APPLICATION_DATA_MULTICAST_TELEGRAM_FOR_UPPER_LAYER:
                return SdnApplicationDataMulticastForUpperLayerTelegram(
                    ppn_connections_library=ppn_connections_library,
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

    def can_src_be_computed(self) -> bool:
        raise NotImplementedError()

    def prepare_data_and_recompute_crc(self) -> None:
        raise NotImplementedError()


@dataclass
class SdnApplicationDataMulticastForUpperLayerTelegram(SdnOnboardUnisigMessage):

    def __post_init__(self) -> None:
        super().__post_init__()
        self.remaining_undecoded_bits = self.byte_message_decoded.get_remaining_bits_as_str_of_bit()
        self.number_remaining_undecoded_bits = len(self.remaining_undecoded_bits)
        # assert self.byte_message_decoded.is_correctly_and_completely_decoded
        pass

    def can_src_be_computed(self) -> bool:
        raise NotImplementedError()

    def prepare_data_and_recompute_crc(self) -> None:
        raise NotImplementedError()


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

        self.reference_sync_n = Unisig32BitsIntWithUnisigBytesOrder(self.byte_message_decoded)

        self.reference_time_n_minus_1_utc = UnisigTimeStamp.from_next_bytes_in_byte_message_decoded(self.byte_message_decoded)

        self.crc = UnisigCrc.from_bits_as_string(self.byte_message_decoded.get_and_remove_last_bytes_as_bitset_str(size_bytes=SL4_CRC_SIZE_IN_BYTES))
        assert self.byte_message_decoded.is_correctly_and_completely_decoded
        pass

    def can_src_be_computed(self) -> bool:
        raise NotImplementedError()

    def prepare_data_and_recompute_crc(self) -> None:
        raise NotImplementedError()


@dataclass
class Unisig32BitsIntWithUnisigBytesOrder:

    def __init__(self, byte_message_decoded: bytes_messages.DecodedBytesMessage) -> None:

        low_word_low_byte = byte_message_decoded.get_next_byte_as_single_int_unsigned()
        low_word_high_byte = byte_message_decoded.get_next_byte_as_single_int_unsigned()
        high_word_low_byte = byte_message_decoded.get_next_byte_as_single_int_unsigned()
        high_word_high_byte = byte_message_decoded.get_next_byte_as_single_int_unsigned()

        self.value_as_int = bytes_messages.DecodedBytesMessage.from_bytes_as_list_int(
            [high_word_high_byte, high_word_low_byte, low_word_high_byte, low_word_low_byte]
        ).get_remaining_bits_as_unsigned_int()

        self.value_as_byte_table_ordered_in_unisig_way = [low_word_low_byte, low_word_high_byte, high_word_low_byte, high_word_high_byte]
        self.value_as_bytes_ordered_in_unisig_way = bytes(self.value_as_byte_table_ordered_in_unisig_way)


@dataclass
class Unisig16BitsIntWithUnisigBytesOrder:

    def __init__(self, byte_message_decoded: bytes_messages.DecodedBytesMessage) -> None:

        self.low_byte = byte_message_decoded.get_next_byte_as_single_int_unsigned()
        self.high_byte = byte_message_decoded.get_next_byte_as_single_int_unsigned()

        self.value_in_decimal_format = bytes_messages.DecodedBytesMessage.from_bytes_as_list_int([self.high_byte, self.low_byte]).get_remaining_bits_as_unsigned_int()


@dataclass
class UnisigCrc:
    as_int: int

    def __post_init__(self) -> None:
        self.as_bytes = self.as_int.to_bytes(6, byteorder="big")
        self.as_bytearray = bytearray(self.as_bytes)
        self.as_base_16_str = bytes_utils.byte_array_to_string_base_16(self.as_bytearray)
        self.as_base_10_str = bytes_utils.byte_array_to_string_base_10(self.as_bytearray)

    @classmethod
    def from_bits_as_string(cls, bits_as_string: str) -> "UnisigCrc":
        assert len(bits_as_string) == 48
        as_int = bytes_messages.DecodedBytesMessage.from_bit_string(bits_as_string).get_remaining_bits_as_unsigned_int()
        return UnisigCrc(as_int)

    @dataclass
    class ImplicitDataExceptLength:
        receiver_address: int
        sender_address: int
        dsap: int
        ssap: int
        higher_order_24bits_of_sequence_number_byte_1: int
        higher_order_24bits_of_sequence_number_byte_2: int
        higher_order_24bits_of_sequence_number_byte_3: int

        def __post_init__(self) -> None:
            self.all_bytes = (
                self.receiver_address.to_bytes()
                + self.sender_address.to_bytes()
                + self.dsap.to_bytes()
                + self.ssap.to_bytes()
                + self.higher_order_24bits_of_sequence_number_byte_1.to_bytes()
                + self.higher_order_24bits_of_sequence_number_byte_2.to_bytes()
                + self.higher_order_24bits_of_sequence_number_byte_3.to_bytes()
            )
            self.all_bytes_as_base_16 = bytes_utils.byte_array_to_string_base_16(self.all_bytes)

        @classmethod
        def from_profibus_log_line(
            cls,
            profibus_log_line: "ppn_profibus_log.ProfibusLogLine",
            higher_order_24bits_of_sequence_number_byte_1: int,
            higher_order_24bits_of_sequence_number_byte_2: int,
            higher_order_24bits_of_sequence_number_byte_3: int,
        ) -> "UnisigCrc.ImplicitDataExceptLength":
            return UnisigCrc.ImplicitDataExceptLength(
                receiver_address=profibus_log_line.target_address,  # Receiver_address / Receive_address (implicit)
                sender_address=profibus_log_line.source_address,  # Receiver_address / Receive_address (implicit)
                dsap=profibus_log_line.target_sap,
                ssap=profibus_log_line.source_sap,
                higher_order_24bits_of_sequence_number_byte_1=higher_order_24bits_of_sequence_number_byte_1,
                higher_order_24bits_of_sequence_number_byte_2=higher_order_24bits_of_sequence_number_byte_2,
                higher_order_24bits_of_sequence_number_byte_3=higher_order_24bits_of_sequence_number_byte_3,
            )

    @dataclass
    class TelegramHeaderForDataTransmissionWithErrorDetection:  # stelegram header for data transmission with error detection
        lowest_order_byte_of_sequence_number_least_significant_data_lsd: int  # (least significant data, LSD)
        command_number: int

        def __post_init__(self) -> None:
            self.all_bytes = self.lowest_order_byte_of_sequence_number_least_significant_data_lsd.to_bytes() + self.command_number.to_bytes()
            self.all_bytes_as_base_16 = bytes_utils.byte_array_to_string_base_16(self.all_bytes)
            pass


@dataclass
class RecomputedUnisigCrc(UnisigCrc):
    implicit_data_bytes: bytes
    implicit_data_except_length: UnisigCrc.ImplicitDataExceptLength
    telegram_header: UnisigCrc.TelegramHeaderForDataTransmissionWithErrorDetection
    implicit_data_length_field_as_int: int
    net_data: "OnboardSdaUnisigMessage.NetData | None"
    all_data_for_checksum_computation_bytes: bytes
    all_data_for_checksum_computation_base_16: str

    def __post_init__(self) -> None:
        super().__post_init__()
        self.explanations_for_debug = f"All data for checksum computation:{self.all_data_for_checksum_computation_base_16}, implicit data:{bytes_utils.byte_array_to_string_base_16(self.implicit_data_bytes)}, header:{self.telegram_header.all_bytes_as_base_16}, net_data:{self.net_data.as_base_16 if self.net_data else 'NA'}"

    @classmethod
    def compute_from_data(
        cls,
        implicit_data_except_length: "UnisigCrc.ImplicitDataExceptLength",
        telegram_header: "UnisigCrc.TelegramHeaderForDataTransmissionWithErrorDetection",
        net_data: "OnboardSdaUnisigMessage.NetData | None" = None,
    ) -> "RecomputedUnisigCrc":
        net_data_length = net_data.length_in_bytes if net_data else 0

        implicit_data_length_int = net_data_length + len(telegram_header.all_bytes) + SL4_CRC_SIZE_IN_BYTES
        implicit_data_length_bytes = implicit_data_length_int.to_bytes()

        implicit_data_bytes = implicit_data_length_bytes + implicit_data_except_length.all_bytes

        data_for_checksum_bytes = implicit_data_bytes + telegram_header.all_bytes
        if net_data:
            data_for_checksum_bytes += net_data.as_bytes
        as_int = crc48_unisig_s57_as_int(data=data_for_checksum_bytes)
        return RecomputedUnisigCrc(
            as_int=as_int,
            implicit_data_bytes=implicit_data_bytes,
            implicit_data_except_length=implicit_data_except_length,
            telegram_header=telegram_header,
            net_data=net_data,
            all_data_for_checksum_computation_bytes=data_for_checksum_bytes,
            all_data_for_checksum_computation_base_16=bytes_utils.byte_array_to_string_base_16(data_for_checksum_bytes),
            implicit_data_length_field_as_int=implicit_data_length_int,
        )


@dataclass
class UnisigTimeStamp:

    as_unisig_32_bits: Unisig32BitsIntWithUnisigBytesOrder

    def __post_init__(self) -> None:
        self.in_ms = self.as_unisig_32_bits.value_as_int
        self.human_format = date_time_formats.format_duration_to_string(self.in_ms / 1000)

    @classmethod
    def from_next_bytes_in_byte_message_decoded(cls, byte_message_decoded: bytes_messages.DecodedBytesMessage) -> "UnisigTimeStamp":
        return UnisigTimeStamp(Unisig32BitsIntWithUnisigBytesOrder(byte_message_decoded))

    @classmethod
    def from_last_bytes_in_byte_message_decoded(cls, byte_message_decoded: bytes_messages.DecodedBytesMessage) -> "UnisigTimeStamp":
        byte_message_extracted = bytes_messages.DecodedBytesMessage.from_bit_string(
            byte_message_decoded.extract_and_remove_last_next_bits_to_str_of_bit(number_of_bits=STL_TIME_STAMP_SUBSET_56_LENGTH_IN_BITS)
        )
        return UnisigTimeStamp(Unisig32BitsIntWithUnisigBytesOrder(byte_message_extracted))


@dataclass
class OnboardSdaUnisigMessage(OnboardUnisigMessage):
    safety_level: SafetyLevel
    telegram_name: str
    command_type: "OnboardSdaUnisigMessage.CommandTypeSubset57"
    lowest_order_byte_sequence_number: int

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.command_type} {self.profibus_log_line}"

    def __post_init__(self) -> None:
        super().__post_init__()
        self.stl_time_stamp: UnisigTimeStamp | None = None
        self.all_data_aka_net_data: OnboardSdaUnisigMessage.NetData | None = None

        if self.transmitter_interlocutor:
            sequence_error = self.transmitter_interlocutor.update_lowest_order_byte_sequence_number(self.lowest_order_byte_sequence_number)
            self.sequence_number_is_continuous_with_previous = sequence_error is None
            logger_config.print_and_log_error_if(sequence_error, f"{self} {sequence_error}")

        self.random_number_representing_sequence_number_byte_2_of_4_for_crc = (
            self.transmitter_interlocutor.random_number_representing_sequence_number_byte_2_of_4 if self.transmitter_interlocutor else None
        )
        self.random_number_representing_sequence_number_byte_3_of_4_for_crc = (
            self.transmitter_interlocutor.random_number_representing_sequence_number_byte_3_of_4 if self.transmitter_interlocutor else None
        )
        self.random_number_representing_sequence_number_byte_4_of_4_for_crc = (
            self.transmitter_interlocutor.random_number_representing_sequence_number_byte_4_of_4 if self.transmitter_interlocutor else None
        )

    def get_crc_telegram_header(self) -> "UnisigCrc.TelegramHeaderForDataTransmissionWithErrorDetection":

        header = UnisigCrc.TelegramHeaderForDataTransmissionWithErrorDetection(
            lowest_order_byte_of_sequence_number_least_significant_data_lsd=self.lowest_order_byte_sequence_number, command_number=self.command_type.value
        )
        return header

    def prepare_data_and_recompute_crc(self) -> None:
        assert self.profibus_log_line

        implicit_data_except_length = self.get_crc_implicit_data_except_length()
        header = self.get_crc_telegram_header()
        self.recompute_crc_from_data_as_bytes_except_length(implicit_data_except_length, header, self.all_data_aka_net_data)

    def get_crc_implicit_data_except_length(self) -> "UnisigCrc.ImplicitDataExceptLength":
        assert self.profibus_log_line
        assert self.random_number_representing_sequence_number_byte_2_of_4_for_crc is not None
        assert self.random_number_representing_sequence_number_byte_3_of_4_for_crc is not None
        assert self.random_number_representing_sequence_number_byte_4_of_4_for_crc is not None

        implicit_data = UnisigCrc.ImplicitDataExceptLength.from_profibus_log_line(
            profibus_log_line=self.profibus_log_line,
            higher_order_24bits_of_sequence_number_byte_1=self.random_number_representing_sequence_number_byte_2_of_4_for_crc,
            higher_order_24bits_of_sequence_number_byte_2=self.random_number_representing_sequence_number_byte_3_of_4_for_crc,
            higher_order_24bits_of_sequence_number_byte_3=self.random_number_representing_sequence_number_byte_4_of_4_for_crc,
        )
        return implicit_data

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

    @dataclass
    class NetData:
        length_in_bits: int
        as_bytes: bytes

        def __post_init__(self) -> None:
            assert self.length_in_bits % 8 == 0
            self.length_in_bytes = int(self.length_in_bits / 8)
            self.as_base_16 = bytes_utils.byte_array_to_string_base_16(self.as_bytes)
            self.as_decoded_bytes_message = bytes_messages.DecodedBytesMessage.from_bytes(self.as_bytes)

        @classmethod
        def from_remaining_bits_in_decoded_message(cls, byte_message_decoded: bytes_messages.DecodedBytesMessage) -> "OnboardSdaUnisigMessage.NetData":

            net_data_length_in_bits = byte_message_decoded.number_of_bits_remaining_to_decode
            assert net_data_length_in_bits % 8 == 0

            return OnboardSdaUnisigMessage.NetData(
                length_in_bits=net_data_length_in_bits,
                as_bytes=byte_message_decoded.get_remaining_bits_as_bytes(),
            )

        @classmethod
        def from_bytes(cls, as_bytes: bytes) -> "OnboardSdaUnisigMessage.NetData":

            net_data_length_in_bits = len(as_bytes) * 8

            return OnboardSdaUnisigMessage.NetData(
                length_in_bits=net_data_length_in_bits,
                as_bytes=as_bytes,
            )

    @classmethod
    def from_sda_hexa_bytes_str(
        cls,
        profibus_log_line: "ppn_profibus_log.ProfibusLogLine",
        bytes_hexa_str: str,
        upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary,
        ppn_connections_library: "ppn_profibus_log.PpnConnectionsLibrary",
    ) -> OnboardUnisigMessage:
        byte_message_decoded = bytes_messages.DecodedBytesMessage.from_hex_string(bytes_hexa_str)
        sda_header = OnboardSdaUnisigMessage.Header(byte_message_decoded)

        if sda_header.command_type in [
            OnboardSdaUnisigMessage.CommandTypeSubset57.SL0_DISCONNECT_TELEGRAM,
            OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_DISCONNECT_TELEGRAM,
        ]:
            disconnect_telegram = SdaDisconnectTelegram(
                ppn_connections_library=ppn_connections_library,
                profibus_log_line=profibus_log_line,
                command_type=sda_header.command_type,
                safety_level=sda_header.safety_level,
                telegram_name=sda_header.telegram_name,
                byte_message_decoded=byte_message_decoded,
                lowest_order_byte_sequence_number=sda_header.lowest_order_byte_sequence_number,
            )

            return disconnect_telegram

        elif sda_header.command_type in [
            OnboardSdaUnisigMessage.CommandTypeSubset57.SL0_IDLE_TELEGRAM,
            OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_IDLE_TELEGRAM,
        ]:
            return SdaIdleTelegram(
                ppn_connections_library=ppn_connections_library,
                profibus_log_line=profibus_log_line,
                command_type=sda_header.command_type,
                safety_level=sda_header.safety_level,
                telegram_name=sda_header.telegram_name,
                byte_message_decoded=byte_message_decoded,
                lowest_order_byte_sequence_number=sda_header.lowest_order_byte_sequence_number,
            )

        elif sda_header.command_type in [
            OnboardSdaUnisigMessage.CommandTypeSubset57.SL0_CONNECT_REQUEST_TELEGRAM,
            OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_CONNECT_REQUEST_TELEGRAM,
            OnboardSdaUnisigMessage.CommandTypeSubset57.SL0_CONNECT_CONFIRM_TELEGRAM,
            OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_CONNECT_CONFIRM_TELEGRAM,
        ]:
            return SdaConnectRequestOrConfirmTelegram(
                ppn_connections_library=ppn_connections_library,
                profibus_log_line=profibus_log_line,
                command_type=sda_header.command_type,
                safety_level=sda_header.safety_level,
                telegram_name=sda_header.telegram_name,
                byte_message_decoded=byte_message_decoded,
                lowest_order_byte_sequence_number=sda_header.lowest_order_byte_sequence_number,
            )

        elif sda_header.command_type in [
            OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_AUTHENTICATION_TELEGRAM,
            OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_AUTHENTICATION_ACKNOWLEDGEMENT_TELEGRAM,
        ]:
            return SdaAuthenticationOrAuthenticationAcknowledgementTelegram(
                ppn_connections_library=ppn_connections_library,
                profibus_log_line=profibus_log_line,
                command_type=sda_header.command_type,
                safety_level=sda_header.safety_level,
                telegram_name=sda_header.telegram_name,
                byte_message_decoded=byte_message_decoded,
                lowest_order_byte_sequence_number=sda_header.lowest_order_byte_sequence_number,
            )

        elif sda_header.command_type in [
            OnboardSdaUnisigMessage.CommandTypeSubset57.SL0_READY_TO_RUN,
            OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_READY_TO_RUN,
            OnboardSdaUnisigMessage.CommandTypeSubset57.SL0_RUN,
            OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_RUN,
        ]:
            return SdaRunOrReadyToRunTelegram(
                ppn_connections_library=ppn_connections_library,
                profibus_log_line=profibus_log_line,
                command_type=sda_header.command_type,
                safety_level=sda_header.safety_level,
                telegram_name=sda_header.telegram_name,
                byte_message_decoded=byte_message_decoded,
                lowest_order_byte_sequence_number=sda_header.lowest_order_byte_sequence_number,
            )

        elif sda_header.command_type in [
            OnboardSdaUnisigMessage.CommandTypeSubset57.SL0_TELEGRAM_FOR_UPPER_LAYER,
            OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_TELEGRAM_FOR_UPPER_LAYER,
        ]:
            return SdaForUpperLayerTelegram(
                ppn_connections_library=ppn_connections_library,
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

    class ConnectTelegramDualBusType(IntEnum):  # 5.2.1 Connect Request Telegram
        THE_NODE_IS_NOT_EQUIPPED_WITH_DUAL_BUSSES = 0
        THE_NODE_IS_EQUIPPED_WITH_DUAL_BUSSES = 1


@dataclass
class SdaDisconnectTelegram(OnboardSdaUnisigMessage):

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.safety_level == SafetyLevel.SL4:
            self.crc = UnisigCrc.from_bits_as_string(self.byte_message_decoded.get_and_remove_last_bytes_as_bitset_str(size_bytes=SL4_CRC_SIZE_IN_BYTES))

        self.all_data_aka_net_data = OnboardSdaUnisigMessage.NetData.from_remaining_bits_in_decoded_message(self.byte_message_decoded)

        self.new_setup_desired = self.all_data_aka_net_data.as_decoded_bytes_message.get_next_bits_as_bool_0_or_1(size_bits=bytes_messages.NUMBER_OF_BITS_IN_BYTE)
        self.disconnect_reason_raw = self.all_data_aka_net_data.as_decoded_bytes_message.get_next_bits_as_single_int_unsigned(size_bits=bytes_messages.NUMBER_OF_BITS_IN_BYTE)
        disconnect_reason_text_length_in_bits = self.all_data_aka_net_data.as_decoded_bytes_message.number_of_bits_remaining_to_decode
        assert disconnect_reason_text_length_in_bits % 8 == 0
        self.disconnect_reason_text = self.all_data_aka_net_data.as_decoded_bytes_message.get_next_bits_as_ascii_char(
            number_of_chars=disconnect_reason_text_length_in_bits // bytes_messages.NUMBER_OF_BITS_IN_BYTE
        )

        self.ppn_connections_library.register_disconnect_telegram(self)

    def can_src_be_computed(self) -> bool:
        return self.safety_level == SafetyLevel.SL4 and self.profibus_log_line is not None


@dataclass
class SdaConnectRequestOrConfirmTelegram(OnboardSdaUnisigMessage):

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.safety_level == SafetyLevel.SL4:
            self.crc = UnisigCrc.from_bits_as_string(self.byte_message_decoded.get_and_remove_last_bytes_as_bitset_str(size_bytes=SL4_CRC_SIZE_IN_BYTES))

        self.all_data_aka_net_data = OnboardSdaUnisigMessage.NetData.from_remaining_bits_in_decoded_message(self.byte_message_decoded)

        self.random_number_representing_sequence_number_byte_1_of_4 = self.all_data_aka_net_data.as_decoded_bytes_message.get_next_byte_as_single_int_unsigned()
        self.random_number_representing_sequence_number_byte_2_of_4 = self.all_data_aka_net_data.as_decoded_bytes_message.get_next_byte_as_single_int_unsigned()
        self.random_number_representing_sequence_number_byte_3_of_4 = self.all_data_aka_net_data.as_decoded_bytes_message.get_next_byte_as_single_int_unsigned()
        self.random_number_representing_sequence_number_byte_4_of_4 = self.all_data_aka_net_data.as_decoded_bytes_message.get_next_byte_as_single_int_unsigned()

        self.random_number_representing_sequence_number_byte_2_of_4_for_crc = self.random_number_representing_sequence_number_byte_2_of_4
        self.random_number_representing_sequence_number_byte_3_of_4_for_crc = self.random_number_representing_sequence_number_byte_3_of_4
        self.random_number_representing_sequence_number_byte_4_of_4_for_crc = self.random_number_representing_sequence_number_byte_4_of_4

        self.idle_cycle_timeout_in_100ms = Unisig16BitsIntWithUnisigBytesOrder(self.all_data_aka_net_data.as_decoded_bytes_message)
        self.configuration_data_prefix_x = self.all_data_aka_net_data.as_decoded_bytes_message.get_next_byte_as_single_int_unsigned()
        assert self.configuration_data_prefix_x == 3
        self.configuration_data_prefix_y = self.all_data_aka_net_data.as_decoded_bytes_message.get_next_byte_as_single_int_unsigned()
        assert self.configuration_data_prefix_y == 0
        self.configuration_data_prefix_z = self.all_data_aka_net_data.as_decoded_bytes_message.get_next_byte_as_single_int_unsigned()
        assert self.configuration_data_prefix_z == 0

        self.dual_bus = OnboardSdaUnisigMessage.ConnectTelegramDualBusType(self.all_data_aka_net_data.as_decoded_bytes_message.get_next_byte_as_single_int_unsigned())

        self.net_data_inside_net_data = OnboardSdaUnisigMessage.NetData.from_remaining_bits_in_decoded_message(self.all_data_aka_net_data.as_decoded_bytes_message)

        if self.command_type in [OnboardSdaUnisigMessage.CommandTypeSubset57.SL0_CONNECT_REQUEST_TELEGRAM, OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_CONNECT_REQUEST_TELEGRAM]:
            self.ppn_connections_library.register_connect_request_telegram(self)
        elif self.command_type in [OnboardSdaUnisigMessage.CommandTypeSubset57.SL0_CONNECT_CONFIRM_TELEGRAM, OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_CONNECT_CONFIRM_TELEGRAM]:
            self.ppn_connections_library.register_connect_confirm_telegram(self)

    def can_src_be_computed(self) -> bool:
        return self.safety_level == SafetyLevel.SL4 and self.profibus_log_line is not None

    def get_crc_implicit_data_except_length(self) -> "UnisigCrc.ImplicitDataExceptLength":
        assert self.profibus_log_line
        assert self.random_number_representing_sequence_number_byte_2_of_4_for_crc is not None
        assert self.random_number_representing_sequence_number_byte_3_of_4_for_crc is not None
        assert self.random_number_representing_sequence_number_byte_4_of_4_for_crc is not None

        implicit_data = UnisigCrc.ImplicitDataExceptLength.from_profibus_log_line(
            profibus_log_line=self.profibus_log_line,
            higher_order_24bits_of_sequence_number_byte_1=self.random_number_representing_sequence_number_byte_2_of_4_for_crc,
            higher_order_24bits_of_sequence_number_byte_2=self.random_number_representing_sequence_number_byte_3_of_4_for_crc,
            higher_order_24bits_of_sequence_number_byte_3=self.random_number_representing_sequence_number_byte_4_of_4_for_crc,
        )
        return implicit_data


@dataclass
class SdaAuthenticationOrAuthenticationAcknowledgementTelegram(OnboardSdaUnisigMessage):

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.safety_level == SafetyLevel.SL4:
            self.crc = UnisigCrc.from_bits_as_string(self.byte_message_decoded.get_and_remove_last_bytes_as_bitset_str(size_bytes=SL4_CRC_SIZE_IN_BYTES))

        self.all_data_aka_net_data = OnboardSdaUnisigMessage.NetData.from_remaining_bits_in_decoded_message(self.byte_message_decoded)
        self.authentication_number = Unisig32BitsIntWithUnisigBytesOrder(self.all_data_aka_net_data.as_decoded_bytes_message)

        assert self.all_data_aka_net_data.as_decoded_bytes_message.is_correctly_and_completely_decoded

    def can_src_be_computed(self) -> bool:
        return self.safety_level == SafetyLevel.SL4 and self.profibus_log_line is not None and self.current_connection_session_before_this_message is not None


@dataclass
class SdaRunOrReadyToRunTelegram(OnboardSdaUnisigMessage):

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.safety_level == SafetyLevel.SL4:
            self.crc = UnisigCrc.from_bits_as_string(self.byte_message_decoded.get_and_remove_last_bytes_as_bitset_str(size_bytes=SL4_CRC_SIZE_IN_BYTES))

        self.all_data_aka_net_data = OnboardSdaUnisigMessage.NetData.from_remaining_bits_in_decoded_message(self.byte_message_decoded)
        self.stl_time_stamp = UnisigTimeStamp.from_next_bytes_in_byte_message_decoded(self.all_data_aka_net_data.as_decoded_bytes_message)
        assert self.all_data_aka_net_data.as_decoded_bytes_message.is_correctly_and_completely_decoded

    def can_src_be_computed(self) -> bool:
        return self.safety_level == SafetyLevel.SL4 and self.profibus_log_line is not None and self.current_connection_session_before_this_message is not None


@dataclass
class SdaIdleTelegram(OnboardSdaUnisigMessage):

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.safety_level == SafetyLevel.SL4:
            self.crc = UnisigCrc.from_bits_as_string(self.byte_message_decoded.extract_next_bytes_to_str_of_bit(size_bytes=SL4_CRC_SIZE_IN_BYTES))

    def can_src_be_computed(self) -> bool:
        return self.safety_level == SafetyLevel.SL4 and self.current_connection_session_before_this_message is not None


@dataclass
class UpperLayerStm:
    upper_layer_telegram: "SdaForUpperLayerTelegram"
    byte_message_decoded: bytes_messages.DecodedBytesMessage

    def __post_init__(self) -> None:

        self.fields_names_and_values: dict[str, str | datetime.datetime | int | None] = {}

        self.nid_stm = self.byte_message_decoded.get_next_byte_as_single_int_unsigned()
        self.l_packet = self.byte_message_decoded.get_next_bits_as_single_int_unsigned(size_bits=UPPER_LAYER_STM_L_MESSAGE_FIELD_SIZE_IN_BITS)
        self.data_without_header_size_in_bits = self.l_packet - UPPER_LAYER_STM_NID_STM_FIELD_SIZE_IN_BITS - UPPER_LAYER_STM_L_MESSAGE_FIELD_SIZE_IN_BITS

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
        additional_fields_decoder_s5758.manual_additional_fields_decoding(self, field_name)


class DelegateHeader:
    def __init__(self, byte_message_decoded: bytes_messages.DecodedBytesMessage) -> None:
        self.NID_STM = byte_message_decoded.get_next_byte_as_single_int_unsigned()
        self.L_MESSAGE = byte_message_decoded.get_next_byte_as_single_int_unsigned()
        self.l_message_minus_delegate_header_size_in_bytes = self.L_MESSAGE - 2


@dataclass
class SdaForUpperLayerTelegram(OnboardSdaUnisigMessage):
    upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.safety_level == SafetyLevel.SL4:
            self.crc = UnisigCrc.from_bits_as_string(self.byte_message_decoded.get_and_remove_last_bytes_as_bitset_str(size_bytes=SL4_CRC_SIZE_IN_BYTES))

        self.all_data_aka_net_data = OnboardSdaUnisigMessage.NetData.from_remaining_bits_in_decoded_message(self.byte_message_decoded)

        self.header = DelegateHeader(self.all_data_aka_net_data.as_decoded_bytes_message)

        self.stl_time_stamp = UnisigTimeStamp.from_last_bytes_in_byte_message_decoded(self.all_data_aka_net_data.as_decoded_bytes_message)

        self.upper_layer_decoded_stms: list[UpperLayerStm] = []

        delegate_content_bytes = self.all_data_aka_net_data.as_decoded_bytes_message.get_next_bits_as_bitset_str(self.header.l_message_minus_delegate_header_size_in_bytes * 8)
        data_for_upper_layer_without_header = bytes_messages.DecodedBytesMessage.from_bit_string(delegate_content_bytes)

        while data_for_upper_layer_without_header.number_of_bits_remaining_to_decode > MAXIMUM_PADDING_SIZE_IN_BITS_SUBSET_58:

            if data_for_upper_layer_without_header.number_of_bits_remaining_to_decode >= UPPER_LAYER_STM_NID_STM_FIELD_SIZE_IN_BITS + UPPER_LAYER_STM_L_MESSAGE_FIELD_SIZE_IN_BITS:
                upper_layer_decoded_stm = UpperLayerStm(self, byte_message_decoded=data_for_upper_layer_without_header)
                self.upper_layer_decoded_stms.append(upper_layer_decoded_stm)
                assert len(self.upper_layer_decoded_stms) < 100
            else:
                self.add_error(
                    f"NotEnoughBitsToDecodeUpperLayerStm nid_content_length_in_bits={upper_layer_decoded_stm.data_without_header_size_in_bits}, byte_message_number_of_remaining_bits_to_decode={data_for_upper_layer_without_header.number_of_bits_remaining_to_decode}, upper_layer_already_decoded_stms_ids={','.join([str(stm.nid_stm) for stm in self.upper_layer_decoded_stms])}",
                )
                break

        self.padding = (
            data_for_upper_layer_without_header.get_next_bits_as_single_int_unsigned(data_for_upper_layer_without_header.number_of_bits_remaining_to_decode)
            if data_for_upper_layer_without_header.number_of_bits_remaining_to_decode > 0 and data_for_upper_layer_without_header.number_of_bits_remaining_to_decode < 8
            else (
                None
                if data_for_upper_layer_without_header.number_of_bits_remaining_to_decode == 0
                else f"Error, too many bits ({data_for_upper_layer_without_header.number_of_bits_remaining_to_decode}) for padding"
            )
        )

        self.remaining_undecoded_bits = self.all_data_aka_net_data.as_decoded_bytes_message.get_remaining_bits_as_str_of_bit()
        self.number_remaining_undecoded_bits = len(self.remaining_undecoded_bits)

        if self.number_remaining_undecoded_bits > 0:
            self.add_error(
                f"RemainingBitsUndecodedAtEndOfSdaDelegate number_of_undecoded_bits={self.number_remaining_undecoded_bits}, undecoded_bits_as_str={self.remaining_undecoded_bits}, upper_layer_already_decoded_stms_ids={','.join([str(stm.nid_stm) for stm in self.upper_layer_decoded_stms])}",
                # f"RemainingBitsUndecodedAtEndOfSdaDelegate number_of_undecoded_bits={self.number_remaining_undecoded_bits}, upper_layer_already_decoded_stms_ids={','.join([str(stm.nid_stm) for stm in self.upper_layer_decoded_stms])}",
            )

    def can_src_be_computed(self) -> bool:
        return self.safety_level == SafetyLevel.SL4 and self.profibus_log_line is not None and self.current_connection_session_before_this_message is not None
