from abc import ABC, abstractmethod
from datetime import datetime
from collections import OrderedDict
from dataclasses import dataclass
from enum import IntEnum
from typing import cast


import pyshark
import pyshark.packet.packet
from common import file_name_utils, file_utils, reports_utils, json_encoders
from logger import logger_config

from stsloganalyzis.unisig.s98 import (
    secret_equipment_name_from_ip_address,
    secret_kmac_keys,
    triple_des_s98,
)

UNISIG_S98_PORTS = [49451, 49452, 49453, 49454, 49455, 49456, 49457]
UNISIG_TRANSPORT_LAYER = "TCP"

TSHARK_FULL_PATH: str = r"C:\Program Files\Wireshark"


def byte_array_to_string_base_10(as_byte_array: bytearray) -> str:
    ret = ""
    for i in range(len(as_byte_array)):
        ret += f"{int(as_byte_array[i])}:"
    ret = ret[:-1]
    return ret


def byte_array_to_string_base_16(as_byte_array: bytearray) -> str:
    ret = ""
    for i in range(len(as_byte_array)):
        ret += f"{hex(int(as_byte_array[i]))[2:]}:"
    ret = ret[:-1]
    return ret


@dataclass
class Unisig98Equipment:
    raw_ip_address: str
    etcs_id: int

    def __post_init__(self) -> None:
        self.name = secret_equipment_name_from_ip_address.get_equipment_name_from_ip_address(self.raw_ip_address)
        logger_config.print_and_log_info(f"Equipment created:{self}")


def convert_wireshark_string_colon_separated_bytes_to_byte_array(wireshark_string_column_separated_bytes: str) -> bytearray:
    bytes_as_list_of_int = [int("0x" + byte_str, 16) for byte_str in wireshark_string_column_separated_bytes.split(":")]
    return bytearray(bytes_as_list_of_int)


@dataclass
class HexaValueSplitBySemiColonInWireshark:
    raw_str_value: str

    def __post_init__(self) -> None:
        self.as_list_of_bytes_as_string = self.raw_str_value.split(":")
        self.as_byte_array = convert_wireshark_string_colon_separated_bytes_to_byte_array(self.raw_str_value)


@dataclass
class HexaValueAsListBytesInWireshark:
    raw_str_value: str

    def __post_init__(self) -> None:
        pass
        # self.as_byte_array = convert_wireshark_string_colon_separated_bytes_to_byte_array(self.raw_str_value)


class UnisigS98EtcsIdType(IntEnum):
    UNDEFINED_NEUTRAL = 0
    ETCS_ID_PRESENT = 1
    UNKNOWN_6 = 6


class UnisigS98EmdMti(IntEnum):
    """6.2.5.1.6.1 The message type identifier (MTI) specifies the type of the SaPDU (Table 7)."""

    AU1_FIRST_AUTHENTICATION_SAPDU = 1
    AU2_SECOND_AUTHENTICATION_SAPDU = 2
    AU3_THIRD_AUTHENTICATION_SAPDU = 3
    DT_DATA_SAPDU = 5
    DISCONNECT_DI_SAPDU = 8
    AR_AUTHENTIFICATION_RESPONSE_TO_THIRD_AUTHENTICATION_SAPDU = 9


class UnisigS98EmdEty(IntEnum):
    """6.2.5.2.2 The first authentication SaPDU consists of the fields specified in Table 8."""

    RADIO_IN_FILL_UNIT = 0
    RBC = 1
    ENGINE = 2
    RESERVED_FOR_BALISE = 3
    RESERVED_FOR_FIELD_ELEMENT_EG_LEVEL_CROSSING_ETC = 4
    KEY_MANAGEMENT_ENTITY = 5
    INTERLOCKING_RELATED_ENTITY = 6


class UnisigS98PacketType(IntEnum):
    AU_1_AUTHENTICATION_PACKET_TYPE_1 = 1
    AU_2_AUTHENTICATION_PACKET_TYPE_2 = 2
    AU_3_OR_AR_OR_DT_DATA_PACKET_TYPE_3 = 3
    DISCONNECT_PACKET_TYPE_4 = 4
    DT_DATA_OR_RETRANSMISSION = 6


@dataclass
class UnisigS98WiresharkPacket:
    tcp_payload: HexaValueSplitBySemiColonInWireshark
    tcp_payload_without_ale_header: HexaValueSplitBySemiColonInWireshark
    ip_dst_str: str
    ip_src_str: str
    number: int
    ale_header: "UnisigS98WiresharkPacket.AleHeader"
    emd_byte: "UnisigS98WiresharkPacket.EmdByte"
    file_full_path: str
    sniff_time: datetime
    sniff_timestamp_str: str

    @dataclass
    class AleHeader:
        length: int
        version_hexa_str: str
        apptype_hexa_str: str
        tsn: int
        nr_flag_hexa_str: str
        packet_type: UnisigS98PacketType
        checksum_hexa_str: str

    @dataclass
    class EmdByte:
        value: int
        ety: UnisigS98EmdEty
        mti: UnisigS98EmdMti
        df: int


