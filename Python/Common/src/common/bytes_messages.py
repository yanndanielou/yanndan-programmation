from dataclasses import dataclass
from typing import Self, cast

NUMBER_OF_BITS_IN_BYTE = int(8)
SIZE_BITS_PER_CHAR = 8


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


def convert_hex_string_to_hex_bytes(hex_string: str) -> bytes:
    valid_hex_string = hex_string.replace("0x", "").replace("h", "").replace(" ", "")
    hex_bytes = bytes.fromhex(valid_hex_string)
    return hex_bytes


class DecodedBytesMessage:
    __key_to_protect_constructor = object()

    def __init__(self, constructor_secret_key: object, str_of_bits: str) -> None:
        assert constructor_secret_key == DecodedBytesMessage.__key_to_protect_constructor, "Class must be instanciated from classmethods"
        self.current_bit_index = 0
        self.str_of_bits = str_of_bits

    @property
    def total_length_in_bits(self) -> int:
        return len(self.str_of_bits)

    @classmethod
    def from_hex_string(cls, hex_string: str) -> Self:
        return cls.from_bytes(convert_hex_string_to_hex_bytes(hex_string))

    @classmethod
    def from_bit_string(cls, str_of_bits: str) -> Self:
        str_of_bits = str_of_bits.replace(" ", "")
        return cls(constructor_secret_key=cls.__key_to_protect_constructor, str_of_bits=str_of_bits)

    @classmethod
    def from_bytes(cls, hex_bytes: bytes) -> Self:
        str_of_bit = convert_bytes_to_to_str_of_bit(hex_bytes)
        return cls.from_bit_string(str_of_bit)

    @classmethod
    def from_bytes_as_list_int(cls, bytes_as_list_int: list[int]) -> Self:
        hex_string = ""
        for byte_as_int in bytes_as_list_int:
            if hex_string != "":
                hex_string += " "

            byte_as_hex = hex(byte_as_int)
            byte_as_hex_without_prefix = byte_as_hex.replace("0x", "")
            if len(byte_as_hex_without_prefix) == 1:
                byte_as_hex_without_prefix = "0" + byte_as_hex_without_prefix
            hex_string += "0x" + byte_as_hex_without_prefix

        return cls.from_hex_string(hex_string)

    @property
    def number_of_bits_remaining_to_decode(self) -> int:
        return self.total_length_in_bits - self.current_bit_index

    def extract_next_bits_to_str_of_bit(self, number_of_bits: int) -> str:
        assert self.current_bit_index + number_of_bits <= self.total_length_in_bits, f"Try to extract {number_of_bits} but only {self.number_of_bits_remaining_to_decode} remain"
        bits_extracted = self.str_of_bits[self.current_bit_index : self.current_bit_index + number_of_bits]
        self.current_bit_index += number_of_bits
        assert self.number_of_bits_remaining_to_decode >= 0, f"Too many ({-self.current_bit_index}) bits decoded!!"
        return bits_extracted

    def extract_next_bytes_to_str_of_bit(self, size_bytes: int) -> str:
        return self.extract_next_bits_to_str_of_bit(size_bytes * NUMBER_OF_BITS_IN_BYTE)

    def extract_and_remove_last_next_bits_to_str_of_bit(self, number_of_bits: int) -> str:
        bits_extracted = self.str_of_bits[-number_of_bits:]
        self.str_of_bits = self.str_of_bits[:-number_of_bits]
        assert self.number_of_bits_remaining_to_decode >= 0, f"Too many ({-self.current_bit_index}) bits decoded!!"
        return bits_extracted

    def get_next_bits_as_ascii_char(self, number_of_chars: int) -> str:
        all_chars: list[str] = []

        for _ in range(0, number_of_chars):
            bits_extracted = self.extract_next_bits_to_str_of_bit(SIZE_BITS_PER_CHAR)
            current_char = convert_bits_to_ascii_char(bits_extracted, self.current_bit_index, SIZE_BITS_PER_CHAR)
            all_chars.append(current_char)

        string_value = "".join(cast(str, all_chars)).rstrip()

        return string_value

    def get_remaining_bits_as_str_of_bit(self) -> str:
        return self.extract_next_bits_to_str_of_bit(self.number_of_bits_remaining_to_decode) if self.number_of_bits_remaining_to_decode else ""

    def get_remaining_bits_as_unsigned_int(self) -> int:
        return self.get_next_bits_as_single_int_unsigned(size_bits=self.number_of_bits_remaining_to_decode)

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

    def get_next_bits_as_int_table_signed_and_unsigned(self, table_dim: int, size_bits: int) -> list[DecodedIntResult]:
        all_values: list[DecodedIntResult] = []

        for _ in range(0, table_dim):
            bits_extracted = self.extract_next_bits_to_str_of_bit(size_bits)
            field_unsigned_value = convert_bits_to_unsigned_int(bits_extracted)

            field_signed_value = convert_bits_to_signed_int(bits_extracted)
            all_values.append(DecodedIntResult(signed_value=field_signed_value, unsigned_value=field_unsigned_value))

        return all_values

    def get_and_remove_last_bytes_as_bitset_str(self, size_bytes: int) -> str:
        bits_extracted = self.get_and_remove_last_bits_as_bitset_str(size_bytes * NUMBER_OF_BITS_IN_BYTE)
        return bits_extracted

    def get_and_remove_last_bits_as_bitset_str(self, size_bits: int) -> str:
        bits_extracted = self.extract_and_remove_last_next_bits_to_str_of_bit(size_bits)
        return bits_extracted

    def get_and_remove_last_bits_as_single_int_signed_and_unsigned(self, size_bits: int) -> DecodedIntResult:
        bits_extracted = self.extract_and_remove_last_next_bits_to_str_of_bit(size_bits)
        return convert_bits_to_signed_and_unsigned_int(bits_extracted)

    def get_and_remove_last_bits_as_single_int_signed(self, size_bits: int) -> int:
        return self.get_and_remove_last_bits_as_single_int_signed_and_unsigned(size_bits).signed_value

    def get_and_remove_last_byte_as_single_int_unsigned(self) -> int:
        return self.get_and_remove_last_bytes_as_single_int_unsigned(size_bytes=1)

    def get_and_remove_last_bytes_as_single_int_unsigned(self, size_bytes: int) -> int:
        return self.get_and_remove_last_bits_as_single_int_unsigned(size_bytes * NUMBER_OF_BITS_IN_BYTE)

    def get_and_remove_last_bits_as_single_int_unsigned(self, size_bits: int) -> int:
        return self.get_and_remove_last_bits_as_single_int_signed_and_unsigned(size_bits).unsigned_value

    @property
    def is_correctly_and_completely_decoded(self) -> bool:
        return self.number_of_bits_remaining_to_decode == 0
