import datetime
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stsloganalyzis.unisig import decode_unisig

from common import date_time_formats


def manual_additional_fields_decoding(upper_layer_stm: "decode_unisig.UpperLayerStm", field_name: str) -> None:
    if field_name.endswith("T_JD"):  # Timestamp en ms
        t_jd = upper_layer_stm.fields_names_and_values[field_name]
        assert isinstance(t_jd, int)
        upper_layer_stm.add_field(field_name + " human format", date_time_formats.format_duration_to_string(t_jd / 1000))

    if "NID_LIGNE_7" in field_name or "M_SW_VERSION_35" in field_name or "NID_UIC_9" in field_name or "NID_TRAIN_7" in field_name:
        decode_also_fields_as_string(upper_layer_stm, field_name)

    if field_name.endswith("TTS"):
        decode_also_fields_as_date_with_tts(upper_layer_stm, field_name)


def decode_also_fields_as_date_with_tts(upper_layer_stm: "decode_unisig.UpperLayerStm", date_tts_field_name: str) -> None:
    matched_regex = re.compile(r"(.*)(TTS)").match(date_tts_field_name)
    assert matched_regex is not None
    field_radical = matched_regex.group(1)
    assert isinstance(field_radical, str)

    year = upper_layer_stm.get_field_int_value_or_assert(field_radical + "YEAR") + 2000
    month = upper_layer_stm.get_field_int_value_or_assert(field_radical + "MONTH")
    day = upper_layer_stm.get_field_int_value_or_assert(field_radical + "DAY")
    hour = upper_layer_stm.get_field_int_value_or_assert(field_radical + "HOUR")
    minute = upper_layer_stm.get_field_int_value_or_assert(field_radical + "MINUTES")
    seconds = upper_layer_stm.get_field_int_value_or_assert(field_radical + "SECONDS")
    tts = upper_layer_stm.get_field_int_value_or_assert(date_tts_field_name)

    as_datetime = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=seconds, microsecond=tts * 10000)  # noqa: DTZ001
    upper_layer_stm.add_field(field_radical + "date", as_datetime)


def decode_also_fields_as_string(upper_layer_stm: "decode_unisig.UpperLayerStm", last_character_field_name: str) -> None:
    matched_regex = re.compile(r"(.*)(\d+)").match(last_character_field_name)
    assert matched_regex is not None
    field_radical = matched_regex.group(1)
    field_index = int(matched_regex.group(2))

    all_fields_as_one_string_value = ""
    for i in range(field_index + 1):
        field_i_name = f"{field_radical}{i}"
        field_i_value_int = upper_layer_stm.fields_names_and_values[field_i_name]
        assert isinstance(field_i_value_int, int)
        field_i_value_str = chr(field_i_value_int)
        all_fields_as_one_string_value += field_i_value_str

    all_fields_as_one_string_value = all_fields_as_one_string_value.lstrip("\x00")
    all_fields_as_one_string_value = all_fields_as_one_string_value.rstrip("_")
    upper_layer_stm.add_field(field_radical.rstrip("_"), all_fields_as_one_string_value)