@dataclass
class UnisigS98WiresharkPacketWithMac(UnisigS98WiresharkPacket, ABC):
    last_au1_packet: "UnisigS98Au1WiresharkPacket | None"
    transmitted_mac: HexaValueSplitBySemiColonInWireshark

    def __post_init__(self) -> None:
        self.recomputed_mac: bytearray | None = None
        self.recomputed_mac_and_transmitted_mac_are_equals: bool | None = None

    @abstractmethod
    def has_context_to_compute_mac(self) -> bool:
        pass

    @abstractmethod
    def recompute_mac(self) -> bytearray:
        pass


@dataclass
class UnisigS98Au1WiresharkPacket(UnisigS98WiresharkPacket):
    calling_etcs_id_type: UnisigS98EtcsIdType
    calling_etcs_id: int
    called_etcs_id_type: UnisigS98EtcsIdType
    called_etcs_id: int
    random_number_b_rb: HexaValueSplitBySemiColonInWireshark
    source_addr_str: str

    def get_etcs_id_from_ip_address(self, ip_address: str) -> int:
        assert ip_address in [self.ip_src_str, self.ip_dst_str]
        return self.calling_etcs_id if ip_address == self.ip_src_str else self.called_etcs_id


@dataclass
class UnisigS98Au2WiresharkPacket(UnisigS98WiresharkPacketWithMac):
    last_au1_packet: UnisigS98Au1WiresharkPacket | None
    responding_etcs_id_type: UnisigS98EtcsIdType
    responding_etcs_id: int
    safety_feature_saf: int
    random_number_a_ra: HexaValueSplitBySemiColonInWireshark

    @dataclass
    class DataToComputeMac:
        length_bytearray: bytearray
        da_bytearray: bytearray
        ety_mti_df_as_byte_array: bytearray
        sa_responder_etcsid_as_3_bytes: bytearray
        safety_feature_saf_as_1_byte: bytearray
        ra_random_number_a_as_8_bytes: bytearray
        rb_random_number_b_as_8_bytes: bytearray
        padding_bytearray: bytearray

        def __post_init__(self) -> None:
            # l | DA | m + padding
            self.all_blocks_bytearray = (
                self.length_bytearray
                + self.da_bytearray
                + self.ety_mti_df_as_byte_array
                + self.sa_responder_etcsid_as_3_bytes
                + self.safety_feature_saf_as_1_byte
                + self.ra_random_number_a_as_8_bytes
                + self.rb_random_number_b_as_8_bytes
                + self.da_bytearray
                + self.padding_bytearray
            )
            self.all_blocks_byte_array_to_string_base_16 = byte_array_to_string_base_16(self.all_blocks_bytearray)
            self.all_blocks_byte_array_to_string_base_10 = byte_array_to_string_base_10(self.all_blocks_bytearray)
            pass

    def __post_init__(self) -> None:
        super().__post_init__()
        self.connexion_zc_pai = (
            triple_des_s98.ConnectionUnisig98(
                secret_kmac_keys.authentication_key_kmac_1,
                secret_kmac_keys.authentication_key_kmac_2,
                secret_kmac_keys.authentication_key_kmac_3,
                self.last_au1_packet.calling_etcs_id,
                self.last_au1_packet.called_etcs_id,
                192,
                True,
            )
            if self.last_au1_packet
            else None
        )

        if self.connexion_zc_pai:
            assert self.last_au1_packet
            self.connexion_zc_pai.start_session(self.random_number_a_ra.as_byte_array, self.last_au1_packet.random_number_b_rb.as_byte_array)

    def has_context_to_compute_mac(self) -> bool:
        return self.last_au1_packet is not None and self.connexion_zc_pai is not None

    def get_data_to_compute_mac(self) -> DataToComputeMac:
        """
        6.2.3.2.1.9 Concerning the AU2 SaPDU, the message m = ETY | MTI | DF | SA | SaF | auth2
        auth2 = "Ra | Rb | B
        """

        assert self.has_context_to_compute_mac()
        assert self.last_au1_packet
        assert self.connexion_zc_pai

        # l | DA (initiator) | Emd byte (ETY + MTI + DF) | SA (responder) | RA | RB | DA (=B)
        length = 27
        length_da_and_message_as_2_bytes_byte_array = bytearray(length.to_bytes(2, byteorder="big"))

        da_initiator_etcsid = self.last_au1_packet.get_etcs_id_from_ip_address(self.ip_dst_str)
        da_initiator_etcsid_etcsid_as_3_bytes_byte_array = bytearray(da_initiator_etcsid.to_bytes(3, byteorder="big"))
        assert len(da_initiator_etcsid_etcsid_as_3_bytes_byte_array) == 3

        ety_mti_df_as_int = self.emd_byte.value
        assert ety_mti_df_as_int == 197
        ety_mti_df_as_1_byte_byte_array = bytearray.fromhex(hex(ety_mti_df_as_int)[2:])

        sa_responder_etcsid = self.last_au1_packet.get_etcs_id_from_ip_address(self.ip_src_str)
        sa_responder_etcsid_as_3_bytes = bytearray(sa_responder_etcsid.to_bytes(3, byteorder="big"))
        assert len(sa_responder_etcsid_as_3_bytes) == 3

        unknwown_value_1_as_1_byte = bytearray(self.safety_feature_saf.to_bytes(1, byteorder="big"))

        ra_random_number_a_as_8_bytes = self.random_number_a_ra.as_byte_array
        rb_random_number_b_as_8_bytes = self.last_au1_packet.random_number_b_rb.as_byte_array

        padding = bytearray(int(0).to_bytes(3, byteorder="big"))
        return UnisigS98Au2WiresharkPacket.DataToComputeMac(
            length_bytearray=length_da_and_message_as_2_bytes_byte_array,
            da_bytearray=da_initiator_etcsid_etcsid_as_3_bytes_byte_array,
            ety_mti_df_as_byte_array=ety_mti_df_as_1_byte_byte_array,
            sa_responder_etcsid_as_3_bytes=sa_responder_etcsid_as_3_bytes,
            safety_feature_saf_as_1_byte=unknwown_value_1_as_1_byte,
            ra_random_number_a_as_8_bytes=ra_random_number_a_as_8_bytes,
            rb_random_number_b_as_8_bytes=rb_random_number_b_as_8_bytes,
            padding_bytearray=padding,
        )

    def recompute_mac(self) -> bytearray:
        assert self.has_context_to_compute_mac()
        assert self.last_au1_packet
        assert self.connexion_zc_pai

        data_to_compute_mac = self.get_data_to_compute_mac()

        self.recomputed_mac = self.connexion_zc_pai.compute_mac_n_blocks(data_to_compute_mac.all_blocks_bytearray, verbose=True)

        compare_as_byte_array = self.recomputed_mac == self.transmitted_mac.as_byte_array
        compare_as_string = triple_des_s98.convert_mac_to_string_of_hexas(self.recomputed_mac) == triple_des_s98.convert_mac_to_string_of_hexas(self.transmitted_mac.as_byte_array)
        assert compare_as_byte_array == compare_as_string
        self.recomputed_mac_and_transmitted_mac_are_equals = compare_as_byte_array

        return self.recomputed_mac


