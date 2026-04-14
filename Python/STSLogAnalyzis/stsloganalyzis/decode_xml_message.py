import datetime
from enum import Enum
import os
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Dict, List, Optional, cast, Tuple

from logger import logger_config


class DecodedXmlMessage:

    class XmlMessageRecordMacro:
        def __init__(self, raw_class: str, raw_id: str, raw_offset: str, raw_dim: Optional[str], decoded_xml_message: "DecodedXmlMessage"):
            self._class_name = raw_class
            self.identifier = raw_id
            self.offset = int(raw_offset)
            assert self.offset == 0, f"Not supported offset {self.offset} for record {raw_class} {raw_id} {decoded_xml_message.message_number}"
            self.dim = int(raw_dim) if raw_dim else 1
            self.decoded_xml_message = decoded_xml_message

    class XmlMessageRecordUnit:
        def __init__(self, record_macro: "DecodedXmlMessage.XmlMessageRecordMacro", index: int):
            self.record_macro = record_macro
            self.fields: List[DecodedXmlMessage.XmlMessageFieldUnit] = []
            self.records: List[DecodedXmlMessage.XmlMessageRecordMacro] = []
            self.all_fields_unit_by_name: Dict[str, DecodedXmlMessage.XmlMessageFieldUnit | List[DecodedXmlMessage.XmlMessageFieldUnit]] = {}
            self.index = index
            record_macro.decoded_xml_message.add_record_by_name(self)
            self.long_name = self.record_macro.identifier if self.record_macro.dim == 1 else f"{self.record_macro.identifier}_{index}"

        def add_field_unit(self, field: "DecodedXmlMessage.XmlMessageFieldUnit") -> None:
            self.fields.append(field)
            assert field.field_macro.identifier not in self.all_fields_unit_by_name
            self.all_fields_unit_by_name[field.field_macro.identifier] = field

    class XmlMessageFieldMacro:
        def __init__(
            self,
            raw_class: str,
            raw_id: str,
            size_bits: int,
            parent_record: "DecodedXmlMessage.XmlMessageRecordUnit",
            field_name_with_record_prefix: str,
            decoded_xml_message: "DecodedXmlMessage",
            raw_dim: Optional[int],
        ):
            self._class_name = raw_class
            self.identifier = raw_id
            self.size_bits = size_bits
            self.dim = int(raw_dim) if raw_dim else 1
            self.parent_record = parent_record
            self.unit_fields: List[DecodedXmlMessage.XmlMessageFieldUnit] = []
            self.field_name_with_record_prefix = field_name_with_record_prefix
            self.decoded_xml_message = decoded_xml_message
            self.bits_extracted: str = ""

    class XmlMessageFieldUnit(ABC):
        @abstractmethod
        def __init__(
            self,
            field_macro: "DecodedXmlMessage.XmlMessageFieldMacro",
            index: int,
            decoded_xml_message: "DecodedXmlMessage",
        ):
            self.field_macro = field_macro
            self.human_readable_value: Optional[int | bool | str] = None
            self.value: Optional[int | bool | str | List[int] | List[bool]] = None

            self.index = index
            field_macro.unit_fields.append(self)
            self.decoded_xml_message = decoded_xml_message
            decoded_xml_message.add_field_by_name(self)

            field_macro.parent_record.add_field_unit(self)
            long_name_record_prefix = "" if self.field_macro.parent_record.record_macro.dim == 1 else f"{self.field_macro.parent_record.record_macro.identifier}_{index}_"
            field_name = self.field_macro.identifier if self.field_macro.dim == 1 else f"{self.field_macro.identifier}_{index}"
            self.long_name = long_name_record_prefix + field_name

    class XmlMessageFieldString(XmlMessageFieldUnit):
        def __init__(self, field_macro: "DecodedXmlMessage.XmlMessageFieldMacro", value: str):
            super().__init__(field_macro=field_macro, decoded_xml_message=field_macro.decoded_xml_message, index=0)
            self.value = value

    class XmlMessageFieldBitfield(XmlMessageFieldUnit):
        def __init__(self, field_macro: "DecodedXmlMessage.XmlMessageFieldMacro", value: str):
            super().__init__(field_macro=field_macro, decoded_xml_message=field_macro.decoded_xml_message, index=0)
            self.value = value

    class XmlMessageFieldInt(XmlMessageFieldUnit):
        def __init__(self, field_macro: "DecodedXmlMessage.XmlMessageFieldMacro", unsigned_value: int | List[int], signed_value: int | List[int]):
            super().__init__(field_macro=field_macro, decoded_xml_message=field_macro.decoded_xml_message, index=0)
            self.value = unsigned_value
            self.unsigned_value = unsigned_value
            self.signed_value = signed_value

    @dataclass
    class XmlMessageEnumerationValue:
        identifier: str
        value: int

    class XmlMessageEnumeration:
        def __init__(self, raw_id: str):
            self.identifier = raw_id
            self.values: List[DecodedXmlMessage.XmlMessageEnumerationValue] = []

    def __init__(self, message_number: int, hex_string: str) -> None:
        self.message_number = message_number
        self.decoded_fields_flat_directory: Dict[str, int | bool | str | List[int] | List[str] | List[bool]] = {}
        self.all_fields_by_name: Dict[str, DecodedXmlMessage.XmlMessageFieldUnit | List[DecodedXmlMessage.XmlMessageFieldUnit]] = {}
        self.all_records_by_name: Dict[str, DecodedXmlMessage.XmlMessageRecordUnit | List[DecodedXmlMessage.XmlMessageRecordUnit]] = {}
        self.not_decoded_because_error_fields_names: List[str] = []
        self.hex_string = hex_string
        self.hlf_decoded: Optional[datetime.datetime] = None
        self.current_bit_index = 0
        self.hex_bytes = bytes.fromhex(hex_string.replace(" ", ""))
        self.root_record: Optional[DecodedXmlMessage.XmlMessageRecordMacro] = None

    def add_field_by_name(self, message_field: XmlMessageFieldUnit) -> None:
        if message_field.field_macro.identifier not in self.all_fields_by_name:
            self.all_fields_by_name[message_field.field_macro.identifier] = message_field
        elif isinstance(self.all_fields_by_name[message_field.field_macro.identifier], list):
            cast(list, self.all_fields_by_name[message_field.field_macro.identifier]).append(message_field)
        else:
            # Convert to list
            previous_field = cast(DecodedXmlMessage.XmlMessageFieldUnit, self.all_fields_by_name[message_field.field_macro.identifier])
            self.all_fields_by_name[message_field.field_macro.identifier] = [previous_field, message_field]

    def add_record_by_name(self, record_field: XmlMessageRecordUnit) -> None:
        if record_field.record_macro.identifier not in self.all_records_by_name:
            self.all_records_by_name[record_field.record_macro.identifier] = record_field
        elif isinstance(self.all_records_by_name[record_field.record_macro.identifier], list):
            cast(list, self.all_records_by_name[record_field.record_macro.identifier]).append(record_field)
        else:
            # Convert to list
            previous_record = cast(DecodedXmlMessage.XmlMessageRecordUnit, self.all_records_by_name[record_field.record_macro.identifier])
            self.all_records_by_name[record_field.record_macro.identifier] = [previous_record, record_field]

    def is_correctly_and_completely_decoded(self) -> bool:
        if self.not_decoded_because_error_fields_names:
            return False

        size_bits = len(self.hex_bytes) * 8
        return self.current_bit_index == size_bits


