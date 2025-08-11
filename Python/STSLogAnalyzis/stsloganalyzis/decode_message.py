import csv
import datetime
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, cast

from logger import logger_config

from stsloganalyzis import decode_action_set_content

# CONTENT_OF_FIELD_IN_CASE_OF_DECODING_ERROR = "!!! Decoding Error !!!"


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


class DecodedMessage:

    class XmlMessageRecord:
        def __init__(self, raw_class: str, raw_id: str, raw_offset: str, raw_dim: Optional[int]):
            self._class_name = raw_class
            self.identifier = raw_id
            self.offset = int(raw_offset)
            self.dim = int(raw_dim) if raw_dim else 1
            self.records: List[DecodedMessage.XmlMessageRecord] = []
            self.fields: List[DecodedMessage.XmlMessageField] = []

    class XmlMessageField:
        def __init__(self, raw_class: str, raw_id: str, raw_size: str, parent_record: "DecodedMessage.XmlMessageRecord", raw_dim: Optional[int]):
            self._class_name = raw_class
            self.identifier = raw_id
            self.size = int(raw_size)
            self.dim = int(raw_dim) if raw_dim else 1
            self.parent_record = parent_record
            self.fields: List[DecodedMessage.XmlMessageField] = []

    @dataclass
    class XmlMessageEnumerationValue:
        identifier: str
        value: int

    class XmlMessageEnumeration:
        def __init__(self, raw_id: str):
            self._class_name = raw_class
            self.identifier = raw_id
            self.size = int(raw_size)
            self.dim = int(raw_dim) if raw_dim else 1
            self.values: List[XmlMessageDecoder.XmlMessageEnumerationValue] = []

    def __init__(self, message_number: int, hex_string: str) -> None:
        self.message_number = message_number
        self.decoded_fields_flat_directory: Dict[str, int | bool | str | List[int | str | bool]] = dict()
        self.not_decoded_because_error_fields_names: List[str] = []
        self.hex_string = hex_string
        self.hlf_decoded: Optional[datetime.datetime] = None
        self.current_bit_index = 0
        self.hex_bytes = bytes.fromhex(hex_string.replace(" ", ""))


class HLFDecoder:

    @staticmethod
    def decode_hlf(decoded_message: DecodedMessage) -> None:
        time_field_value = cast(int, decoded_message.decoded_fields_flat_directory["Time"])
        time_offset_value = cast(int, decoded_message.decoded_fields_flat_directory["TimeOffset"])
        decade_field_value = cast(int, decoded_message.decoded_fields_flat_directory["Decade"])
        day_on_decade_field_value = cast(int, decoded_message.decoded_fields_flat_directory["DayOnDecade"])

        hlf_decoded = HLFDecoder.decode_hlf_fields_to_datetime(time_field_value, time_offset_value, decade_field_value, day_on_decade_field_value)
        decoded_message.hlf_decoded = hlf_decoded

    @staticmethod
    def decode_hlf_fields_to_datetime(time_field_value: int, time_offset_value: int, decade_field_value: int, day_on_decade_field_value: int) -> datetime.datetime:

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


class MessageDecoder:
    def __init__(self, xml_directory_path: str, action_set_content_decoder: Optional[decode_action_set_content.ActionSetContentDecoder]) -> None:
        self.xml_message_decoder = XmlMessageDecoder(xml_directory_path=xml_directory_path)
        self.action_set_content_decoder = action_set_content_decoder

    def decode_raw_hexadecimal_message(
        self, message_number: int, hexadecimal_content: str, also_decode_additional_fields_in_specific_messages: bool, also_decode_hlf: bool
    ) -> Optional[DecodedMessage]:
        decoded_message = self.xml_message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=message_number, hexadecimal_content=hexadecimal_content)
        if decoded_message:
            if also_decode_additional_fields_in_specific_messages:
                self.decode_additional_fields_in_specific_messages(decoded_message=decoded_message)

            if also_decode_hlf:
                HLFDecoder.decode_hlf(decoded_message=decoded_message)

        return decoded_message

    def decode_additional_fields_in_specific_messages(self, decoded_message: DecodedMessage) -> None:
        if decoded_message.message_number == 192 and self.action_set_content_decoder:
            actions_field = cast(str, decoded_message.decoded_fields_flat_directory["Actions"])
            action_set_decoded = self.action_set_content_decoder.decode_actions_bitfield(bitfield=actions_field)
            decoded_message.decoded_fields_flat_directory.update(action_set_decoded.action_set_id_with_value)