@dataclass
class UnisigS98Au3WiresharkPacket(UnisigS98WiresharkPacketWithMac):

    def get_data_to_compute_mac(self) -> None:
        """
        6.2.3.2.1.10 Concerning the AU3 SaPDU, the message m = 000 | MTI | DF | auth3
        auth3 = Rb | Ra.
        """
        pass

    def has_context_to_compute_mac(self) -> bool:
        logger_config.print_and_log_error("Not implemented")
        assert False

    def recompute_mac(self) -> bytearray:
        logger_config.print_and_log_error("Not implemented")
        assert False


@dataclass
class UnisigS98AuthenticationResponseWiresharkPacket(UnisigS98WiresharkPacketWithMac):

    def has_context_to_compute_mac(self) -> bool:
        logger_config.print_and_log_error("Not implemented")
        assert False

    def recompute_mac(self) -> bytearray:
        logger_config.print_and_log_error("Not implemented")
        assert False


@dataclass
class UnisigS98DtDataWiresharkPacket(UnisigS98WiresharkPacketWithMac):
    connexion_zc_pai: triple_des_s98.ConnectionUnisig98 | None
    sai_user_data: HexaValueSplitBySemiColonInWireshark | None

    @dataclass
    class DataToComputeMac:
        length_bytearray: bytearray
        da_bytearray: bytearray
        message_bytearray: bytearray
        padding_bytearray: bytearray

        def __post_init__(self) -> None:
            # l | DA | m + padding
            self.all_blocks_bytearray = self.length_bytearray + self.da_bytearray + self.message_bytearray + self.padding_bytearray

    def __post_init__(self) -> None:
        super().__post_init__()
        self.tcp_payload_without_ale_header_and_mac = HexaValueSplitBySemiColonInWireshark(self.tcp_payload_without_ale_header.raw_str_value[:-24])
        self.recomputed_mac: bytearray | None = None
        self.recomputed_mac_and_transmitted_mac_are_equals: bool | None = None
        if self.sai_user_data is None:
            pass

    def get_data_to_compute_mac(self) -> DataToComputeMac:
        assert self.connexion_zc_pai
        assert self.last_au1_packet
        message_receiver_etcsid = self.last_au1_packet.get_etcs_id_from_ip_address(self.ip_dst_str)
        # message_receiver_etcsid_as_3_bytes = bytearray(message_receiver_etcsid)
        message_receiver_etcsid_as_3_bytes = bytearray(message_receiver_etcsid.to_bytes(3, byteorder="big"))

        assert len(message_receiver_etcsid_as_3_bytes) == 3

        length_da_and_message = len(message_receiver_etcsid_as_3_bytes) + len(self.tcp_payload_without_ale_header_and_mac.as_list_of_bytes_as_string)
        length_da_and_message_as_2_bytes = bytearray(length_da_and_message.to_bytes(2, byteorder="big"))
        # l | DA | m
        l_da_message = length_da_and_message_as_2_bytes + message_receiver_etcsid_as_3_bytes + self.tcp_payload_without_ale_header_and_mac.as_byte_array

        l_da_message_with_padding = l_da_message

        padding = bytearray()
        while len(l_da_message_with_padding) % 8 != 0:
            padding += bytearray.fromhex("00")
            l_da_message_with_padding = l_da_message + padding

        return UnisigS98DtDataWiresharkPacket.DataToComputeMac(
            da_bytearray=message_receiver_etcsid_as_3_bytes,
            length_bytearray=length_da_and_message_as_2_bytes,
            message_bytearray=self.tcp_payload_without_ale_header_and_mac.as_byte_array,
            padding_bytearray=padding,
        )

    def has_context_to_compute_mac(self) -> bool:
        return self.last_au1_packet is not None and self.connexion_zc_pai is not None

    def recompute_mac(self) -> bytearray:
        assert self.last_au1_packet
        assert self.connexion_zc_pai
        data_to_compute_mac = self.get_data_to_compute_mac()
        self.recomputed_mac = self.connexion_zc_pai.compute_mac_n_blocks(data_to_compute_mac.all_blocks_bytearray)

        compare_as_byte_array = self.recomputed_mac == self.transmitted_mac.as_byte_array
        compare_as_string = triple_des_s98.convert_mac_to_string_of_hexas(self.recomputed_mac) == triple_des_s98.convert_mac_to_string_of_hexas(self.transmitted_mac.as_byte_array)
        assert compare_as_byte_array == compare_as_string
        self.recomputed_mac_and_transmitted_mac_are_equals = compare_as_byte_array
        return self.recomputed_mac


