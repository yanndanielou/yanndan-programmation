import datetime

import pytest

import decode_message

# fmt: off

# time_field_value: int, time_offset_value: int, decade_field_value: int, day_on_decade_field_value: int, expected_datetime: datetime.datetime
decode_hlf_test_data = [
    (0, 0, 0, 0, datetime.datetime(year=2000, month=1, day=1, hour=0, minute=0, second=0)),
    (0, 0, 1, 0, datetime.datetime(year=2010, month=1, day=1, hour=0, minute=0, second=0)),
    (0, 0, 1, 1, datetime.datetime(year=2010, month=1, day=2, hour=0, minute=0, second=0)),
    (0, 0, 1, 40, datetime.datetime(year=2010, month=2, day=10, hour=0, minute=0, second=0)),
]
# fmt: on


class TestDecodeHlfFieldsToDatetime:
    def test_0(self) -> None:
        decoded_datetime = decode_message.MessageDecoder(xml_directory_path="D:/RIYL1/Data/Xml").decode_hlf_fields_to_datetime(
            time_field_value=0, time_offset_value=0, decade_field_value=0, day_on_decade_field_value=0
        )
        assert decode_message.MessageDecoder.decode_hlf_fields_to_datetime(time_field_value=0, time_offset_value=0, decade_field_value=0, day_on_decade_field_value=0) == datetime.datetime(
            year=2000, month=1, day=1, hour=0, minute=0, second=0
        )

    @pytest.mark.parametrize("time_field_value, time_offset_value,decade_field_value, day_on_decade_field_value, expected_datetime", decode_hlf_test_data)
    def test_several_data(self, time_field_value: int, time_offset_value: int, decade_field_value: int, day_on_decade_field_value: int, expected_datetime: datetime.datetime) -> None:

        decoded_hlf = decode_message.MessageDecoder.decode_hlf_fields_to_datetime(
            time_field_value=time_field_value, time_offset_value=time_offset_value, decade_field_value=decade_field_value, day_on_decade_field_value=day_on_decade_field_value
        )
        assert decoded_hlf == expected_datetime, str(decoded_hlf)
