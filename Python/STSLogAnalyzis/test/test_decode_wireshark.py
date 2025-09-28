import datetime

import pytest

from typing import cast

from stsloganalyzis import decode_wireshark


class TestDecodeWiresharkWithOnlyCbtc:
    def test_process_one_file(self) -> None:

        decode_wireshark.read_pcap_pcapng(r"Input_for_tests\pcap\2_trames_with_17_messages_each.pcapng")

        pass
