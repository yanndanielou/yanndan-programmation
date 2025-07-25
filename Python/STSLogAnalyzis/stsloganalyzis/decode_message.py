import csv
import datetime
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, cast

from logger import logger_config

from stsloganalyzis import decode_action_set_content


@dataclass
class InvariantMessage:
    message_id: str
    message_number: int


class InvariantMessagesManager:
    def __init__(self, messages_list_csv_file_full_path: str) -> None:

        self.all_messages: List[InvariantMessage] = []
        self.all_messages_by_id: Dict[str, InvariantMessage] = dict()

        # Read the CSV file
        with open(messages_list_csv_file_full_path, mode="r", encoding="ANSI") as file:
            csv_reader = csv.DictReader(file, delimiter=";")

            # Iterate through each row in the CSV
            for csv_row in csv_reader:
                message_id: str = csv_row["ID"]
                message_number = int(csv_row["MESSAGE_INDEX"])
                message = InvariantMessage(message_id=message_id, message_number=message_number)
                self.all_messages.append(message)
                self.all_messages_by_id[message_id] = message

    def get_message_by_id(self, message_id: str) -> Optional[InvariantMessage]:
        return self.all_messages_by_id[message_id] if message_id in self.all_messages_by_id else None


@dataclass
class DecodedMessage:
    message_number: int
    decoded_fields: Dict


class MessageDecoder:
    def __init__(self, xml_directory_path: str, invariant_message_manager: InvariantMessagesManager, action_set_content_decoder: decode_action_set_content.ActionSetContentDecoder) -> None:
        self.xml_message_decoder = XmlMessageDecoder(xml_directory_path=xml_directory_path)
        self.invariant_message_manager = invariant_message_manager
        self.action_set_content_decoder = action_set_content_decoder

    def decode_raw_hexadecimal_message(self, message_number: int, hexadecimal_content: str, also_decode_additional_fields_in_specific_messages: bool) -> Optional[DecodedMessage]:
        decoded_message = self.xml_message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=message_number, hexadecimal_content=hexadecimal_content)
        if decoded_message and also_decode_additional_fields_in_specific_messages:
            self.decode_additional_fields_in_specific_messages(decoded_message=decoded_message)

        return decoded_message

    def decode_additional_fields_in_specific_messages(self, decoded_message: DecodedMessage) -> None:
        if decoded_message.message_number == 192:
            actions_field = decoded_message.decoded_fields["Actions"]
            action_set_decoded = self.action_set_content_decoder.decode_actions_bitfield(bitfield=actions_field)
            decoded_message.decoded_fields.update(action_set_decoded.action_set_id_with_value)


