import csv
import datetime
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, cast

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

    class XmlMessageRecordMacro:
        def __init__(self, raw_class: str, raw_id: str, raw_offset: str, raw_dim: Optional[str], decoded_message: "DecodedMessage"):
            self._class_name = raw_class
            self.identifier = raw_id
            self.offset = int(raw_offset)
            self.dim = int(raw_dim) if raw_dim else 1
            self.decoded_message = decoded_message

    class XmlMessageRecordUnit:
        def __init__(self, record_macro: "DecodedMessage.XmlMessageRecordMacro", index: int):
            self.record_macro = record_macro
            self.fields: List[DecodedMessage.XmlMessageFieldUnit] = []
            self.records: List[DecodedMessage.XmlMessageRecordMacro] = []
            self.all_fields_unit_by_name: Dict[str, DecodedMessage.XmlMessageFieldUnit | List[DecodedMessage.XmlMessageFieldUnit]] = {}
            self.index = index
            record_macro.decoded_message.add_record_by_name(self)

        def add_field_unit(self, field: "DecodedMessage.XmlMessageFieldUnit") -> None:
            self.fields.append(field)
            assert field.field_macro.identifier not in self.all_fields_unit_by_name
            self.all_fields_unit_by_name[field.field_macro.identifier] = field

    class XmlMessageFieldMacro:
        def __init__(
            self,
            raw_class: str,
            raw_id: str,
            size_bits: int,
            parent_record: "DecodedMessage.XmlMessageRecordUnit",
            field_name_with_record_prefix: str,
            decoded_message: "DecodedMessage",
            raw_dim: Optional[int],
        ):
            self._class_name = raw_class
            self.identifier = raw_id
            self.size_bits = size_bits
            self.dim = int(raw_dim) if raw_dim else 1
            self.parent_record = parent_record
            self.unit_fields: List[DecodedMessage.XmlMessageFieldUnit] = []
            self.field_name_with_record_prefix = field_name_with_record_prefix
            self.decoded_message = decoded_message

    class XmlMessageFieldUnit(ABC):
        @abstractmethod
        def __init__(
            self,
            field_macro: "DecodedMessage.XmlMessageFieldMacro",
            index: int,
            decoded_message: "DecodedMessage",
        ):
            self.field_macro = field_macro
            self.human_readable_value: Optional[int | bool | str] = None
            self.value: Optional[int | bool | str | List[int] | List[bool]] = None

            self.index = index
            field_macro.unit_fields.append(self)
            self.decoded_message = decoded_message
            decoded_message.add_field_by_name(self)

            field_macro.parent_record.add_field_unit(self)

    class XmlMessageFieldString(XmlMessageFieldUnit):
        def __init__(self, field_macro: "DecodedMessage.XmlMessageFieldMacro", value: str):
            super().__init__(field_macro=field_macro, decoded_message=field_macro.decoded_message, index=0)
            self.value = value

    class XmlMessageFieldBitfield(XmlMessageFieldUnit):
        def __init__(self, field_macro: "DecodedMessage.XmlMessageFieldMacro", value: str):
            super().__init__(field_macro=field_macro, decoded_message=field_macro.decoded_message, index=0)
            self.value = value

    class XmlMessageFieldInt(XmlMessageFieldUnit):
        def __init__(self, field_macro: "DecodedMessage.XmlMessageFieldMacro", value: int | List[int]):
            super().__init__(field_macro=field_macro, decoded_message=field_macro.decoded_message, index=0)
            self.value = value

    @dataclass
    class XmlMessageEnumerationValue:
        identifier: str
        value: int

    class XmlMessageEnumeration:
        def __init__(self, raw_id: str):
            self.identifier = raw_id
            self.values: List[DecodedMessage.XmlMessageEnumerationValue] = []

    def __init__(self, message_number: int, hex_string: str) -> None:
        self.message_number = message_number
        self.decoded_fields_flat_directory: Dict[str, int | bool | str | List[int] | List[str] | List[bool]] = {}
        self.all_fields_by_name: Dict[str, DecodedMessage.XmlMessageFieldUnit | List[DecodedMessage.XmlMessageFieldUnit]] = {}
        self.all_records_by_name: Dict[str, DecodedMessage.XmlMessageRecordUnit | List[DecodedMessage.XmlMessageRecordUnit]] = {}
        self.not_decoded_because_error_fields_names: List[str] = []
        self.hex_string = hex_string
        self.hlf_decoded: Optional[datetime.datetime] = None
        self.current_bit_index = 0
        self.hex_bytes = bytes.fromhex(hex_string.replace(" ", ""))
        self.root_record: Optional[DecodedMessage.XmlMessageRecordMacro] = None

    def add_field_by_name(self, message_field: XmlMessageFieldUnit) -> None:
        if message_field.field_macro.identifier not in self.all_fields_by_name:
            self.all_fields_by_name[message_field.field_macro.identifier] = message_field
        elif isinstance(self.all_fields_by_name[message_field.field_macro.identifier], list):
            cast(list, self.all_fields_by_name[message_field.field_macro.identifier]).append(message_field)
        else:
            # Convert to list
            previous_field = cast(DecodedMessage.XmlMessageFieldUnit, self.all_fields_by_name[message_field.field_macro.identifier])
            self.all_fields_by_name[message_field.field_macro.identifier] = [previous_field, message_field]

    def add_record_by_name(self, record_field: XmlMessageRecordUnit) -> None:
        if record_field.record_macro.identifier not in self.all_records_by_name:
            self.all_records_by_name[record_field.record_macro.identifier] = record_field
        elif isinstance(self.all_records_by_name[record_field.record_macro.identifier], list):
            cast(list, self.all_records_by_name[record_field.record_macro.identifier]).append(record_field)
        else:
            # Convert to list
            previous_record = cast(DecodedMessage.XmlMessageRecordUnit, self.all_records_by_name[record_field.record_macro.identifier])
            self.all_records_by_name[record_field.record_macro.identifier] = [previous_record, record_field]

    def is_correctly_and_completely_decoded(self) -> bool:
        if self.not_decoded_because_error_fields_names:
            return False

        size_bits = len(self.hex_bytes) * 8
        return self.current_bit_index == size_bits


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


