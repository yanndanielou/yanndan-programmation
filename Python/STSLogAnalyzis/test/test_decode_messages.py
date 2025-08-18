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


class TestDecodeSimpleFakeMessages:

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
        assert not decoded_message.not_decoded_because_error_fields_names
        assert decoded_message.is_correctly_and_completely_decoded()
        for i in range(0, 8):
            assert decoded_message.decoded_fields_flat_directory[f"TheBitField{i}"] == bits_expected_values[i], f"failed for i:{i}"

    @pytest.mark.parametrize("hexa_content, int_expected_value", [("01", 1), ("02", 2), ("10", 16)])
    def test_message_with_only_one_int_field(self, hexa_content: str, int_expected_value: int) -> None:
        hexa_content_as_str = hexa_content
        xml_message_decoder = decode_message.XmlMessageDecoder(xml_directory_path=r"Input_for_tests\Xml")
        decoded_message = xml_message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=999, hexadecimal_content=hexa_content_as_str)
        assert decoded_message
        assert not decoded_message.not_decoded_because_error_fields_names
        assert decoded_message.is_correctly_and_completely_decoded()
        assert decoded_message.decoded_fields_flat_directory["TheOnlyField"] == int_expected_value

    @pytest.mark.parametrize("hexa_content, first_field_int_expected_value,second_field_int_expected_value", [("01 02", 1, 2), ("00 00", 0, 0), ("04 03", 4, 3)])
    def test_message_with_only_two_int_fields(self, hexa_content: str, first_field_int_expected_value: int, second_field_int_expected_value: int) -> None:
        hexa_content_as_str = hexa_content
        xml_message_decoder = decode_message.XmlMessageDecoder(xml_directory_path=r"Input_for_tests\Xml")
        decoded_message = xml_message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=998, hexadecimal_content=hexa_content_as_str)
        assert decoded_message
        assert not decoded_message.not_decoded_because_error_fields_names
        assert decoded_message.is_correctly_and_completely_decoded()
        assert decoded_message.decoded_fields_flat_directory["TheFirstField"] == first_field_int_expected_value
        assert decoded_message.decoded_fields_flat_directory["TheSecondField"] == second_field_int_expected_value

    @pytest.mark.parametrize("hexa_content, expected_value", [("61 62", "ab")])
    def test_message_with_only_one_string_field(self, hexa_content: str, expected_value: str) -> None:
        hexa_content_as_str = hexa_content
        xml_message_decoder = decode_message.XmlMessageDecoder(xml_directory_path=r"Input_for_tests\Xml")
        decoded_message = xml_message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=997, hexadecimal_content=hexa_content_as_str)
        assert decoded_message
        assert decoded_message.is_correctly_and_completely_decoded()
        assert not decoded_message.not_decoded_because_error_fields_names
        assert decoded_message.decoded_fields_flat_directory["TheStringField"] == expected_value


class TestDecodeCbtcMessageswithRecordWithDimension:

    message_205_hexa_content_as_str = "01 00 20 00 0F 00 F0 00 00 50 04 00 A0 00 00 00 00 00 00 00 00 0F 00 00 00 00 00 00 00 00 00 00 00 00 01 42 01 42 01 01 01 01 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 40 00 06 F0 E9 00 01 19 40 27 FC"
    xml_message_decoder = decode_message.XmlMessageDecoder(xml_directory_path=r"D:\NEXT\Data\Xml")

    def test_message_is_completely_read(self) -> None:
        decoded_message = self.xml_message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=205, hexadecimal_content=self.message_205_hexa_content_as_str)
        assert decoded_message
        assert decoded_message.is_correctly_and_completely_decoded()

    def test_fields_after_record_are_correctly_read_without_decalage(self) -> None:
        decoded_message = self.xml_message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=205, hexadecimal_content=self.message_205_hexa_content_as_str)
        assert decoded_message
        assert not decoded_message.not_decoded_because_error_fields_names
        assert decoded_message.is_correctly_and_completely_decoded()
        assert decoded_message.decoded_fields_flat_directory["UtoTrainReversingMode"] == 4
        assert decoded_message.decoded_fields_flat_directory["TimeOffset"] == 72000

    def test_access_fields_inside_record_by_field_name_and_index(self) -> None:
        decoded_message = self.xml_message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=205, hexadecimal_content=self.message_205_hexa_content_as_str)
        assert decoded_message
        assert not decoded_message.not_decoded_because_error_fields_names
        assert decoded_message.is_correctly_and_completely_decoded()
        assert isinstance(decoded_message.all_fields_by_name["TvdArb"], list)
        assert decoded_message.all_fields_by_name["TvdArb"]
        assert len(decoded_message.all_fields_by_name["TvdArb"]) == 250
        assert decoded_message.all_fields_by_name["TvdArb"][0].value == 0
        assert decoded_message.all_fields_by_name["TvdArb"][6].value == 1
        assert decoded_message.all_fields_by_name["TvdArb"][12].value == 1
        assert decoded_message.all_fields_by_name["TvdArb"][13].value == 0

    def test_access_fields_inside_record_by_record_index_and_field_name(self) -> None:
        decoded_message = self.xml_message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=205, hexadecimal_content=self.message_205_hexa_content_as_str)
        assert decoded_message
        assert not decoded_message.not_decoded_because_error_fields_names
        assert decoded_message.is_correctly_and_completely_decoded()
        assert isinstance(decoded_message.all_records_by_name["TvdOpData"], list)
        assert decoded_message.all_records_by_name["TvdOpData"]
        assert len(decoded_message.all_records_by_name["TvdOpData"]) == 250
        assert isinstance(decoded_message.all_records_by_name["TvdOpData"][0].all_fields_unit_by_name["TvdArb"], decode_message.DecodedMessage.XmlMessageFieldInt)
        assert decoded_message.all_records_by_name["TvdOpData"][0].all_fields_unit_by_name["TvdArb"].value == 0
        assert isinstance(decoded_message.all_records_by_name["TvdOpData"][6].all_fields_unit_by_name["TvdArb"], decode_message.DecodedMessage.XmlMessageFieldInt)
        assert decoded_message.all_records_by_name["TvdOpData"][6].all_fields_unit_by_name["TvdArb"].value == 1
        assert isinstance(decoded_message.all_records_by_name["TvdOpData"][12].all_fields_unit_by_name["TvdArb"], decode_message.DecodedMessage.XmlMessageFieldInt)
        assert decoded_message.all_records_by_name["TvdOpData"][12].all_fields_unit_by_name["TvdArb"].value == 1
        assert isinstance(decoded_message.all_records_by_name["TvdOpData"][13].all_fields_unit_by_name["TvdArb"], decode_message.DecodedMessage.XmlMessageFieldInt)
        assert decoded_message.all_records_by_name["TvdOpData"][13].all_fields_unit_by_name["TvdArb"].value == 0


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
