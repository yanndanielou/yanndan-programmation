from common import bytes_messages

from stsloganalyzis.unisig import decode_unisig, upper_layer_libraries


class TestUpperLayerLibrary:

    def tests_upper_layer_library_packet_field_containing_fields(self) -> None:
        upper_layer_decoding_library = upper_layer_libraries.UpperLayerDecodingLibrary.from_next_json_file_full_path(r"test\resources\ppn\upper_layer_library_packet_field_containing_fields.json")

        data_to_encode = bytes_messages.convert_hex_string_to_hex_bytes("7Bh 89h 34h 53h 01h 02h 03h 04h 05h 06h 07h 08h 09h 10h")
        telegram = decode_unisig.UpperLayerTelegram(
            safety_level=decode_unisig.SafetyLevel.SL4,
            telegram_name="",
            byte_message_decoded=bytes_messages.DecodedBytesMessage.from_hex_string("34h 53h 01h 02h 03h 04h 05h 06h 07h 08h 09h 10h"),
            lowest_order_byte_sequence_number=12,
            command_type=decode_unisig.SdaUnisigMessage.CommandTypeSubset57.SL4_TELEGRAM_FOR_UPPER_LAYER,
            upper_layer_decoding_library=upper_layer_decoding_library,
        )


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
