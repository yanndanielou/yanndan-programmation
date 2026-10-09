from dataclasses import dataclass
from enum import IntEnum
from typing import cast

from collections import OrderedDict

import pyshark
import pyshark.packet.packet
from common import file_utils, reports_utils, file_name_utils
from logger import logger_config

from stsloganalyzis.unisig.s98 import secret_equipment_name_from_ip_address, secret_kmac_keys, triple_des_s98

UNISIG_S98_PORTS = [49451, 49452, 49453, 49454, 49455, 49456, 49457]
UNISIG_TRANSPORT_LAYER = "TCP"

TSHARK_FULL_PATH: str = r"C:\Program Files\Wireshark"


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
        ety: int
        mti: UnisigS98EmdMti
        df: int


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
class UnisigS98Au2WiresharkPacket(UnisigS98WiresharkPacket):
    last_au1_packet: UnisigS98Au1WiresharkPacket | None
    responding_etcs_id_type: UnisigS98EtcsIdType
    responding_etcs_id: int
    random_number_a_ra: HexaValueSplitBySemiColonInWireshark
    mac: HexaValueSplitBySemiColonInWireshark

    def __post_init__(self) -> None:
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

        self.recomputed_mac: bytearray | None = None
        self.recomputed_mac_and_transmitted_mac_are_equals: bool | None = None

        if self.connexion_zc_pai:
            assert self.last_au1_packet
            self.connexion_zc_pai.start_session(self.random_number_a_ra.as_byte_array, self.last_au1_packet.random_number_b_rb.as_byte_array)

    def recompute_mac(self) -> bytearray:
        assert self.last_au1_packet
        assert self.connexion_zc_pai
        self.recomputed_mac = self.connexion_zc_pai.compute_input_mac_au2()

        compare_as_byte_array = self.recomputed_mac == self.mac.as_byte_array
        compare_as_string = triple_des_s98.convert_mac_to_string_of_hexas(self.recomputed_mac) == triple_des_s98.convert_mac_to_string_of_hexas(self.mac.as_byte_array)
        assert compare_as_byte_array == compare_as_string
        self.recomputed_mac_and_transmitted_mac_are_equals = compare_as_byte_array
        return self.recomputed_mac


@dataclass
class UnisigS98Au3WiresharkPacket(UnisigS98WiresharkPacket):
    mac: HexaValueSplitBySemiColonInWireshark


@dataclass
class UnisigS98AuthenticationResponseWiresharkPacket(UnisigS98WiresharkPacket):
    mac: HexaValueSplitBySemiColonInWireshark


