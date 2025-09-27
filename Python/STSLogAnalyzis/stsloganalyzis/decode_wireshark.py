import csv
import datetime
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, cast

import dpkt
from pcapng import FileScanner


from logger import logger_config

from stsloganalyzis import decode_action_set_content

# CONTENT_OF_FIELD_IN_CASE_OF_DECODING_ERROR = "!!! Decoding Error !!!"


@dataclass
class InvariantMessage:
    message_id: str
    message_number: int


def read_pcap_pcapng(pcap_path: str) -> None:
    with open(pcap_path, "rb") as fp:
        scanner = FileScanner(fp)
        block_number = 0
        for block in scanner:
            block_number += 1
            pass  # do something with the block...
        logger_config.print_and_log_info(f"block_number:  {block_number}")


def read_pcap_dpkt(pcap_path: str) -> None:

    counter = 0
    ipcounter = 0
    tcpcounter = 0
    udpcounter = 0

    for ts, pkt in dpkt.pcap.Reader(open(pcap_path, "r", encoding="utf-8")):

        counter += 1
        eth = dpkt.ethernet.Ethernet(pkt)
        if eth.type != dpkt.ethernet.ETH_TYPE_IP:
            continue

        ip = eth.data
        ipcounter += 1

        if ip.p == dpkt.ip.IP_PROTO_TCP:
            tcpcounter += 1

        if ip.p == dpkt.ip.IP_PROTO_UDP:
            udpcounter += 1

    logger_config.print_and_log_info(f"Total number of packets in the pcap file: {counter}")
    logger_config.print_and_log_info(f"Total number of ip packets: {ipcounter}")
    logger_config.print_and_log_info(f"Total number of tcp packets: {tcpcounter}")
    logger_config.print_and_log_info(f"Total number of udp packets:  {udpcounter}")


# read_pcap_dpkt("C:\\D_Drive\\temp\\tests_ar_ppn\\PAE PPN modif désactivation ar sur CAB 1A mais CAB2B intouchée.pcapng")
# read_pcap_dpkt(r"C:\D_Drive\temp\tests_ar_ppn\PAE PPN modif désactivation ar sur CAB 1A mais CAB2B intouchée.pcapng")
read_pcap_pcapng(r"C:\D_Drive\temp\tests_ar_ppn\PAE PPN modif désactivation ar sur CAB 1A mais CAB2B intouchée.pcapng")
