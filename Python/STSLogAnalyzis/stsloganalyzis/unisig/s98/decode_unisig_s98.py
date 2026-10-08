from dataclasses import dataclass
from enum import IntEnum
from typing import cast

import pyshark
import pyshark.packet.packet

UNISIG_S98_PORTS = [49451, 49452, 49453, 49454, 49455, 49456, 49457]
UNISIG_TRANSPORT_LAYER = "TCP"


def convert_wireshark_string_colon_separated_bytes_to_byte_array(wireshark_string_column_separated_bytes: str) -> bytearray:
    bytes_as_list_of_int = [int("0x" + byte_str, 16) for byte_str in wireshark_string_column_separated_bytes.split(":")]
    return bytearray(bytes_as_list_of_int)


@dataclass
class RandomNumber:
    raw_str_value: str

    def __post_init__(self) -> None:
        self.as_byte_array = convert_wireshark_string_colon_separated_bytes_to_byte_array(self.raw_str_value)


class UnisigS98EtcsIdType(IntEnum):
    UNDEFINED_NEUTRAL = 0
    ETCS_ID_PRESENT = 1
    UNKNOWN_6 = 6


class UnisigS98PacketType(IntEnum):
    AU_1_AUTHENTICATION_1 = 1
    AU_2_AUTHENTICATION_2 = 2
    AU_3_AR_DT_DATA = 3
    DT_DATA_OR_RETRANSMISSION = 6


@dataclass
class UnisigS98WiresharkPacket:
    tcp_payload_str: str
    ip_dst_str: str
    ip_src_str: str
    ale_header: "UnisigS98WiresharkPacket.AleHeader"

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
class UnisigS98Au1WiresharkPacket(UnisigS98WiresharkPacket):
    calling_etcs_id_type: UnisigS98EtcsIdType
    calling_etcs_id: int
    called_etcs_id_type: UnisigS98EtcsIdType
    called_etcs_id: int
    random_number_b_rb: RandomNumber
    source_addr_str: str


@dataclass
class UnisigS98Au2WiresharkPacket(UnisigS98WiresharkPacket):
    responding_etcs_id_type: UnisigS98EtcsIdType
    responding_etcs_id: int
    random_number_a_ra: RandomNumber
    mac_str: int


def build_unisig_s98_packet_from_wireshark_packet(wireshark_packet: pyshark.packet.packet.Packet) -> UnisigS98WiresharkPacket:
    tcp_payload = wireshark_packet.tcp.payload

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

    if packet_type == UnisigS98PacketType.AU_1_AUTHENTICATION_1:
        return UnisigS98Au1WiresharkPacket(
            tcp_payload_str=tcp_payload,
            ip_dst_str=wireshark_packet.ip.dst,
            ip_src_str=wireshark_packet.ip.src,
            ale_header=ale_header,
            calling_etcs_id_type=UnisigS98EtcsIdType(int(wireshark_packet.ss098.get_field_value("ss098.conn.calling_ety"))),
            calling_etcs_id=int(wireshark_packet.ss098.get_field_value("ss098.conn.calling_id")),
            called_etcs_id_type=UnisigS98EtcsIdType(int(wireshark_packet.ss098.get_field_value("ss098.conn.called_ety"))),
            called_etcs_id=int(wireshark_packet.ss098.get_field_value("ss098.conn.called_id")),
            random_number_b_rb=RandomNumber(wireshark_packet.ss098.get_field_value("ss098.conn.rb")),
            source_addr_str=wireshark_packet.ss098.get_field_value("ss098.conn.source_addr"),
        )
    elif packet_type == UnisigS98PacketType.AU_2_AUTHENTICATION_2:
        return UnisigS98Au2WiresharkPacket(
            tcp_payload_str=tcp_payload,
            ip_dst_str=wireshark_packet.ip.dst,
            ip_src_str=wireshark_packet.ip.src,
            ale_header=ale_header,
            responding_etcs_id_type=UnisigS98EtcsIdType(int(wireshark_packet.ss098.get_field_value("ss098.conn.resp_ety"))),
            responding_etcs_id=int(wireshark_packet.ss098.get_field_value("ss098.conn.resp_id")),
            random_number_a_ra=RandomNumber(wireshark_packet.ss098.get_field_value("ss098.conn.ra")),
            mac_str=wireshark_packet.ss098.get_field_value("ss098.auth.mac"),
        )

    unisig_98_packet = UnisigS98WiresharkPacket(
        tcp_payload_str=tcp_payload,
        ip_dst_str=wireshark_packet.ip.dst,
        ip_src_str=wireshark_packet.ip.src,
        ale_header=ale_header,
    )

    return unisig_98_packet


def get_all_unisig_s98_packets_from_pcap(pcap_file_full_path: str, tshark_path: str = r"C:\Program Files\Wireshark") -> list[UnisigS98WiresharkPacket]:
    packets: list[UnisigS98WiresharkPacket] = []
    capture = pyshark.FileCapture(pcap_file_full_path, tshark_path=tshark_path)

    number_of_non_tcp_packets = 0

    for packet in capture:
        packet = cast(pyshark.packet.packet.Packet, packet)
        if packet.transport_layer == UNISIG_TRANSPORT_LAYER and int(packet.tcp.port) in UNISIG_S98_PORTS:

            packets.append(build_unisig_s98_packet_from_wireshark_packet(packet))
        else:
            number_of_non_tcp_packets += 1

    return packets