@dataclass
class XmlMessageDecoder:
    xml_directory_path: str

    @staticmethod
    def decode_hlf_fields_to_datetime(time_field_value: int, time_offset_value: int, decade_field_value: int, day_on_decade_field_value: int) -> datetime.datetime:
        """
        Decodes the given fields into a datetime object.

        Parameters:
            time_field_value (int): Number of tenths of a second into the day [0..864000].
            time_offset_value (int): Time offset in tenths of an hour [0..86400].
            decade_field_value (int): Decade within the century [0..9].
            day_on_decade_field_value (int): Day within the decade [0..3652].

        Returns:
            datetime.datetime: The decoded date and time.
        """

        # Calculate the start year of the decade
        start_year = 2000 + (decade_field_value * 10)

        # Calculate the date by adding the day on decade to start of the decade
        decade_date = datetime.datetime(start_year, 1, 1) + datetime.timedelta(days=day_on_decade_field_value)

        # Calculate time in hours, minutes, and seconds from time_field_value
        total_seconds = time_field_value / 10  # tenths of a second to seconds
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = total_seconds % 60

        # Calculate the time offset:
        offset_hours = time_offset_value // 36000
        offset_minutes = (time_offset_value % 36000) // 600

        # Apply the offset for local time
        local_time = decade_date + datetime.timedelta(hours=hours - offset_hours, minutes=minutes - offset_minutes, seconds=seconds)

        return local_time

    def hex_to_int(self, hex_string: str) -> int:
        """Convert a hex string to an integer."""
        return int(hex_string, 16)

    def extract_bits(self, data: bytes, start_bit: int, bit_length: int) -> str:
        """Extract a specific number of bits starting at a given bit index from a list of bytes."""
        # logger_config.print_and_log_info(f"data length:{len(data)}, start_bit:{start_bit},bit_length:{bit_length},")
        start_byte = start_bit // 8
        end_bit = start_bit + bit_length
        end_byte = (end_bit + 7) // 8

        # Get the relevant bytes
        relevant_bytes = data[start_byte:end_byte]
        combined_bits = "".join(f"{byte:08b}" for byte in relevant_bytes)

        return combined_bits

    def extract_bits_bitfield(self, combined_bits: str, start_bit: int, bit_length: int) -> str:
        # Extract the substring of the combined bits and convert to an integer
        bit_segment = combined_bits[start_bit % 8 : start_bit % 8 + bit_length]
        return bit_segment

    def extract_bits_ascii_char(self, combined_bits: str, start_bit: int, bit_length: int) -> str:
        # Extract the substring of the combined bits and convert to an integer
        result_int = self.extract_bits_int(combined_bits=combined_bits, start_bit=start_bit, bit_length=bit_length)
        return chr(result_int)

    def extract_bits_int(self, combined_bits: str, start_bit: int, bit_length: int) -> int:
        # Extract the substring of the combined bits and convert to an integer
        bit_segment = combined_bits[start_bit % 8 : start_bit % 8 + bit_length]
        return int(bit_segment, 2)

    def parse_selector(self, record: ET.Element, previously_decoded_fields: dict, hex_string: str, current_bit_index: int = 0) -> Tuple[Dict[str, int | bool | str | List[int | str | bool]], int]:
        newly_decoded_fields: Dict[str, int | bool | str | List[int | str | bool]] = {}
        hex_bytes = bytes.fromhex(hex_string.replace(" ", ""))

        trigger_value_trigger_element = record[0]
        assert trigger_value_trigger_element.get("class")
        trigger_field = trigger_value_trigger_element.get("case")
        trigger_value = int(cast(str, trigger_value_trigger_element.get("value")))

        assert trigger_field in previously_decoded_fields
        if previously_decoded_fields[trigger_field] == trigger_value:
            elements_to_decode = record[1:]
            assert len(elements_to_decode) == 1
            element_to_decode = elements_to_decode[0]
            assert element_to_decode.tag == "record"
            newly_decoded_fields, current_bit_index = self.parse_record(record=element_to_decode, hex_string=hex_string, current_bit_index=current_bit_index)

        return newly_decoded_fields, current_bit_index

    def parse_record(self, record: ET.Element, hex_string: str, current_bit_index: int = 0) -> Tuple[Dict[str, int | bool | str | List[int | str | bool]], int]:
        """Recursively parse records to decode fields."""
        decoded_fields: Dict[str, int | bool | str | List[int | str | bool]] = {}
        hex_bytes = bytes.fromhex(hex_string.replace(" ", ""))

        for element in record:
            # logger_config.print_and_log_info(f"current_bit_index {current_bit_index} is {type(current_bit_index)}")

            if element.tag == "record" or element.tag == "layer":
                # logger_config.print_and_log_info(f"{element.tag} found: {element.get("id")}, current_bit_index:{current_bit_index}")
                # Recursive call to process nested records
                nested_fields, current_bit_index = self.parse_record(element, hex_string, current_bit_index)
                decoded_fields.update(nested_fields)
            elif element.tag == "selector":
                nested_fields, current_bit_index = self.parse_selector(element, decoded_fields, hex_string, current_bit_index)
                decoded_fields.update(nested_fields)
            elif element.tag == "field":
                field_name = cast(str, element.get("id"))

                field_size_bits = int(element.get("size", 0))  # Bits
                field_dim = int(element.get("dim", 1))

                # logger_config.print_and_log_info(f"Field {field_name} with size {field_size_bits} bits and dim {field_dim}")

                field_table_values: List[str | int] = []

                for i in range(0, field_dim):
                    field_name_with_dim = field_name if field_dim == 1 else field_name + f"_{i}"
                    # logger_config.print_and_log_info(f"current_bit_index {current_bit_index} is {type(current_bit_index)}")

                    bits_extracted = self.extract_bits(hex_bytes, current_bit_index, field_size_bits)
                    field_type = element.get("class")

                    field_value: str | int = ""

                    if field_type == "BigEndianInteger":
                        field_value = self.extract_bits_int(bits_extracted, current_bit_index, field_size_bits)

                        decoded_fields[field_name_with_dim] = field_value
                    elif field_type == "BigEndianBitSet":
                        # field_value = self.extract_bits_int(bits_extracted, current_bit_index, field_size_bits)
                        field_value = self.extract_bits_bitfield(bits_extracted, current_bit_index, field_size_bits)
                        decoded_fields[field_name_with_dim] = field_value
                        pass
                    elif field_type == "BigEndianASCIIChar":
                        field_value = self.extract_bits_ascii_char(bits_extracted, current_bit_index, field_size_bits)
                        decoded_fields[field_name_with_dim] = field_value
                        # decoded_fields[field_name_with_dim + "_raw"] = field_value
                    else:
                        logger_config.print_and_log_error(f"Field {field_name_with_dim} has unsupported type {field_type}")

                    field_table_values.append(field_value)
                    # logger_config.print_and_log_info(f"Field {field_name_with_dim} is {field_value}")
                    current_bit_index += field_size_bits
                    # logger_config.print_and_log_info(f"current_bit_index {current_bit_index} is {type(current_bit_index)}")

                if field_dim > 1:
                    if field_type == "BigEndianASCIIChar":
                        decoded_fields[field_name] = "".join(cast(str, field_table_values)).rstrip()
                        # logger_config.print_and_log_info(f"Field {field_name} is {decoded_fields[field_name]}")
                        decoded_fields[field_name + "_list"] = field_table_values
                    else:
                        decoded_fields[field_name] = field_table_values

        return decoded_fields, current_bit_index

    def decode_xml_fields_in_message_hexadecimal(self, message_number: int, hexadecimal_content: str) -> Optional[DecodedMessage]:
        # Open the corresponding XML file based on message_id
        xml_file_path = self.xml_directory_path + "/" + f"MsgId{message_number}scheme.xml"
        try:
            # Load and parse the XML file
            print(f"Load and parse file {xml_file_path}")
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
        except FileNotFoundError:
            print(f"File {xml_file_path} not found.")
            return None

        # Traverse the root record and decode
        decoded_fields, _ = self.parse_record(root, hexadecimal_content)
        decoded_message = DecodedMessage(decoded_fields=decoded_fields, message_number=message_number)
        return decoded_message

    def decode_hlf_hexa(self, hlf_content_hexa: str, decoded_fields: dict) -> datetime.datetime:

        decoded_hlf = XmlMessageDecoder.decode_hlf_fields_to_datetime(
            time_field_value=decoded_fields["Time"],
            time_offset_value=decoded_fields["TimeOffset"],
            decade_field_value=decoded_fields["Decade"],
            day_on_decade_field_value=decoded_fields["DayOnDecade"],
        )
        print(f"{hlf_content_hexa} is {decoded_hlf}")
        decoded_fields["Decoded time"] = decoded_hlf
        return decoded_hlf