class SignedOrUnsignedTypeForIntegerFieldsManagerBase(ABC):
    class TypeDecoding(Enum):
        SIGNED_ONLY = "SIGNED_ONLY"
        UNSIGNED_ONLY = "UNSIGNED_ONLY"
        SIGNED_AND_UNSIGNED = "SIGNED_AND_UNSIGNED"

    @abstractmethod
    def get_decoding_type_for_field(self, message_number: int, field_name: str) -> TypeDecoding:
        pass


class AlwaysUnsignedTypeForIntegerFieldsManager(SignedOrUnsignedTypeForIntegerFieldsManagerBase):

    def get_decoding_type_for_field(self, message_number: int, field_name: str) -> SignedOrUnsignedTypeForIntegerFieldsManagerBase.TypeDecoding:
        return SignedOrUnsignedTypeForIntegerFieldsManagerBase.TypeDecoding.UNSIGNED_ONLY


class XmlMessageDecoder:

    BIG_ENDIAN_INTEGER = "BigEndianInteger"
    BIG_ENDIAN_BIT_SET = "BigEndianBitSet"
    BIG_ENDIAN_ASCII_CHAR = "BigEndianASCIIChar"

    _parsed_xml_files_by_path: ClassVar[Dict[str, ET.Element]] = {}

    def __init__(self, xml_directory_path: str, signed_or_unsigned_type_for_integer_fields_manager: Optional[SignedOrUnsignedTypeForIntegerFieldsManagerBase]) -> None:
        if not signed_or_unsigned_type_for_integer_fields_manager:
            signed_or_unsigned_type_for_integer_fields_manager = AlwaysUnsignedTypeForIntegerFieldsManager()
        self.signed_or_unsigned_type_for_integer_fields_manager = signed_or_unsigned_type_for_integer_fields_manager

        self.xml_directory_path = xml_directory_path
        self.cached_messages_by_id: Dict[int, ET.Element] = dict()
        self.decoded_xml_message: Optional[DecodedXmlMessage] = None
        self.signed_integer_fields_by_message_id_and_field_name = signed_integer_fields_by_message_id_and_field_name

    @staticmethod
    def hex_to_int(hex_string: str) -> int:
        """Convert a hex string to an integer."""
        return int(hex_string, 16)

    def extract_bits(self, start_bit: int, bit_length: int) -> str:
        assert self.decoded_xml_message
        bits_extracted = self.extract_bits_to_bytes(data=self.decoded_xml_message.hex_bytes, start_bit=start_bit, bit_length=bit_length)
        self.decoded_xml_message.current_bit_index += bit_length
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
        result_int = XmlMessageDecoder.convert_bits_unsigned_int(combined_bits=combined_bits, start_bit=start_bit, bit_length=bit_length)
        return chr(result_int)

    @staticmethod
    def convert_bits_unsigned_int(combined_bits: str, start_bit: int, bit_length: int) -> int:
        # Extract the substring of the combined bits and convert to an integer
        bit_segment = XmlMessageDecoder.convert_bits_bitfield(combined_bits=combined_bits, start_bit=start_bit, bit_length=bit_length)
        return int(bit_segment, 2)

    @staticmethod
    def convert_bits_signed_int(combined_bits: str, start_bit: int, bit_length: int) -> int:
        # Extract the substring of the combined bits and convert to a signed integer
        bit_segment = XmlMessageDecoder.convert_bits_bitfield(combined_bits=combined_bits, start_bit=start_bit, bit_length=bit_length)
        value = int(bit_segment, 2)
        if value >= (1 << (bit_length - 1)):
            value -= 1 << bit_length
        return value

    def _parse_selector(self, record: ET.Element, parent_record: DecodedXmlMessage.XmlMessageRecordUnit) -> None:

        decoded_xml_message = cast(DecodedXmlMessage, self.decoded_xml_message)

        trigger_value_trigger_element = record[0]
        assert trigger_value_trigger_element.get("class")
        trigger_field = trigger_value_trigger_element.get("case")
        trigger_value = int(cast(str, trigger_value_trigger_element.get("value")))

        assert trigger_field in decoded_xml_message.decoded_fields_flat_directory
        if decoded_xml_message.decoded_fields_flat_directory[trigger_field] == trigger_value:
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

    def _parse_string_type_field(self, xml_decoded_field_macro: DecodedXmlMessage.XmlMessageFieldMacro) -> None:

        assert self.decoded_xml_message is not None
        all_chars: List[str] = []

        for i in range(0, xml_decoded_field_macro.dim):
            xml_decoded_field_macro.bits_extracted = self.extract_bits(self.decoded_xml_message.current_bit_index, xml_decoded_field_macro.size_bits)

            current_char = self.convert_bits_ascii_char(xml_decoded_field_macro.bits_extracted, self.decoded_xml_message.current_bit_index, xml_decoded_field_macro.size_bits)
            all_chars.append(current_char)
            self.decoded_xml_message.decoded_fields_flat_directory[xml_decoded_field_macro.field_name_with_record_prefix + "_" + str(i)] = current_char

        string_value = "".join(cast(str, all_chars)).rstrip()
        # logger_config.print_and_log_info(f"Field {field_name} is {decoded_fields[field_name]}")
        self.decoded_xml_message.decoded_fields_flat_directory[xml_decoded_field_macro.field_name_with_record_prefix] = string_value
        self.decoded_xml_message.decoded_fields_flat_directory[xml_decoded_field_macro.field_name_with_record_prefix + "_list"] = all_chars

        DecodedXmlMessage.XmlMessageFieldString(field_macro=xml_decoded_field_macro, value=string_value)

    def _parse_bitset_type_field(self, xml_decoded_field_macro: DecodedXmlMessage.XmlMessageFieldMacro) -> None:

        assert self.decoded_xml_message is not None

        xml_decoded_field_macro.bits_extracted = self.extract_bits(self.decoded_xml_message.current_bit_index, xml_decoded_field_macro.size_bits)
        field_value = self.convert_bits_bitfield(xml_decoded_field_macro.bits_extracted, self.decoded_xml_message.current_bit_index, xml_decoded_field_macro.size_bits)
        self.decoded_xml_message.decoded_fields_flat_directory[xml_decoded_field_macro.field_name_with_record_prefix] = field_value

        DecodedXmlMessage.XmlMessageFieldBitfield(field_macro=xml_decoded_field_macro, value=field_value)

    def _parse_int_table_type_field(self, xml_decoded_field_macro: DecodedXmlMessage.XmlMessageFieldMacro) -> None:

        assert self.decoded_xml_message is not None

        all_signed_values: List[int] = []
        all_unsigned_values: List[int] = []

        for _ in range(0, xml_decoded_field_macro.dim):
            xml_decoded_field_macro.bits_extracted = self.extract_bits(self.decoded_xml_message.current_bit_index, xml_decoded_field_macro.size_bits)
            field_unsigned_value = self.convert_bits_unsigned_int(xml_decoded_field_macro.bits_extracted, self.decoded_xml_message.current_bit_index, xml_decoded_field_macro.size_bits)
            all_unsigned_values.append(field_unsigned_value)

            field_signed_value = self.convert_bits_signed_int(xml_decoded_field_macro.bits_extracted, self.decoded_xml_message.current_bit_index, xml_decoded_field_macro.size_bits)
            all_signed_values.append(field_signed_value)
            # self.decoded_xml_message.decoded_fields_flat_directory[xml_decoded_field_macro.field_name_with_record_prefix] = field_value

        field = DecodedXmlMessage.XmlMessageFieldInt(field_macro=xml_decoded_field_macro, unsigned_value=all_unsigned_values, signed_value=all_signed_values)
        self.decoded_xml_message.decoded_fields_flat_directory[field.long_name] = all_unsigned_values

    def _parse_single_int_type_field(self, xml_decoded_field_macro: DecodedXmlMessage.XmlMessageFieldMacro) -> None:

        assert self.decoded_xml_message is not None

        xml_decoded_field_macro.bits_extracted = self.extract_bits(self.decoded_xml_message.current_bit_index, xml_decoded_field_macro.size_bits)
        field_unsigned_value = self.convert_bits_unsigned_int(xml_decoded_field_macro.bits_extracted, self.decoded_xml_message.current_bit_index, xml_decoded_field_macro.size_bits)
        self.decoded_xml_message.decoded_fields_flat_directory[xml_decoded_field_macro.field_name_with_record_prefix] = field_unsigned_value
        self.decoded_xml_message.decoded_fields_flat_directory[xml_decoded_field_macro.field_name_with_record_prefix + "_as_unsigned"] = field_unsigned_value
        field_signed_value = self.convert_bits_signed_int(xml_decoded_field_macro.bits_extracted, self.decoded_xml_message.current_bit_index, xml_decoded_field_macro.size_bits)
        self.decoded_xml_message.decoded_fields_flat_directory[xml_decoded_field_macro.field_name_with_record_prefix + "_as_signed"] = field_signed_value

        DecodedXmlMessage.XmlMessageFieldInt(field_macro=xml_decoded_field_macro, unsigned_value=field_unsigned_value, signed_value=field_signed_value)

    def _parse_int_type_field(self, xml_decoded_field_macro: DecodedXmlMessage.XmlMessageFieldMacro) -> None:

        assert self.decoded_xml_message is not None
        if xml_decoded_field_macro.dim == 1:
            self._parse_single_int_type_field(xml_decoded_field_macro=xml_decoded_field_macro)
        else:
            self._parse_int_table_type_field(xml_decoded_field_macro=xml_decoded_field_macro)

    def _parse_field(self, element: ET.Element, xml_message_record_unit: DecodedXmlMessage.XmlMessageRecordUnit, record_prefix: str) -> None:

        assert self.decoded_xml_message is not None

        raw_field_name = cast(str, element.get("id"))
        field_size_bits = int(element.get("size", 0))
        field_dim = int(element.get("dim", 1))
        field_type = element.get("class")
        assert field_type

        field_name_with_record_prefix = record_prefix + raw_field_name

        xml_decoded_field_macro = DecodedXmlMessage.XmlMessageFieldMacro(
            raw_class=field_type,
            parent_record=xml_message_record_unit,
            raw_dim=field_dim,
            raw_id=raw_field_name,
            size_bits=field_size_bits,
            field_name_with_record_prefix=field_name_with_record_prefix,
            decoded_xml_message=self.decoded_xml_message,
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
                f"Message {self.decoded_xml_message.message_number}: Error when decoding field {raw_field_name} {xml_decoded_field_macro.field_name_with_record_prefix}. {val_err}. {val_err.__class__.__name__}"
            )
            self.decoded_xml_message.not_decoded_because_error_fields_names.append(raw_field_name)

    def _parse_record(self, record: ET.Element, parent_record: Optional[DecodedXmlMessage.XmlMessageRecordUnit] = None) -> None:
        """Recursively parse records to decode fields."""
        raw_class = record.get("class")
        assert raw_class
        raw_dim = record.get("dim")
        raw_id = record.get("id")
        assert raw_id
        raw_offset = record.get("offset")
        assert raw_offset

        assert self.decoded_xml_message
        xml_message_record_macro = DecodedXmlMessage.XmlMessageRecordMacro(
            raw_class=raw_class,
            raw_dim=raw_dim,
            raw_id=raw_id,
            raw_offset=raw_offset,
            decoded_xml_message=self.decoded_xml_message,
        )

        if parent_record is None:
            self.decoded_xml_message.root_record = xml_message_record_macro
        else:
            parent_record.records.append(xml_message_record_macro)

        record_dim = int(record.get("dim", 1))
        for record_it in range(0, record_dim):

            record_prefix = "" if record_dim == 1 else f"{record.get("id")}_{record_it}"
            xml_message_record_unit = DecodedXmlMessage.XmlMessageRecordUnit(xml_message_record_macro, index=record_it)

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

    @classmethod
    def get_xml_file_root(cls, message_number: int, xml_directory_path: str) -> Optional[ET.Element]:
        # Open the corresponding XML file based on message_id
        xml_file_path = os.path.join(xml_directory_path, f"MsgId{message_number}scheme.xml")
        if xml_file_path in cls._parsed_xml_files_by_path:
            return cls._parsed_xml_files_by_path[xml_file_path]

        try:
            # Load and parse the XML file once
            logger_config.print_and_log_info(f"Load and parse file {xml_file_path}")
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            cls._parsed_xml_files_by_path[xml_file_path] = root
            return root
        except FileNotFoundError:
            logger_config.print_and_log_error(f"File {xml_file_path} not found.")
            return None

    def decode_xml_fields_in_message_hexadecimal(self, message_number: int, hexadecimal_content: str) -> Optional[DecodedXmlMessage]:

        assert isinstance(message_number, int), f"message_number is type {type(message_number)}"
        if message_number not in self.cached_messages_by_id:
            xml_file_root = XmlMessageDecoder.get_xml_file_root(message_number=message_number, xml_directory_path=self.xml_directory_path)
            if xml_file_root is None:
                return None
            self.cached_messages_by_id[message_number] = xml_file_root

        root = self.cached_messages_by_id[message_number]
        # Traverse the root record and decode
        decoded_xml_message = self.decoded_xml_message = DecodedXmlMessage(message_number=message_number, hex_string=hexadecimal_content)
        self._parse_root(root)
        self.decoded_xml_message = None
        return decoded_xml_message
