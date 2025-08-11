import datetime

import pytest

from typing import List

from stsloganalyzis import decode_message

# fmt: off

# time_field_value: int, time_offset_value: int, decade_field_value: int, day_on_decade_field_value: int, expected_datetime: datetime.datetime
decode_hlf_test_data = [
    (0, 0, 0, 0, datetime.datetime(year=2000, month=1, day=1, hour=0, minute=0, second=0)),
    (0, 0, 1, 0, datetime.datetime(year=2010, month=1, day=1, hour=0, minute=0, second=0)),
    (0, 0, 1, 1, datetime.datetime(year=2010, month=1, day=2, hour=0, minute=0, second=0)),
    (0, 0, 1, 40, datetime.datetime(year=2010, month=2, day=10, hour=0, minute=0, second=0)),
]
# fmt: on


class TestDecodeTestMessages:

    @pytest.mark.parametrize(
        "hexa_content, bits_expected_values",
        [
            ("00", [0, 0, 0, 0, 0, 0, 0, 0]),
            ("80", [1, 0, 0, 0, 0, 0, 0, 0]),
            ("01", [0, 0, 0, 0, 0, 0, 0, 1]),
        ],
    )
    def test_message_with_only_8_bit_fields(self, hexa_content: str, bits_expected_values: List[int]) -> None:
        hexa_content_as_str = hexa_content
        xml_message_decoder = decode_message.XmlMessageDecoder(xml_directory_path=r"Input_for_tests\Xml")
        decoded_message = xml_message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=996, hexadecimal_content=hexa_content_as_str)
        assert decoded_message
        for i in range(0, 8):
            assert decoded_message.decoded_fields_flat_directory[f"TheBitField{i}"] == bits_expected_values[i], f"failed for i:{i}"

    @pytest.mark.parametrize("hexa_content, int_expected_value", [("01", 1), ("02", 2), ("10", 16)])
    def test_message_with_only_one_int_field(self, hexa_content: str, int_expected_value: int) -> None:
        hexa_content_as_str = hexa_content
        xml_message_decoder = decode_message.XmlMessageDecoder(xml_directory_path=r"Input_for_tests\Xml")
        decoded_message = xml_message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=999, hexadecimal_content=hexa_content_as_str)
        assert decoded_message
        assert decoded_message.decoded_fields_flat_directory["TheOnlyField"] == int_expected_value

    @pytest.mark.parametrize("hexa_content, first_field_int_expected_value,second_field_int_expected_value", [("01 02", 1, 2), ("00 00", 0, 0), ("04 03", 4, 3)])
    def test_message_with_only_two_int_fields(self, hexa_content: str, first_field_int_expected_value: int, second_field_int_expected_value: int) -> None:
        hexa_content_as_str = hexa_content
        xml_message_decoder = decode_message.XmlMessageDecoder(xml_directory_path=r"Input_for_tests\Xml")
        decoded_message = xml_message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=998, hexadecimal_content=hexa_content_as_str)
        assert decoded_message
        assert decoded_message.decoded_fields_flat_directory["TheFirstField"] == first_field_int_expected_value
        assert decoded_message.decoded_fields_flat_directory["TheSecondField"] == second_field_int_expected_value

    @pytest.mark.parametrize("hexa_content, expected_value", [("61 62", "ab")])
    def test_message_with_only_one_string_field(self, hexa_content: str, expected_value: str) -> None:
        hexa_content_as_str = hexa_content
        xml_message_decoder = decode_message.XmlMessageDecoder(xml_directory_path=r"Input_for_tests\Xml")
        decoded_message = xml_message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=997, hexadecimal_content=hexa_content_as_str)
        assert decoded_message
        assert decoded_message.decoded_fields_flat_directory["TheStringField"] == expected_value


class TestDecodeCbtcMessages:
    def test_message_with_record_with_dimension(self) -> None:
        hexa_content_as_str = "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 42 01 42 01 01 01 01 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 40 00 06 F0 E9 00 01 19 40 27 FC"

        xml_message_decoder = decode_message.XmlMessageDecoder(xml_directory_path=r"D:\NEXT\Data\Xml")
        decoded_message = xml_message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=205, hexadecimal_content=hexa_content_as_str)
        assert decoded_message
        assert decoded_message.decoded_fields_flat_directory["UtoTrainReversingMode"] == 4
        assert decoded_message.decoded_fields_flat_directory["TimeOffset"] == 72000


class TestDecodeHlf:
    def test_0(self) -> None:
        assert decode_message.HLFDecoder.decode_hlf_fields_to_datetime(time_field_value=0, time_offset_value=0, decade_field_value=0, day_on_decade_field_value=0) == datetime.datetime(
            year=2000, month=1, day=1, hour=0, minute=0, second=0
        )

    @pytest.mark.parametrize("time_field_value, time_offset_value,decade_field_value, day_on_decade_field_value, expected_datetime", decode_hlf_test_data)
    def test_several_data(self, time_field_value: int, time_offset_value: int, decade_field_value: int, day_on_decade_field_value: int, expected_datetime: datetime.datetime) -> None:

        decoded_hlf = decode_message.HLFDecoder.decode_hlf_fields_to_datetime(
            time_field_value=time_field_value, time_offset_value=time_offset_value, decade_field_value=decade_field_value, day_on_decade_field_value=day_on_decade_field_value
        )
        assert decoded_hlf == expected_datetime, str(decoded_hlf)
