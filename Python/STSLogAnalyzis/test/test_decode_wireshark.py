import datetime

import pytest

from typing import cast

from stsloganalyzis import decode_wireshark


class TestDecodeWiresharkWithOnlyCbtc:
    def test_process_one_file(self) -> None:

        dissector = decode_wireshark.PcapDissector(pcap_file=r"Input_for_tests\pcap\2_trames_with_17_messages_each.pcapng")
        dissector.load_capture()
        dissector.fill_dictionnary_for_each_packet()

        pass
