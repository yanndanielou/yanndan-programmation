from dataclasses import dataclass
from typing import List, cast, Self

NUMBER_OF_BITS_IN_BYTE = int(8)


@dataclass
class DecodedIntResult:
    signed_value: int
    unsigned_value: int


def extract_bits_of_bytes_to_bytes(data: bytes, start_bit: int, number_of_bits: int) -> bytes:
    # logger_config.print_and_log_info(f"data length:{len(data)}, start_bit:{start_bit},number_of_bits:{number_of_bits},")
    start_byte = start_bit // 8
    end_bit = start_bit + number_of_bits
    end_byte = (end_bit + 7) // 8

    # Get the relevant bytes
    relevant_bytes = data[start_byte:end_byte]
    return relevant_bytes


def convert_bytes_to_to_str_of_bit(to_convert: bytes) -> str:
    combined_bits = "".join(f"{byte:08b}" for byte in to_convert)
    return combined_bits


def extract_bits_of_bytes_to_str_of_bit(data: bytes, start_bit: int, number_of_bits: int) -> str:
    """Extract a specific number of bits starting at a given bit index from a list of bytes."""
    relevant_bytes = extract_bits_of_bytes_to_bytes(data=data, start_bit=start_bit, number_of_bits=number_of_bits)
    combined_bits = convert_bytes_to_to_str_of_bit(relevant_bytes)
    return combined_bits


def convert_bits_to_ascii_char(combined_bits: str, start_bit: int, number_of_bits: int) -> str:
    # Extract the substring of the combined bits and convert to an integer
    result_int = convert_bits_to_unsigned_int(combined_bits=combined_bits)
    return chr(result_int)


def convert_bits_to_signed_and_unsigned_int(combined_bits: str) -> DecodedIntResult:

    return DecodedIntResult(
        signed_value=convert_bits_to_signed_int(combined_bits=combined_bits),
        unsigned_value=convert_bits_to_unsigned_int(combined_bits=combined_bits),
    )


def convert_bits_to_unsigned_int(combined_bits: str) -> int:
    # Extract the substring of the combined bits and convert to an integer
    return int(combined_bits, 2)


def convert_bits_to_signed_int(combined_bits: str) -> int:
    # Extract the substring of the combined bits and convert to a signed integer
    number_of_bits = len(combined_bits)
    value = int(combined_bits, 2)
    if value >= (1 << (number_of_bits - 1)):
        value -= 1 << number_of_bits
    return value


class DecodedBytesMessage:
    __key_to_protect_constructor = object()

    def __init__(self, key: object, str_of_bits: str) -> None:
        assert key == DecodedBytesMessage.__key_to_protect_constructor, "Class must be instanciated from classmethods"
        self.current_bit_index = 0
        self.str_of_bits = str_of_bits
        self.total_length_in_bits = len(self.str_of_bits)

    @classmethod
    def from_hex_string(cls, hex_string: str) -> Self:
        hex_bytes = bytes.fromhex(hex_string.replace(" ", ""))
        return cls.from_bytes(hex_bytes)

    @classmethod
    def from_bit_string(cls, str_of_bits: str) -> Self:
        return cls(key=cls.__key_to_protect_constructor, str_of_bits=str_of_bits)

    @classmethod
    def from_bytes(cls, hex_bytes: bytes) -> Self:
        str_of_bit = convert_bytes_to_to_str_of_bit(hex_bytes)
        return cls.from_bit_string(str_of_bit)

    @property
    def number_of_bits_remaining_to_decode(self) -> int:
        return self.total_length_in_bits - self.current_bit_index

    def extract_next_bits_to_str_of_bit(self, number_of_bits: int) -> str:
        bits_extracted = self.str_of_bits[self.current_bit_index : self.current_bit_index + number_of_bits]
        self.current_bit_index += number_of_bits
        assert self.number_of_bits_remaining_to_decode >= 0, f"Too many ({-self.current_bit_index}) bits decoded!!"
        return bits_extracted

    def get_next_bits_as_ascii_char(self, number_of_chars: int) -> str:
        all_chars: List[str] = []

        size_bits_per_char = 8

        for _ in range(0, number_of_chars):
            bits_extracted = self.extract_next_bits_to_str_of_bit(size_bits_per_char)
            current_char = convert_bits_to_ascii_char(bits_extracted, self.current_bit_index, size_bits_per_char)
            all_chars.append(current_char)

        string_value = "".join(cast(str, all_chars)).rstrip()

        return string_value

    def get_next_bits_as_bitset_str(self, size_bits: int) -> str:
        bits_extracted = self.extract_next_bits_to_str_of_bit(size_bits)
        return bits_extracted

    def get_next_bits_as_single_int_signed_and_unsigned(self, size_bits: int) -> DecodedIntResult:
        bits_extracted = self.extract_next_bits_to_str_of_bit(size_bits)
        return convert_bits_to_signed_and_unsigned_int(bits_extracted)

    def get_next_bits_as_single_int_signed(self, size_bits: int) -> int:
        return self.get_next_bits_as_single_int_signed_and_unsigned(size_bits).signed_value

    def get_next_byte_as_single_int_unsigned(self) -> int:
        return self.get_next_bytes_as_single_int_unsigned(size_bytes=1)

    def get_next_bytes_as_single_int_unsigned(self, size_bytes: int) -> int:
        return self.get_next_bits_as_single_int_unsigned(size_bytes * NUMBER_OF_BITS_IN_BYTE)

    def get_next_bits_as_single_int_unsigned(self, size_bits: int) -> int:
        return self.get_next_bits_as_single_int_signed_and_unsigned(size_bits).unsigned_value

    def get_next_bits_as_bool_0_or_1(self, size_bits: int) -> bool:
        as_int = self.get_next_bits_as_single_int_unsigned(size_bits)
        assert as_int in [0, 1], f"Unsupported bool with value {as_int}"
        return as_int == 1

    def get_next_bits_as_int_table_signed_and_unsigned(self, table_dim: int, size_bits: int) -> List[DecodedIntResult]:
        all_values: List[DecodedIntResult] = []

        for _ in range(0, table_dim):
            bits_extracted = self.extract_next_bits_to_str_of_bit(size_bits)
            field_unsigned_value = convert_bits_to_unsigned_int(bits_extracted)

            field_signed_value = convert_bits_to_signed_int(bits_extracted)
            all_values.append(DecodedIntResult(signed_value=field_signed_value, unsigned_value=field_unsigned_value))

        return all_values

    def is_correctly_and_completely_decoded(self) -> bool:
        return self.number_of_bits_remaining_to_decode == 0