@dataclass
class UnisigS98DtDataWiresharkPacket(UnisigS98WiresharkPacket):
    last_au1_packet: UnisigS98Au1WiresharkPacket | None
    connexion_zc_pai: triple_des_s98.ConnectionUnisig98 | None
    sai_user_data: HexaValueSplitBySemiColonInWireshark | None
    mac: HexaValueSplitBySemiColonInWireshark

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

    def recompute_mac(self) -> bytearray:
        assert self.last_au1_packet
        assert self.connexion_zc_pai
        data_to_compute_mac = self.get_data_to_compute_mac()
        self.recomputed_mac = self.connexion_zc_pai.compute_mac_n_blocks(data_to_compute_mac.all_blocks_bytearray)

        compare_as_byte_array = self.recomputed_mac == self.mac.as_byte_array
        compare_as_string = triple_des_s98.convert_mac_to_string_of_hexas(self.recomputed_mac) == triple_des_s98.convert_mac_to_string_of_hexas(self.mac.as_byte_array)
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
            return " ".join(self.directories_parsed)

        if self.files_full_paths_parsed:
            return " ".join([file_name_utils.get_file_name_without_extension_from_full_path(file_full_path_parsed) for file_full_path_parsed in self.files_full_paths_parsed])

        return ""

    def register_au1_packet(self, au1_packet: UnisigS98Au1WiresharkPacket) -> None:
        self.get_or_create_equipment_by_ip_address_and_etcs_id(au1_packet.ip_src_str, au1_packet.calling_etcs_id)
        self.get_or_create_equipment_by_ip_address_and_etcs_id(au1_packet.ip_dst_str, au1_packet.called_etcs_id)
        self.last_au1_packet_by_interlocutors[(au1_packet.ip_src_str, au1_packet.ip_dst_str)] = au1_packet
        self.last_au1_packet_by_interlocutors[(au1_packet.ip_dst_str, au1_packet.ip_src_str)] = au1_packet

    def register_au2_packet(self, au2_packet: UnisigS98Au2WiresharkPacket) -> None:
        if not au2_packet.connexion_zc_pai:
            logger_config.print_and_log_error(f"Could not handle AU2 packet {au2_packet} because no previous AU1 packet")
            self.last_connexion_by_interlocutors.pop((au2_packet.ip_src_str, au2_packet.ip_dst_str))
            self.last_connexion_by_interlocutors.pop((au2_packet.ip_dst_str, au2_packet.ip_src_str))
            return
        self.last_connexion_by_interlocutors[(au2_packet.ip_src_str, au2_packet.ip_dst_str)] = au2_packet.connexion_zc_pai
        self.last_connexion_by_interlocutors[(au2_packet.ip_dst_str, au2_packet.ip_src_str)] = au2_packet.connexion_zc_pai

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
                number_of_packets_parsed + 1 % 1000 == 0,
                f"{number_of_packets_parsed+1} packets parsed, {len(unisig_s98_packets_found)} unisig packets found so far in {pcap_file_full_path}",
                print_ram_usage=True,
            )
        self.unisig_s98_packets += unisig_s98_packets_found

    def build_unisig_s98_packet_from_wireshark_packet(self, wireshark_packet: pyshark.packet.packet.Packet, pcap_file_full_path: str) -> UnisigS98WiresharkPacket:
        tcp_payload = HexaValueSplitBySemiColonInWireshark(wireshark_packet.tcp.payload)
        tcp_payload_without_ale_header = HexaValueSplitBySemiColonInWireshark(tcp_payload.raw_str_value[30:])

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
            ety=int(wireshark_packet.ss098.get_field_value("ss098.sai.ety")),
            mti=UnisigS98EmdMti(int(wireshark_packet.ss098.get_field_value("ss098.sai.mti"))),
            df=int(wireshark_packet.ss098.get_field_value("ss098.sai.df")),
        )

        if packet_type == UnisigS98PacketType.AU_1_AUTHENTICATION_PACKET_TYPE_1:

            au1_packet = UnisigS98Au1WiresharkPacket(
                file_full_path=pcap_file_full_path,
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
                random_number_a_ra=HexaValueSplitBySemiColonInWireshark(wireshark_packet.ss098.get_field_value("ss098.conn.ra")),
                mac=HexaValueSplitBySemiColonInWireshark(wireshark_packet.ss098.get_field_value("ss098.auth.mac")),
            )
            self.register_au2_packet(au2)
            return au2
        elif packet_type == UnisigS98PacketType.AU_3_OR_AR_OR_DT_DATA_PACKET_TYPE_3:
            last_au1_packet = self.last_au1_packet_by_interlocutors.get((ip_src_str, ip_dst_str))
            last_connexion = self.last_connexion_by_interlocutors.get((ip_src_str, ip_dst_str))
            if emd_byte.mti == UnisigS98EmdMti.DT_DATA_SAPDU:
                return UnisigS98DtDataWiresharkPacket(
                    file_full_path=pcap_file_full_path,
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
                    mac=HexaValueSplitBySemiColonInWireshark(wireshark_packet.ss098.get_field_value("ss098.sai.mac")),
                )

            elif emd_byte.mti == UnisigS98EmdMti.AU3_THIRD_AUTHENTICATION_SAPDU:
                return UnisigS98Au3WiresharkPacket(
                    file_full_path=pcap_file_full_path,
                    tcp_payload=tcp_payload,
                    tcp_payload_without_ale_header=tcp_payload_without_ale_header,
                    ip_dst_str=ip_dst_str,
                    ip_src_str=ip_src_str,
                    number=number,
                    ale_header=ale_header,
                    emd_byte=emd_byte,
                    mac=HexaValueSplitBySemiColonInWireshark(wireshark_packet.ss098.get_field_value("ss098.auth.mac")),
                )
            elif emd_byte.mti == UnisigS98EmdMti.AR_AUTHENTIFICATION_RESPONSE_TO_THIRD_AUTHENTICATION_SAPDU:
                return UnisigS98AuthenticationResponseWiresharkPacket(
                    file_full_path=pcap_file_full_path,
                    tcp_payload=tcp_payload,
                    tcp_payload_without_ale_header=tcp_payload_without_ale_header,
                    ip_dst_str=ip_dst_str,
                    ip_src_str=ip_src_str,
                    number=number,
                    ale_header=ale_header,
                    emd_byte=emd_byte,
                    mac=HexaValueSplitBySemiColonInWireshark(wireshark_packet.ss098.get_field_value("ss098.auth.mac")),
                )
            assert False, f"Unsupported emd_byte.mti {emd_byte.mti} in {wireshark_packet.frame_info}"
        elif packet_type == UnisigS98PacketType.DISCONNECT_PACKET_TYPE_4:
            return UnisigS98PaiDisconnectRequest(
                file_full_path=pcap_file_full_path,
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
        assert False, f"Unsupported packet_type {packet_type} in {wireshark_packet.frame_info}"

    def save_all_packets(self) -> None:

        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=[
                OrderedDict(
                    {
                        "File name": file_name_utils.get_file_name_without_extension_from_full_path(unisig_s98_packet.file_full_path),
                        "Number": unisig_s98_packet.number,
                        "class": unisig_s98_packet.__class__.__name__,
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
