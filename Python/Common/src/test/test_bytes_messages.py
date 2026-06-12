import pytest

from common import bytes_messages


def test_decode_byte_message() -> None:
    decoded_message = bytes_messages.DecodedBytesMessage("01 02 03 04 FF 41 00 AA 41 6E 74")

    # 01
    assert decoded_message.get_next_byte_as_single_int_unsigned() == 1

    # 02
    assert decoded_message.get_next_bits_as_single_int_signed_and_unsigned(size_bits=8).unsigned_value == 2

    # 03 04
    assert decoded_message.get_next_bytes_as_single_int_unsigned(size_bytes=2) == 772

    # FF
    assert decoded_message.get_next_bits_as_single_int_signed_and_unsigned(size_bits=8).signed_value == -1

    # 41
    assert not decoded_message.get_next_bits_as_bool_0_or_1(size_bits=1)
    assert decoded_message.get_next_bits_as_single_int_signed(size_bits=3) == -4

    assert decoded_message.get_next_bits_as_single_int_signed(size_bits=1) == 0
    assert decoded_message.get_next_bits_as_bool_0_or_1(size_bits=3)

    # 00
    assert not decoded_message.get_next_bits_as_bool_0_or_1(size_bits=8)

    assert not decoded_message.is_correctly_and_completely_decoded()

    # AA
    assert decoded_message.get_next_bits_as_int_table_signed_and_unsigned(table_dim=2, size_bits=1)[0] == bytes_messages.DecodedIntResult(-1, 1)
    assert decoded_message.get_next_bits_as_int_table_signed_and_unsigned(table_dim=1, size_bits=2)[0] == bytes_messages.DecodedIntResult(-2, 2)
    assert decoded_message.get_next_bits_as_int_table_signed_and_unsigned(table_dim=2, size_bits=2)[0] == bytes_messages.DecodedIntResult(-2, 2)

    # 41 6E 74
    assert decoded_message.get_next_bits_as_ascii_char(number_of_chars=3, size_bits_per_char=8) == "Ant"
    assert decoded_message.is_correctly_and_completely_decoded()


def test_decode_bits_message() -> None:
    decoded_message = bytes_messages.DecodedBitsMessage("01110101")
    pass
