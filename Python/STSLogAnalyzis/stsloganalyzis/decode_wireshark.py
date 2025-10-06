import csv
import datetime
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, cast

import dpkt
from pcapng import FileScanner

import pyshark
import pyshark.packet.packet
import pyshark.packet.layers

from logger import logger_config

# CONTENT_OF_FIELD_IN_CASE_OF_DECODING_ERROR = "!!! Decoding Error !!!"


@dataclass
class InvariantMessage:
    message_id: str
    message_number: int


# Load the packet capture using the Lua dissector

import pyshark
from typing import List


class PcapDissector:
    def __init__(self, pcap_file: str, tshark_path: str = r"C:\Program Files\Wireshark"):
        self.pcap_file = pcap_file
        self.tshark_path = tshark_path
        self.capture = None

    def load_capture(self) -> None:
        """
        Loads the pcap file with the given Lua scripts using Tshark.
        """
        self.capture = pyshark.FileCapture(self.pcap_file, tshark_path=self.tshark_path)
        # self.capture = pyshark.FileCapture(self.pcap_file, tshark_path=r"C:\Program Files\Wireshark", custom_parameters={"-X": lua_script_params.strip()})

    def parse_packet(self, packet: pyshark.packet.packet.Packet) -> None:
        """
        Parses a packet and prints the layers and fields.
        """
        try:
            for layer in packet.layers:
                print(f"Layer: {layer.layer_name}")
                print(f"fields_names = {layer.field_names}")
                for field in layer.field_names:
                    print(f"    {field}: {getattr(layer, field)}")
        except AttributeError as e:
            print(f"An error occurred: {e}")

    def print_packets_with_pretty_print(self) -> None:

        if self.capture is None:
            raise ValueError("Capture not loaded. Call 'load_capture()' first.")

        for packet in self.capture:
            print(packet.pretty_print())

    def fill_dictionnary_for_each_packet(self) -> None:

        if self.capture is None:
            raise ValueError("Capture not loaded. Call 'load_capture()' first.")

        for packet in self.capture:

            for layer in packet.layers:
                all_fields_with_alternates = layer._get_all_fields_with_alternates()

                for field in all_fields_with_alternates:
                    field_key = field.showname_key
                    field_value = field.showname_value
                    print(f"layer {layer.layer_name}, {field_key} = {field_value}")

    def process_packets(self) -> None:
        """
        Processes all packets in the capture to extract and display data.
        """

        if self.capture is None:
            raise ValueError("Capture not loaded. Call 'load_capture()' first.")

        for packet in self.capture:
            self.parse_packet(packet)
            self.parse_wcn_packet(packet)

        self.capture.close()

    def parse_wcn_packet(self, packet: pyshark.packet.packet.Packet) -> None:
        wcn_layer = packet.wcn
        all_fields = wcn_layer._all_fields
        all_fields_with_alternates = wcn_layer._get_all_fields_with_alternates()
        number_of_fields = len(all_fields_with_alternates)

        for field in all_fields_with_alternates:
            field_key = field.showname_key
            field_value = field.showname_value
            logger_config.print_and_log_info(f"{field_key} = {field_value}")
            # print(field)

        pass


def read_pcap_pcapng(pcap_path: str) -> None:
    with open(pcap_path, "rb") as fp:
        scanner = FileScanner(fp)
        block_number = 0
        for block in scanner:
            print(block)
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
# read_pcap_pcapng(r"C:\D_Drive\temp\tests_ar_ppn\PAE PPN modif désactivation ar sur CAB 1A mais CAB2B intouchée.pcapng")
# read_pcap_pcapng(r"C:\D_Drive\temp\tests_ar_ppn\PAE PPN modif désactivation ar sur CAB 1A mais CAB2B intouchée.pcapng")
