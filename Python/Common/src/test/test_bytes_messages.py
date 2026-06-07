import pytest

from common import bytes_messages


def test_decode_a() -> None:
    decoded_message = bytes_messages.DecodedBytesMessage("01 02 03 41 6E 74")
    assert decoded_message.get_next_bits_as_single_int_signed_and_unsigned(size_bits=8)[1] == 1
    assert decoded_message.get_next_bits_as_single_int_signed_and_unsigned(size_bits=8)[1] == 2
    assert decoded_message.get_next_bits_as_single_int_signed_and_unsigned(size_bits=8)[1] == 3
    assert decoded_message.get_next_bits_as_ascii_char(number_of_chars=3, size_bits_per_char=8) == "Ant"