class XmlMessageDecoder:

    BIG_ENDIAN_INTEGER = "BigEndianInteger"
    BIG_ENDIAN_BIT_SET = "BigEndianBitSet"
    BIG_ENDIAN_ASCII_CHAR = "BigEndianASCIIChar"

    def __init__(self, xml_directory_path: str) -> None:
        self.xml_directory_path = xml_directory_path
        self.cached_messages_by_id: Dict[int, ET.Element] = dict()
        self.decoded_message: Optional[DecodedMessage] = None

    @staticmethod
    def hex_to_int(hex_string: str) -> int:
        """Convert a hex string to an integer."""
        return int(hex_string, 16)

    def extract_bits(self, start_bit: int, bit_length: int) -> str:
        assert self.decoded_message
        bits_extracted = self.extract_bits_to_bytes(data=self.decoded_message.hex_bytes, start_bit=start_bit, bit_length=bit_length)
        self.decoded_message.current_bit_index += bit_length
        return bits_extracted

    @staticmethod
    def extract_bits_to_bytes(data: bytes, start_bit: int, bit_length: int) -> str:
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
    def convert_bits_bitfield(combined_bits: str, start_bit: int, bit_length: int) -> str:
        # Extract the substring of the combined bits and convert to an integer
        bit_segment = combined_bits[(start_bit - bit_length) % 8 : (start_bit - bit_length) % 8 + bit_length]
        return bit_segment

    @staticmethod
    def convert_bits_ascii_char(combined_bits: str, start_bit: int, bit_length: int) -> str:
        # Extract the substring of the combined bits and convert to an integer
        result_int = XmlMessageDecoder.convert_bits_int(combined_bits=combined_bits, start_bit=start_bit, bit_length=bit_length)
        return chr(result_int)

    @staticmethod
    def convert_bits_int(combined_bits: str, start_bit: int, bit_length: int) -> int:
        # Extract the substring of the combined bits and convert to an integer
        bit_segment = XmlMessageDecoder.convert_bits_bitfield(combined_bits=combined_bits, start_bit=start_bit, bit_length=bit_length)
        return int(bit_segment, 2)

    def _parse_selector(self, record: ET.Element, parent_record: DecodedMessage.XmlMessageRecordUnit) -> None:

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
            self._parse_record(record=element_to_decode, parent_record=parent_record)

    def _parse_root(self, root: ET.Element) -> None:
        assert len(root) == 1
        self._parse_layer(root[0])

    def _parse_layer(self, layer: ET.Element) -> None:
        assert len(layer) == 1
        self._parse_record(layer[0])

    def _parse_string_type_field(self, xml_decoded_field_macro: DecodedMessage.XmlMessageFieldMacro) -> None:

        assert self.decoded_message is not None
        all_chars: List[str] = []

        for i in range(0, xml_decoded_field_macro.dim):
            bits_extracted = self.extract_bits(self.decoded_message.current_bit_index, xml_decoded_field_macro.size_bits)

            current_char = self.convert_bits_ascii_char(bits_extracted, self.decoded_message.current_bit_index, xml_decoded_field_macro.size_bits)
            all_chars.append(current_char)
            self.decoded_message.decoded_fields_flat_directory[xml_decoded_field_macro.field_name_with_record_prefix + "_" + str(i)] = current_char

        string_value = "".join(cast(str, all_chars)).rstrip()
        # logger_config.print_and_log_info(f"Field {field_name} is {decoded_fields[field_name]}")
        self.decoded_message.decoded_fields_flat_directory[xml_decoded_field_macro.field_name_with_record_prefix] = string_value
        self.decoded_message.decoded_fields_flat_directory[xml_decoded_field_macro.field_name_with_record_prefix + "_list"] = all_chars

        DecodedMessage.XmlMessageFieldString(field_macro=xml_decoded_field_macro, value=string_value)

    def _parse_bitset_type_field(self, xml_decoded_field_macro: DecodedMessage.XmlMessageFieldMacro) -> None:

        assert self.decoded_message is not None

        bits_extracted = self.extract_bits(self.decoded_message.current_bit_index, xml_decoded_field_macro.size_bits)
        field_value = self.convert_bits_bitfield(bits_extracted, self.decoded_message.current_bit_index, xml_decoded_field_macro.size_bits)
        self.decoded_message.decoded_fields_flat_directory[xml_decoded_field_macro.field_name_with_record_prefix] = field_value

        DecodedMessage.XmlMessageFieldBitfield(field_macro=xml_decoded_field_macro, value=field_value)

    def _parse_int_table_type_field(self, xml_decoded_field_macro: DecodedMessage.XmlMessageFieldMacro) -> None:

        assert self.decoded_message is not None

        all_values: List[int] = []

        for _ in range(0, xml_decoded_field_macro.dim):
            bits_extracted = self.extract_bits(self.decoded_message.current_bit_index, xml_decoded_field_macro.size_bits)
            field_value = self.convert_bits_int(bits_extracted, self.decoded_message.current_bit_index, xml_decoded_field_macro.size_bits)
            self.decoded_message.decoded_fields_flat_directory[xml_decoded_field_macro.field_name_with_record_prefix] = field_value

            all_values.append(field_value)

        self.decoded_message.decoded_fields_flat_directory[xml_decoded_field_macro.field_name_with_record_prefix] = all_values

        DecodedMessage.XmlMessageFieldInt(field_macro=xml_decoded_field_macro, value=all_values)

    def _parse_single_int_type_field(self, xml_decoded_field_macro: DecodedMessage.XmlMessageFieldMacro) -> None:

        assert self.decoded_message is not None

        field_table_values: List[str | int] = []

        bits_extracted = self.extract_bits(self.decoded_message.current_bit_index, xml_decoded_field_macro.size_bits)
        field_value = self.convert_bits_int(bits_extracted, self.decoded_message.current_bit_index, xml_decoded_field_macro.size_bits)
        self.decoded_message.decoded_fields_flat_directory[xml_decoded_field_macro.field_name_with_record_prefix] = field_value

        field_table_values.append(field_value)

        DecodedMessage.XmlMessageFieldInt(field_macro=xml_decoded_field_macro, value=field_value)

    def _parse_int_type_field(self, xml_decoded_field_macro: DecodedMessage.XmlMessageFieldMacro) -> None:

        assert self.decoded_message is not None
        if xml_decoded_field_macro.dim == 1:
            self._parse_single_int_type_field(xml_decoded_field_macro=xml_decoded_field_macro)
        else:
            self._parse_int_table_type_field(xml_decoded_field_macro=xml_decoded_field_macro)

    def _parse_field(self, element: ET.Element, xml_message_record_unit: DecodedMessage.XmlMessageRecordUnit, record_prefix: str) -> None:

        assert self.decoded_message is not None

        raw_field_name = cast(str, element.get("id"))
        field_size_bits = int(element.get("size", 0))
        field_dim = int(element.get("dim", 1))
        field_type = element.get("class")
        assert field_type

        field_name_with_record_prefix = record_prefix + raw_field_name

        xml_decoded_field_macro = DecodedMessage.XmlMessageFieldMacro(
            raw_class=field_type,
            parent_record=xml_message_record_unit,
            raw_dim=field_dim,
            raw_id=raw_field_name,
            size_bits=field_size_bits,
            field_name_with_record_prefix=field_name_with_record_prefix,
            decoded_message=self.decoded_message,
        )

        try:
            if field_type == self.BIG_ENDIAN_ASCII_CHAR:
                self._parse_string_type_field(xml_decoded_field_macro=xml_decoded_field_macro)

            elif field_type == self.BIG_ENDIAN_BIT_SET:
                self._parse_bitset_type_field(xml_decoded_field_macro=xml_decoded_field_macro)

            elif field_type == self.BIG_ENDIAN_INTEGER:
                self._parse_int_type_field(xml_decoded_field_macro=xml_decoded_field_macro)

        except ValueError as val_err:
            # logger_config.print_and_log_exception(val_err)
            logger_config.print_and_log_error(
                f"Message {self.decoded_message.message_number}: Error when decoding field {raw_field_name} {xml_decoded_field_macro.field_name_with_record_prefix}. {val_err}. {val_err.__class__.__name__}"
            )
            self.decoded_message.not_decoded_because_error_fields_names.append(raw_field_name)

    def _parse_record(self, record: ET.Element, parent_record: Optional[DecodedMessage.XmlMessageRecordUnit] = None) -> None:
        """Recursively parse records to decode fields."""
        raw_class = record.get("class")
        assert raw_class
        raw_dim = record.get("dim")
        raw_id = record.get("id")
        assert raw_id
        raw_offset = record.get("offset")
        assert raw_offset

        assert self.decoded_message
        xml_message_record_macro = DecodedMessage.XmlMessageRecordMacro(
            raw_class=raw_class,
            raw_dim=raw_dim,
            raw_id=raw_id,
            raw_offset=raw_offset,
            decoded_message=self.decoded_message,
        )

        if parent_record is None:
            self.decoded_message.root_record = xml_message_record_macro
        else:
            parent_record.records.append(xml_message_record_macro)

        record_dim = int(record.get("dim", 1))
        for record_it in range(0, record_dim):

            xml_message_record_unit = DecodedMessage.XmlMessageRecordUnit(xml_message_record_macro, index=record_it)
            record_prefix = "" if record_dim == 1 else f"{record.get("id")}_{record_it}"

            for element in record:
                # logger_config.print_and_log_info(f"current_bit_index {current_bit_index} is {type(current_bit_index)}")

                if element.tag == "record":
                    # logger_config.print_and_log_info(f"{element.tag} found: {element.get("id")}, current_bit_index:{current_bit_index}")
                    # Recursive call to process nested records
                    self._parse_record(record=element, parent_record=xml_message_record_unit)
                elif element.tag == "selector":
                    self._parse_selector(element, parent_record=xml_message_record_unit)
                elif element.tag == "field":
                    self._parse_field(element=element, xml_message_record_unit=xml_message_record_unit, record_prefix=record_prefix)

    @staticmethod
    def get_xml_file_root(message_number: int, xml_directory_path: str) -> Optional[ET.Element]:
        # Open the corresponding XML file based on message_id
        xml_file_path = xml_directory_path + "/" + f"MsgId{message_number}scheme.xml"
        try:
            # Load and parse the XML file
            logger_config.print_and_log_info(f"Load and parse file {xml_file_path}")
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            return root
        except FileNotFoundError:
            logger_config.print_and_log_error(f"File {xml_file_path} not found.")
            return None

    def decode_xml_fields_in_message_hexadecimal(self, message_number: int, hexadecimal_content: str) -> Optional[DecodedMessage]:

        if message_number not in self.cached_messages_by_id:
            xml_file_root = XmlMessageDecoder.get_xml_file_root(message_number=message_number, xml_directory_path=self.xml_directory_path)
            if xml_file_root is None:
                return None
            self.cached_messages_by_id[message_number] = xml_file_root

        root = self.cached_messages_by_id[message_number]
        # Traverse the root record and decode
        decoded_message = self.decoded_message = DecodedMessage(message_number=message_number, hex_string=hexadecimal_content)
        self._parse_root(root)
        self.decoded_message = None
        return decoded_message
