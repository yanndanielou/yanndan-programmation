from enum import IntEnum
from dataclasses import dataclass
from stsloganalyzis.unisig.s98 import triple_des_s98, secret_kmac_keys
from typing import cast
import pyshark.packet.packet
import pyshark

UNISIG_S98_PORTS = [49451, 49452, 49453, 49454, 49455, 49456, 49457]
UNISIG_TRANSPORT_LAYER = "TCP"


class UnisigS98EtcsIdType(IntEnum):
    UNDEFINED_NEUTRAL = 0
    ETCS_ID_PRESENT = 1


class UnisigS98PacketType(IntEnum):
    AU_1_AUTHENTICATION_1 = 1
    AU_2_AUTHENTICATION_2 = 2
    AU_3_AR_DT_DATA = 3
    DT_DATA_OR_RETRANSMISSION = 6


@dataclass
class UnisigS98Packet:
    tcp_payload_str: str
    ip_dst_str: str
    ip_src_str: str
    ale_header: "UnisigS98Packet.AleHeader"

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
class UnisigS98Au1Packet(UnisigS98Packet):
    calling_etcs_id_type: UnisigS98EtcsIdType
    calling_etcs_id: int
    called_etcs_id_type: UnisigS98EtcsIdType
    called_etcs_id: int
    random_number_a_ra: int


def build_unisig_s98_packet_from_wireshark_packet(wireshark_packet: pyshark.packet.packet.Packet) -> UnisigS98Packet:
    tcp_payload = wireshark_packet.tcp.payload

    packet_type = UnisigS98PacketType(int(wireshark_packet.ss098.ale.packet_type))

    ale_header = UnisigS98Packet.AleHeader(
        length=int(wireshark_packet.ss098.ale.length),
        version_hexa_str=wireshark_packet.ss098.ale.version,
        apptype_hexa_str=wireshark_packet.ss098.ale.apptype,
        tsn=int(wireshark_packet.ss098.ale.tsn),
        nr_flag_hexa_str=wireshark_packet.ss098.ale.nr_flag,
        packet_type=packet_type,
        checksum_hexa_str=wireshark_packet.ss098.ale.checksum_hexa_str,
    )

    if packet_type == UnisigS98PacketType.AU_1_AUTHENTICATION_1:
        return UnisigS98Au1Packet(
            tcp_payload_str=tcp_payload,
            ip_dst_str=wireshark_packet.ip.dst,
            ip_src_str=wireshark_packet.ip.src,
            ale_header=ale_header,
            calling_etcs_id_type=UnisigS98EtcsIdType(int(wireshark_packet.ss098.conn.calling_ety)),
            calling_etcs_id=int(wireshark_packet.ss098.conn.calling_id),
            called_etcs_id_type=UnisigS98EtcsIdType(int(wireshark_packet.ss098.conn.called_ety)),
            called_etcs_id=int(wireshark_packet.ss098.conn.called_id),
            random_number_a_ra=int(wireshark_packet.ss098.conn.ra),
        )

    unisig_98_packet = UnisigS98Packet(
        tcp_payload_str=tcp_payload,
        ip_dst_str=wireshark_packet.ip.dst,
        ip_src_str=wireshark_packet.ip.src,
        ale_header=ale_header,
    )

    return unisig_98_packet


def get_all_unisig_s98_packets_from_pcap(pcap_file_full_path: str, tshark_path: str = r"C:\Program Files\Wireshark") -> list[UnisigS98Packet]:
    packets: list[UnisigS98Packet] = []
    capture = pyshark.FileCapture(pcap_file_full_path, tshark_path=tshark_path)

    number_of_non_tcp_packets = 0

    for packet in capture:
        packet = cast(pyshark.packet.packet.Packet, packet)
        if packet.transport_layer == UNISIG_TRANSPORT_LAYER and int(packet.tcp.port) in UNISIG_S98_PORTS:

            packets.append(build_unisig_s98_packet_from_wireshark_packet(packet))
        else:
            number_of_non_tcp_packets += 1

    return packets
