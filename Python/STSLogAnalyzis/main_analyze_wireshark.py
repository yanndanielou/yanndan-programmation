from stsloganalyzis import decode_wireshark
from logger import logger_config

with logger_config.application_logger():

    dissector = decode_wireshark.PcapDissector(pcap_file=r"Input_for_tests/pcap/SAAT_1_LINE.pcapng")
    dissector.load_capture()
    dissector.print_packets_with_pretty_print()
    dissector.fill_dictionnary_for_each_packet()
    pass