def decode_hlf_hexa_tests_(hlf_content_hexa: str) -> datetime.datetime:
    hlf_message_id = 85
    message_decoder = XmlMessageDecoder(xml_directory_path="D:/RIYL1/Data/Xml")

    decoded_hexa_content_with_xml = cast(DecodedMessage, message_decoder.decode_xml_fields_in_message_hexadecimal(hlf_message_id, hlf_content_hexa)).decoded_fields
    # print(decoded_hexa_content_with_xml)
    decoded_hlf = XmlMessageDecoder.decode_hlf_fields_to_datetime(
        time_field_value=decoded_hexa_content_with_xml["Time"],
        time_offset_value=decoded_hexa_content_with_xml["TimeOffset"],
        decade_field_value=decoded_hexa_content_with_xml["Decade"],
        day_on_decade_field_value=decoded_hexa_content_with_xml["DayOnDecade"],
    )
    print(f"{hlf_content_hexa} is {decoded_hlf}")
    return decoded_hlf


# Example usage

"""
decode_hlf_hexa("00 0d 23 f2 00 00 8c a0 27 4a")
decode_hlf_hexa("00 0d 24 88 00 00 8c a0 27 4a")
decode_hlf_hexa("00 0d 25 1e 00 00 8c a0 27 4a")
decode_hlf_hexa("00 0d 25 b4 00 00 8c a0 27 4a")

# print(decode_hlf(time_field_value=322730, time_offset_value=1, decade_field_value=2, day_on_decade_field_value=1428))
"""