@dataclass
class XmlMessageDecoder:
    xml_directory_path: str
    decoded_message: Optional[DecodedMessage] = None

    @staticmethod
    def hex_to_int(hex_string: str) -> int:
        """Convert a hex string to an integer."""
        return int(hex_string, 16)

    @staticmethod
    def extract_bits(data: bytes, start_bit: int, bit_length: int) -> str:
        """Extract a specific number of bits starting at a given bit index from a list of bytes."""
        # logger_config.print_and_log_info(f"data length:{len(data)}, start_bit:{start_bit},bit_length:{bit_length},")
        start_byte = start_bit // 8
        end_bit = start_bit + bit_length
        end_byte = (end_bit + 7) // 8

        # Get the relevant bytes
        relevant_bytes = data[start_byte:end_byte]
        combined_bits = "".join(f"{byte:08b}" for byte in relevant_bytes)

        return combined_bits

    @staticmethod
    def extract_bits_bitfield(combined_bits: str, start_bit: int, bit_length: int) -> str:
        # Extract the substring of the combined bits and convert to an integer
        bit_segment = combined_bits[start_bit % 8 : start_bit % 8 + bit_length]
        return bit_segment

    @staticmethod
    def extract_bits_ascii_char(combined_bits: str, start_bit: int, bit_length: int) -> str:
        # Extract the substring of the combined bits and convert to an integer
        result_int = XmlMessageDecoder.extract_bits_int(combined_bits=combined_bits, start_bit=start_bit, bit_length=bit_length)
        return chr(result_int)

    @staticmethod
    def extract_bits_int(combined_bits: str, start_bit: int, bit_length: int) -> int:
        # Extract the substring of the combined bits and convert to an integer
        bit_segment = combined_bits[start_bit % 8 : start_bit % 8 + bit_length]
        return int(bit_segment, 2)

    def _parse_selector(self, record: ET.Element) -> None:

        decoded_message = cast(DecodedMessage, self.decoded_message)

        trigger_value_trigger_element = record[0]
        assert trigger_value_trigger_element.get("class")
        trigger_field = trigger_value_trigger_element.get("case")
        trigger_value = int(cast(str, trigger_value_trigger_element.get("value")))

        assert trigger_field in decoded_message.decoded_fields_flat_directory
        if decoded_message.decoded_fields_flat_directory[trigger_field] == trigger_value:
            elements_to_decode = record[1:]
            assert len(elements_to_decode) == 1
            element_to_decode = elements_to_decode[0]
            assert element_to_decode.tag == "record"
            self._parse_record(record=element_to_decode)

    def _parse_record(self, record: ET.Element) -> None:
        """Recursively parse records to decode fields."""

        decoded_message = cast(DecodedMessage, self.decoded_message)

        record_dim = int(record.get("dim", 1))
        for recordIt in range(0, record_dim):

            record_prefix = "" if record_dim == 1 else f"{record.get("id")}_{recordIt}"

            for element in record:
                # logger_config.print_and_log_info(f"current_bit_index {current_bit_index} is {type(current_bit_index)}")

                if element.tag == "record" or element.tag == "layer":
                    # logger_config.print_and_log_info(f"{element.tag} found: {element.get("id")}, current_bit_index:{current_bit_index}")
                    # Recursive call to process nested records
                    self._parse_record(element)
                elif element.tag == "selector":
                    self._parse_selector(element)
                elif element.tag == "field":
                    raw_field_name = cast(str, element.get("id"))

                    field_size_bits = int(element.get("size", 0))  # Bits
                    field_dim = int(element.get("dim", 1))

                    # logger_config.print_and_log_info(f"Field {field_name} with size {field_size_bits} bits and dim {field_dim}")

                    field_table_values: List[str | int] = []

                    for fieldIt in range(0, field_dim):
                        field_name_with_record_prefix = record_prefix + raw_field_name
                        field_name_with_dim = raw_field_name if field_dim == 1 else raw_field_name + f"_{fieldIt}"
                        field_name_with_dim_and_record_prefix = record_prefix + field_name_with_dim

                        # logger_config.print_and_log_info(f"current_bit_index {current_bit_index} is {type(current_bit_index)}")

                        bits_extracted = self.extract_bits(decoded_message.hex_bytes, decoded_message.current_bit_index, field_size_bits)
                        field_type = element.get("class")

                        field_value: str | int = ""

                        try:
                            if field_type == "BigEndianInteger":
                                field_value = self.extract_bits_int(bits_extracted, decoded_message.current_bit_index, field_size_bits)
                                decoded_message.decoded_fields_flat_directory[field_name_with_dim_and_record_prefix] = field_value
                            elif field_type == "BigEndianBitSet":
                                # field_value = self.extract_bits_int(bits_extracted, current_bit_index, field_size_bits)
                                field_value = self.extract_bits_bitfield(bits_extracted, decoded_message.current_bit_index, field_size_bits)
                                decoded_message.decoded_fields_flat_directory[field_name_with_dim_and_record_prefix] = field_value
                            elif field_type == "BigEndianASCIIChar":
                                field_value = self.extract_bits_ascii_char(bits_extracted, decoded_message.current_bit_index, field_size_bits)
                                decoded_message.decoded_fields_flat_directory[field_name_with_dim_and_record_prefix] = field_value
                                # decoded_fields[field_name_with_dim + "_raw"] = field_value
                            else:
                                logger_config.print_and_log_error(f"Field {field_name_with_dim_and_record_prefix} has unsupported type {field_type}")
                        except Exception as ex:
                            logger_config.print_and_log_exception(ex)
                            logger_config.print_and_log_error(f"Error when decoding field {raw_field_name} {field_name_with_dim_and_record_prefix}")
                            # decoded_message.decoded_fields[field_name] = CONTENT_OF_FIELD_IN_CASE_OF_DECODING_ERROR
                            decoded_message.not_decoded_because_error_fields_names.append(raw_field_name)
                            pass

                        field_table_values.append(field_value)
                        # logger_config.print_and_log_info(f"Field {field_name_with_dim_and_record_prefix} is {field_value}")
                        decoded_message.current_bit_index += field_size_bits
                        # logger_config.print_and_log_info(f"current_bit_index {current_bit_index} is {type(current_bit_index)}")

                    if field_dim > 1:
                        if field_type == "BigEndianASCIIChar":
                            decoded_message.decoded_fields_flat_directory[field_name_with_record_prefix] = "".join(cast(str, field_table_values)).rstrip()
                            # logger_config.print_and_log_info(f"Field {field_name} is {decoded_fields[field_name]}")
                            decoded_message.decoded_fields_flat_directory[field_name_with_record_prefix + "_list"] = field_table_values
                        else:
                            decoded_message.decoded_fields_flat_directory[field_name_with_record_prefix] = field_table_values

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
        decoded_message = self.decoded_message = DecodedMessage(message_number=message_number, hex_string=hexadecimal_content)
        self._parse_record(root)
        self.decoded_message = None
        return decoded_message
