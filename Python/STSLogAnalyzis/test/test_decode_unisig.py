import pytest

from typing import cast

from stsloganalyzis.ppn import ppn_log
from stsloganalyzis.unisig import decode_unisig, upper_layer_libraries
from common import bytes_messages


class TestDecodeUnisigCrc:

    class TestSrcSl4:

        def test_encore_checksum_32(self) -> None:

            data_to_encode = bytes_messages.convert_hex_string_to_hex_bytes("0Eh 7Fh 53h 21h 21h 03h 00h 00h 8Dh EFh CDh ABh 89h")
            expected_checksum = bytes_messages.convert_hex_string_to_hex_bytes("97h E4h C3h C1h 6Ah 30h")
            computed_checksum = decode_unisig.compute_crc_unisig_32(data_to_encode)
            assert expected_checksum == computed_checksum

        def test_encore_checksum_64(self) -> None:

            data_to_encode = bytes_messages.convert_hex_string_to_hex_bytes("0Eh 7Fh 53h 21h 21h 03h 00h 00h 8Dh EFh CDh ABh 89h")
            expected_checksum = bytes_messages.convert_hex_string_to_hex_bytes("97h E4h C3h C1h 6Ah 30h")
            computed_checksum = decode_unisig.compute_crc_unisig_64(data_to_encode)
            assert expected_checksum == computed_checksum