@dataclass
class UnisigS98PaiDisconnectRequest(UnisigS98WiresharkPacket):
    remaining_data: HexaValueSplitBySemiColonInWireshark


@dataclass
class UnisigS98Simulation:

    def __init__(self) -> None:
        self.unisig_s98_packets: list[UnisigS98WiresharkPacket] = []
        self.equipments: list[Unisig98Equipment] = []
        self.last_au1_packet_by_interlocutors: dict[tuple[str, str], UnisigS98Au1WiresharkPacket] = {}
        self.last_connexion_by_interlocutors: dict[tuple[str, str], triple_des_s98.ConnectionUnisig98] = {}
        self.directories_parsed: list[str] = []
        self.files_full_paths_parsed: list[str] = []

    @property
    def label(self) -> str:
        if self.directories_parsed:
            return " ".join([file_name_utils.get_directory_name_from_directory_full_path(directory_parsed) for directory_parsed in self.directories_parsed])

        if self.files_full_paths_parsed:
            return " ".join([file_name_utils.get_file_name_without_extension_from_full_path(file_full_path_parsed) for file_full_path_parsed in self.files_full_paths_parsed])

        return ""

    def register_au1_packet(self, packet: UnisigS98Au1WiresharkPacket) -> None:
        logger_config.print_and_log_info(f"AU1 packet detected from {packet.ip_src_str} to {packet.ip_dst_str}")
        self.get_or_create_equipment_by_ip_address_and_etcs_id(packet.ip_src_str, packet.calling_etcs_id)
        self.get_or_create_equipment_by_ip_address_and_etcs_id(packet.ip_dst_str, packet.called_etcs_id)
        self.last_au1_packet_by_interlocutors[(packet.ip_src_str, packet.ip_dst_str)] = packet
        self.last_au1_packet_by_interlocutors[(packet.ip_dst_str, packet.ip_src_str)] = packet

    def register_au2_packet(self, packet: UnisigS98Au2WiresharkPacket) -> None:
        logger_config.print_and_log_info(f"AU2 packet detected from {packet.ip_src_str} to {packet.ip_dst_str}")
        if not packet.connexion_zc_pai:
            logger_config.print_and_log_error(f"Could not handle AU2 packet {packet} because no previous AU1 packet")
            self.last_connexion_by_interlocutors.pop((packet.ip_src_str, packet.ip_dst_str))
            self.last_connexion_by_interlocutors.pop((packet.ip_dst_str, packet.ip_src_str))
            return
        self.last_connexion_by_interlocutors[(packet.ip_src_str, packet.ip_dst_str)] = packet.connexion_zc_pai
        self.last_connexion_by_interlocutors[(packet.ip_dst_str, packet.ip_src_str)] = packet.connexion_zc_pai

    def register_disconnect_request_packet(self, packet: UnisigS98PaiDisconnectRequest) -> None:
        logger_config.print_and_log_info(f"Disconnect request packet detected from {packet.ip_src_str} to {packet.ip_dst_str}")
        self.last_connexion_by_interlocutors.pop((packet.ip_src_str, packet.ip_dst_str), None)
        self.last_connexion_by_interlocutors.pop((packet.ip_dst_str, packet.ip_src_str), None)
        self.last_au1_packet_by_interlocutors.pop((packet.ip_src_str, packet.ip_dst_str), None)
        self.last_au1_packet_by_interlocutors.pop((packet.ip_dst_str, packet.ip_src_str), None)

    def get_or_create_equipment_by_ip_address_and_etcs_id(self, raw_ip_address: str, etcs_id: int) -> Unisig98Equipment:
        equipments_found = [equipment for equipment in self.equipments if equipment.raw_ip_address == raw_ip_address and equipment.etcs_id == etcs_id]
        if equipments_found:
            assert len(equipments_found) == 1
            return equipments_found[0]
        self.equipments.append(Unisig98Equipment(raw_ip_address=raw_ip_address, etcs_id=etcs_id))
        return self.get_or_create_equipment_by_ip_address_and_etcs_id(raw_ip_address, etcs_id)

    def build_unisig_s98_packets_from_load_pcap_files_in_directory(self, pcap_directory_full_path: str, filename_pattern: str = "*") -> None:

        self.directories_parsed.append(pcap_directory_full_path)
        all_pcap_files_full_paths = file_utils.get_files_by_directory_and_file_name_mask(
            directory_path=pcap_directory_full_path,
            file_sort_order=file_utils.FileSortOrder.TIMESTAMP_OLDER_TO_NEWER,
            filename_pattern=filename_pattern,
        )
        logger_config.print_and_log_info(f"{len(all_pcap_files_full_paths)} files found in {pcap_directory_full_path}")
        for pcap_file_full_path in all_pcap_files_full_paths:
            self.build_unisig_s98_packets_from_load_pcap_file(pcap_file_full_path)

    @logger_config.stopwatch_decorator(monitor_ram_usage=True)
    def build_unisig_s98_packets_from_load_pcap_file(self, pcap_file_full_path: str) -> None:

        self.files_full_paths_parsed.append(pcap_file_full_path)
        capture = pyshark.FileCapture(pcap_file_full_path, tshark_path=TSHARK_FULL_PATH, display_filter="ss098")

        number_of_packets_parsed = 0
        number_of_errors = 0
        unisig_s98_packets_found: list[UnisigS98WiresharkPacket] = []

        for number_of_packets_parsed, packet in enumerate(capture):

            packet = cast(pyshark.packet.packet.Packet, packet)
            try:
                if packet.transport_layer == UNISIG_TRANSPORT_LAYER and int(packet.tcp.port) in UNISIG_S98_PORTS and "payload" in packet.tcp.field_names and packet.get_multiple_layers("ss098"):
                    unisig_s98_packets_found.append(self.build_unisig_s98_packet_from_wireshark_packet(packet, pcap_file_full_path))

            except (AttributeError, ValueError, AssertionError) as exc_catched:
                logger_config.print_and_log_exception(exc_catched)
                logger_config.print_and_log_error(f"Could not parse {number_of_packets_parsed+1} th packet of {pcap_file_full_path} at {packet.frame_info}")
                number_of_errors += 1

            logger_config.print_and_log_info_if(
                (number_of_packets_parsed + 1) % 1000 == 0,
                f"{number_of_packets_parsed+1} packets parsed, {len(unisig_s98_packets_found)} unisig packets found so far in {pcap_file_full_path}",
                print_ram_usage=True,
            )
        self.unisig_s98_packets += unisig_s98_packets_found

    def build_unisig_s98_packet_from_wireshark_packet(self, wireshark_packet: pyshark.packet.packet.Packet, pcap_file_full_path: str) -> UnisigS98WiresharkPacket:
        tcp_payload = HexaValueSplitBySemiColonInWireshark(wireshark_packet.tcp.payload)
        tcp_payload_without_ale_header = HexaValueSplitBySemiColonInWireshark(tcp_payload.raw_str_value[30:])

        sniff_time = wireshark_packet.sniff_time
        assert isinstance(sniff_time, datetime)
        sniff_timestamp_str = wireshark_packet.sniff_timestamp
        number = int(wireshark_packet.number)
        ip_dst_str = wireshark_packet.ip.dst
        ip_src_str = wireshark_packet.ip.src

        packet_type = UnisigS98PacketType(int(wireshark_packet.ss098.get_field_value("ss098.ale.packet_type")))

        ale_header = UnisigS98WiresharkPacket.AleHeader(
            length=int(wireshark_packet.ss098.get_field_value("ss098.ale.length")),
            version_hexa_str=wireshark_packet.ss098.get_field_value("ss098.ale.version"),
            apptype_hexa_str=wireshark_packet.ss098.get_field_value("ss098.ale.apptype"),
            tsn=int(wireshark_packet.ss098.get_field_value("ss098.ale.tsn")),
            nr_flag_hexa_str=wireshark_packet.ss098.get_field_value("ss098.ale.nr_flag"),
            packet_type=packet_type,
            checksum_hexa_str=wireshark_packet.ss098.get_field_value("ss098.ale.checksum_hexa_str"),
        )

        emd_byte = UnisigS98WiresharkPacket.EmdByte(
            value=int(wireshark_packet.ss098.get_field_value("ss098.sai.emd"), 16),
            ety=UnisigS98EmdEty(int(wireshark_packet.ss098.get_field_value("ss098.sai.ety"))),
            mti=UnisigS98EmdMti(int(wireshark_packet.ss098.get_field_value("ss098.sai.mti"))),
            df=int(wireshark_packet.ss098.get_field_value("ss098.sai.df")),
        )

        if packet_type == UnisigS98PacketType.AU_1_AUTHENTICATION_PACKET_TYPE_1:

            au1_packet = UnisigS98Au1WiresharkPacket(
                file_full_path=pcap_file_full_path,
                sniff_time=sniff_time.replace(tzinfo=None),
                sniff_timestamp_str=sniff_timestamp_str,
                tcp_payload=tcp_payload,
                tcp_payload_without_ale_header=tcp_payload_without_ale_header,
                ip_dst_str=ip_dst_str,
                ip_src_str=ip_src_str,
                number=number,
                ale_header=ale_header,
                emd_byte=emd_byte,
                calling_etcs_id_type=UnisigS98EtcsIdType(int(wireshark_packet.ss098.get_field_value("ss098.conn.calling_ety"))),
                calling_etcs_id=int(wireshark_packet.ss098.get_field_value("ss098.conn.calling_id")),
                called_etcs_id_type=UnisigS98EtcsIdType(int(wireshark_packet.ss098.get_field_value("ss098.conn.called_ety"))),
                called_etcs_id=int(wireshark_packet.ss098.get_field_value("ss098.conn.called_id")),
                random_number_b_rb=HexaValueSplitBySemiColonInWireshark(wireshark_packet.ss098.get_field_value("ss098.conn.rb")),
                source_addr_str=wireshark_packet.ss098.get_field_value("ss098.conn.source_addr"),
            )
            self.register_au1_packet(au1_packet)
            return au1_packet
        elif packet_type == UnisigS98PacketType.AU_2_AUTHENTICATION_PACKET_TYPE_2:
            last_au1_packet = self.last_au1_packet_by_interlocutors.get((ip_src_str, ip_dst_str))
            au2 = UnisigS98Au2WiresharkPacket(
                file_full_path=pcap_file_full_path,
                sniff_time=sniff_time,
                sniff_timestamp_str=sniff_timestamp_str,
                last_au1_packet=last_au1_packet,
                tcp_payload=tcp_payload,
                tcp_payload_without_ale_header=tcp_payload_without_ale_header,
                ip_dst_str=ip_dst_str,
                ip_src_str=ip_src_str,
                number=number,
                ale_header=ale_header,
                emd_byte=emd_byte,
                responding_etcs_id_type=UnisigS98EtcsIdType(int(wireshark_packet.ss098.get_field_value("ss098.conn.resp_ety"))),
                responding_etcs_id=int(wireshark_packet.ss098.get_field_value("ss098.conn.resp_id")),
                safety_feature_saf=int(wireshark_packet.ss098.get_field_value("ss098.conn.saf")),
                random_number_a_ra=HexaValueSplitBySemiColonInWireshark(wireshark_packet.ss098.get_field_value("ss098.conn.ra")),
                transmitted_mac=HexaValueSplitBySemiColonInWireshark(wireshark_packet.ss098.get_field_value("ss098.auth.mac")),
            )
            self.register_au2_packet(au2)
            return au2
        elif packet_type == UnisigS98PacketType.AU_3_OR_AR_OR_DT_DATA_PACKET_TYPE_3:
            last_au1_packet = self.last_au1_packet_by_interlocutors.get((ip_src_str, ip_dst_str))
            last_connexion = self.last_connexion_by_interlocutors.get((ip_src_str, ip_dst_str))
            if emd_byte.mti == UnisigS98EmdMti.DT_DATA_SAPDU:
                return UnisigS98DtDataWiresharkPacket(
                    file_full_path=pcap_file_full_path,
                    sniff_time=sniff_time,
                    sniff_timestamp_str=sniff_timestamp_str,
                    last_au1_packet=last_au1_packet,
                    connexion_zc_pai=last_connexion,
                    tcp_payload=tcp_payload,
                    tcp_payload_without_ale_header=tcp_payload_without_ale_header,
                    ip_dst_str=ip_dst_str,
                    ip_src_str=ip_src_str,
                    number=number,
                    ale_header=ale_header,
                    emd_byte=emd_byte,
                    sai_user_data=(
                        HexaValueSplitBySemiColonInWireshark(wireshark_packet.ss098.get_field_value("ss098.sai.user_data")) if wireshark_packet.ss098.get_field_value("ss098.sai.user_data") else None
                    ),
                    transmitted_mac=HexaValueSplitBySemiColonInWireshark(wireshark_packet.ss098.get_field_value("ss098.sai.mac")),
                )

            elif emd_byte.mti == UnisigS98EmdMti.AU3_THIRD_AUTHENTICATION_SAPDU:
                return UnisigS98Au3WiresharkPacket(
                    last_au1_packet=last_au1_packet,
                    file_full_path=pcap_file_full_path,
                    sniff_time=sniff_time,
                    sniff_timestamp_str=sniff_timestamp_str,
                    tcp_payload=tcp_payload,
                    tcp_payload_without_ale_header=tcp_payload_without_ale_header,
                    ip_dst_str=ip_dst_str,
                    ip_src_str=ip_src_str,
                    number=number,
                    ale_header=ale_header,
                    emd_byte=emd_byte,
                    transmitted_mac=HexaValueSplitBySemiColonInWireshark(wireshark_packet.ss098.get_field_value("ss098.auth.mac")),
                )
            elif emd_byte.mti == UnisigS98EmdMti.AR_AUTHENTIFICATION_RESPONSE_TO_THIRD_AUTHENTICATION_SAPDU:
                return UnisigS98AuthenticationResponseWiresharkPacket(
                    last_au1_packet=last_au1_packet,
                    file_full_path=pcap_file_full_path,
                    sniff_time=sniff_time,
                    sniff_timestamp_str=sniff_timestamp_str,
                    tcp_payload=tcp_payload,
                    tcp_payload_without_ale_header=tcp_payload_without_ale_header,
                    ip_dst_str=ip_dst_str,
                    ip_src_str=ip_src_str,
                    number=number,
                    ale_header=ale_header,
                    emd_byte=emd_byte,
                    transmitted_mac=HexaValueSplitBySemiColonInWireshark(wireshark_packet.ss098.get_field_value("ss098.auth.mac")),
                )
            assert False, f"Unsupported emd_byte.mti {emd_byte.mti} in {wireshark_packet.frame_info}"
        elif packet_type == UnisigS98PacketType.DISCONNECT_PACKET_TYPE_4:
            disconnect_request = UnisigS98PaiDisconnectRequest(
                file_full_path=pcap_file_full_path,
                sniff_time=sniff_time,
                sniff_timestamp_str=sniff_timestamp_str,
                tcp_payload=tcp_payload,
                tcp_payload_without_ale_header=tcp_payload_without_ale_header,
                ip_dst_str=ip_dst_str,
                ip_src_str=ip_src_str,
                number=number,
                ale_header=ale_header,
                emd_byte=emd_byte,
                remaining_data=HexaValueSplitBySemiColonInWireshark(
                    wireshark_packet.ss098.get_field_value("ss098.data"),
                ),
            )
            self.register_disconnect_request_packet(disconnect_request)
            return disconnect_request

        assert False, f"Unsupported packet_type {packet_type} in {wireshark_packet.frame_info}"

    @logger_config.stopwatch_decorator(monitor_ram_usage=True, inform_beginning=True)
    def recompute_all_mac(self) -> tuple[int, int]:
        mac_computed = 0
        errors = 0
        for unisig_s98_packet in self.unisig_s98_packets:
            try:
                if isinstance(unisig_s98_packet, UnisigS98WiresharkPacketWithMac) and unisig_s98_packet.has_context_to_compute_mac():
                    unisig_s98_packet.recompute_mac()
                    mac_computed += 1
            except AssertionError as ass_err:
                logger_config.print_and_log_exception(ass_err)
                errors += 1

        logger_config.print_and_log_info(f"{mac_computed} mac computed. {errors} errors")
        return mac_computed, errors

    def dump_packets_as_json(self, output_directory: str) -> None:
        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(self.unisig_s98_packets, json_file_full_path=output_directory + "\\" + self.label + " json dump")

    def save_all_packets_as_reports(self) -> None:

        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=[
                OrderedDict(
                    {
                        "File name": file_name_utils.get_file_name_without_extension_from_full_path(unisig_s98_packet.file_full_path),
                        "Number": unisig_s98_packet.number,
                        "sniff_time": unisig_s98_packet.sniff_time,
                        "sniff_timestamp_str": unisig_s98_packet.sniff_timestamp_str,
                        "class": unisig_s98_packet.__class__.__name__,
                        "ip_src_str": unisig_s98_packet.ip_src_str,
                        "ip_dst_str": unisig_s98_packet.ip_dst_str,
                        "emd_byte": unisig_s98_packet.emd_byte.value,
                        "emb ety": unisig_s98_packet.emd_byte.ety,
                        "emb mti": unisig_s98_packet.emd_byte.mti,
                        "emb df": unisig_s98_packet.emd_byte.df,
                        "ale length": unisig_s98_packet.ale_header.length,
                        "ale packet type": unisig_s98_packet.ale_header.packet_type,
                        "transmitted mac str": (
                            unisig_s98_packet.transmitted_mac.raw_str_value if isinstance(unisig_s98_packet, UnisigS98WiresharkPacketWithMac) and unisig_s98_packet.transmitted_mac else None
                        ),
                        "recomputed mac as str base 10": (
                            byte_array_to_string_base_10(unisig_s98_packet.recomputed_mac)
                            if isinstance(unisig_s98_packet, UnisigS98WiresharkPacketWithMac) and unisig_s98_packet.recomputed_mac
                            else None
                        ),
                        "recomputed mac as str base 16": (
                            byte_array_to_string_base_16(unisig_s98_packet.recomputed_mac)
                            if isinstance(unisig_s98_packet, UnisigS98WiresharkPacketWithMac) and unisig_s98_packet.recomputed_mac
                            else None
                        ),
                        "recomputed_mac_and_transmitted_mac_are_equals": (
                            unisig_s98_packet.recomputed_mac_and_transmitted_mac_are_equals if isinstance(unisig_s98_packet, UnisigS98WiresharkPacketWithMac) else None
                        ),
                        "data to compute mac: length_bytearray (base 10)": (
                            byte_array_to_string_base_10(unisig_s98_packet.get_data_to_compute_mac().length_bytearray)
                            if isinstance(unisig_s98_packet, UnisigS98DtDataWiresharkPacket) and unisig_s98_packet.has_context_to_compute_mac()
                            else None
                        ),
                        "data to compute mac: da_bytearray (base 10)": (
                            byte_array_to_string_base_10(unisig_s98_packet.get_data_to_compute_mac().da_bytearray)
                            if isinstance(unisig_s98_packet, UnisigS98DtDataWiresharkPacket) and unisig_s98_packet.has_context_to_compute_mac()
                            else None
                        ),
                        "data to compute mac: message_bytearray (base 10)": (
                            byte_array_to_string_base_10(unisig_s98_packet.get_data_to_compute_mac().message_bytearray)
                            if isinstance(unisig_s98_packet, UnisigS98DtDataWiresharkPacket) and unisig_s98_packet.has_context_to_compute_mac()
                            else None
                        ),
                        "data to compute mac: padding_bytearray (base 10)": (
                            byte_array_to_string_base_10(unisig_s98_packet.get_data_to_compute_mac().padding_bytearray)
                            if isinstance(unisig_s98_packet, UnisigS98DtDataWiresharkPacket) and unisig_s98_packet.has_context_to_compute_mac()
                            else None
                        ),
                        "data to compute mac: length_bytearray (base 16)": (
                            byte_array_to_string_base_16(unisig_s98_packet.get_data_to_compute_mac().length_bytearray)
                            if isinstance(unisig_s98_packet, UnisigS98DtDataWiresharkPacket) and unisig_s98_packet.has_context_to_compute_mac()
                            else None
                        ),
                        "data to compute mac: da_bytearray (base 16)": (
                            byte_array_to_string_base_16(unisig_s98_packet.get_data_to_compute_mac().da_bytearray)
                            if isinstance(unisig_s98_packet, UnisigS98DtDataWiresharkPacket) and unisig_s98_packet.has_context_to_compute_mac()
                            else None
                        ),
                        "data to compute mac: message_bytearray (base 16)": (
                            byte_array_to_string_base_16(unisig_s98_packet.get_data_to_compute_mac().message_bytearray)
                            if isinstance(unisig_s98_packet, UnisigS98DtDataWiresharkPacket) and unisig_s98_packet.has_context_to_compute_mac()
                            else None
                        ),
                        "data to compute mac: padding_bytearray (base 16)": (
                            byte_array_to_string_base_16(unisig_s98_packet.get_data_to_compute_mac().padding_bytearray)
                            if isinstance(unisig_s98_packet, UnisigS98DtDataWiresharkPacket) and unisig_s98_packet.has_context_to_compute_mac()
                            else None
                        ),
                    }
                )
                for unisig_s98_packet in self.unisig_s98_packets
            ],
            file_base_name=self.label + " all packets",
            create_csv_file=False,
            create_txt_file=False,
            split_big_files=False,
            chunk_size=200000,
        )
