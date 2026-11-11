from common import bytes_messages, bytes_utils

from stsloganalyzis.ppn import ppn_profibus_log
from stsloganalyzis.unisig import upper_layer_libraries
from stsloganalyzis.unisig.s5758 import decode_unisig_s57_s58


class TestComputeUnisigCrc:

    class TestSrcSl4:

        class TestComputeChecksumFunction:

            def test_example_1_subset_57_sender_sl4_receiver_sl4(self) -> None:
                """10.2.1.2.1 Example 1: Sender: SIL 4 / Receiver: SIL 4 (based on the example in chapter 6.2.1.6)"""
                data_to_encode = bytes_messages.convert_hex_string_to_hex_bytes("0Eh 7Fh 53h 21h 21h 03h 00h 00h 8Dh EFh CDh ABh 89h")
                expected_checksum = bytes_messages.convert_hex_string_to_hex_bytes("97h E4h C3h C1h 6Ah 30h")
                computed_checksum_bytes = decode_unisig_s57_s58.crc48_unisig_s57_as_bytes(data_to_encode)
                assert expected_checksum == computed_checksum_bytes
                computed_checksum_str_base_16 = bytes_utils.byte_array_to_string_base_16(computed_checksum_bytes)
                expected_checksum_str_base_16 = bytes_utils.byte_array_to_string_base_16(expected_checksum)
                assert computed_checksum_str_base_16 == expected_checksum_str_base_16

        class TestRecomputedUnisigCrcClass:

            def test_idle_cycle(self) -> None:
                """10.2.1.2.1 Example 1: Sender: SIL 4 / Receiver: SIL 4 (based on the example in chapter 6.2.1.6)"""
                data_to_encode = bytes_messages.convert_hex_string_to_hex_bytes("0Eh 7Fh 53h 21h 21h 03h 00h 00h 8Dh EFh CDh ABh 89h")
                expected_checksum = bytes_messages.convert_hex_string_to_hex_bytes("97h E4h C3h C1h 6Ah 30h")
                computed_checksum_bytes = decode_unisig_s57_s58.crc48_unisig_s57_as_bytes(data_to_encode)
                assert expected_checksum == computed_checksum_bytes
                computed_checksum_str_base_16 = bytes_utils.byte_array_to_string_base_16(computed_checksum_bytes)
                expected_checksum_str_base_16 = bytes_utils.byte_array_to_string_base_16(expected_checksum)
                assert computed_checksum_str_base_16 == expected_checksum_str_base_16
