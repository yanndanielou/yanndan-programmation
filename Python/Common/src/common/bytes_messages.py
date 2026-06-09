from dataclasses import dataclass
from typing import List, cast


@dataclass
class DecodedIntResult:
    signed_value: int
    unsigned_value: int


class DecodedBytesMessage:

    def __init__(self, hex_string: str) -> None:
        self.hex_string = hex_string
        self.current_bit_index = 0
        self.hex_bytes = bytes.fromhex(hex_string.replace(" ", ""))

    def extract_bits(self, start_bit: int, number_of_bits: int) -> str:
        bits_extracted = self.extract_bits_to_bytes(data=self.hex_bytes, start_bit=start_bit, number_of_bits=number_of_bits)
        self.current_bit_index += number_of_bits
        return bits_extracted

    def get_next_bits_as_ascii_char(self, number_of_chars: int, size_bits_per_char: int) -> str:
        all_chars: List[str] = []

        for _ in range(0, number_of_chars):
            bits_extracted = self.extract_bits(self.current_bit_index, size_bits_per_char)
            current_char = self.convert_bits_ascii_char(bits_extracted, self.current_bit_index, size_bits_per_char)
            all_chars.append(current_char)

        string_value = "".join(cast(str, all_chars)).rstrip()

        return string_value

    def get_next_bits_as_bitset_str(self, size_bits: int) -> str:

        bits_extracted = self.extract_bits(self.current_bit_index, size_bits)
        field_value = self.convert_bits_bitfield(bits_extracted, self.current_bit_index, size_bits)
        return field_value

    def get_next_bits_as_single_int_signed_and_unsigned(self, size_bits: int) -> DecodedIntResult:
        bits_extracted = self.extract_bits(self.current_bit_index, size_bits)
        return self.convert_bits_signed_and_unsigned_int(bits_extracted, self.current_bit_index, size_bits)

    def get_next_bits_as_int_table_signed_and_unsigned(self, table_dim: int, size_bits: int) -> List[DecodedIntResult]:
        all_values: List[DecodedIntResult] = []

        for _ in range(0, table_dim):
            bits_extracted = self.extract_bits(self.current_bit_index, size_bits)
            field_unsigned_value = self.convert_bits_unsigned_int(bits_extracted, self.current_bit_index, size_bits)

            field_signed_value = self.convert_bits_signed_int(bits_extracted, self.current_bit_index, size_bits)
            all_values.append(DecodedIntResult(signed_value=field_signed_value, unsigned_value=field_unsigned_value))

        return all_values

    def is_correctly_and_completely_decoded(self) -> bool:
        size_bits = len(self.hex_bytes) * 8
        return self.current_bit_index == size_bits

    @staticmethod
    def extract_bits_to_bytes(data: bytes, start_bit: int, number_of_bits: int) -> str:
        """Extract a specific number of bits starting at a given bit index from a list of bytes."""
        # logger_config.print_and_log_info(f"data length:{len(data)}, start_bit:{start_bit},number_of_bits:{number_of_bits},")
        start_byte = start_bit // 8
        end_bit = start_bit + number_of_bits
        end_byte = (end_bit + 7) // 8

        # Get the relevant bytes
        relevant_bytes = data[start_byte:end_byte]
        combined_bits = "".join(f"{byte:08b}" for byte in relevant_bytes)

        return combined_bits

    @staticmethod
    def convert_bits_bitfield(combined_bits: str, start_bit: int, number_of_bits: int) -> str:
        # Extract the substring of the combined bits and convert to an integer
        bit_segment = combined_bits[(start_bit - number_of_bits) % 8 : (start_bit - number_of_bits) % 8 + number_of_bits]
        return bit_segment

    @staticmethod
    def convert_bits_ascii_char(combined_bits: str, start_bit: int, number_of_bits: int) -> str:
        # Extract the substring of the combined bits and convert to an integer
        result_int = DecodedBytesMessage.convert_bits_unsigned_int(combined_bits=combined_bits, start_bit=start_bit, number_of_bits=number_of_bits)
        return chr(result_int)

    @staticmethod
    def convert_bits_signed_and_unsigned_int(combined_bits: str, start_bit: int, number_of_bits: int) -> DecodedIntResult:

        return DecodedIntResult(
            signed_value=DecodedBytesMessage.convert_bits_signed_int(combined_bits=combined_bits, start_bit=start_bit, number_of_bits=number_of_bits),
            unsigned_value=DecodedBytesMessage.convert_bits_unsigned_int(combined_bits=combined_bits, start_bit=start_bit, number_of_bits=number_of_bits),
        )

    @staticmethod
    def convert_bits_unsigned_int(combined_bits: str, start_bit: int, number_of_bits: int) -> int:
        # Extract the substring of the combined bits and convert to an integer
        bit_segment = DecodedBytesMessage.convert_bits_bitfield(combined_bits=combined_bits, start_bit=start_bit, number_of_bits=number_of_bits)
        return int(bit_segment, 2)

    @staticmethod
    def convert_bits_signed_int(combined_bits: str, start_bit: int, number_of_bits: int) -> int:
        # Extract the substring of the combined bits and convert to a signed integer
        bit_segment = DecodedBytesMessage.convert_bits_bitfield(combined_bits=combined_bits, start_bit=start_bit, number_of_bits=number_of_bits)
        value = int(bit_segment, 2)
        if value >= (1 << (number_of_bits - 1)):
            value -= 1 << number_of_bits
        return value
