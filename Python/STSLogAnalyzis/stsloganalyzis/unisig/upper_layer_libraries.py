import json
from dataclasses import dataclass
from typing import Self, cast

from logger import logger_config


@dataclass
class EnumAttributesTypeDefinition:
    name: str
    states_ordered_by_value_from_zero: list[str]


@dataclass
class PacketVariantDefinition:
    name: str
    trigger_variable_name: str
    trigger_variable_value: int
    alias: str | None
    fields_or_variants: list["PacketFieldDefinition|PacketVariantsDefinition"]


@dataclass
class PacketVariantsDefinition:
    variants: list["PacketVariantDefinition"]

    @property
    def trigger_variable_name(self) -> str:
        found = list({variant.trigger_variable_name for variant in self.variants})
        assert found
        assert len(found) == 1
        return found[0]


@dataclass
class PacketFieldDefinition:
    name: str
    size_in_bits: int | None
    enum_type_definition: EnumAttributesTypeDefinition | None = None
    fields_or_variants: list["PacketFieldDefinition|PacketVariantsDefinition"] | None = None


@dataclass
class PacketDefinition:
    name: str
    alias: str
    identifier: int
    fields: list[PacketFieldDefinition]


@dataclass
class UpperLayerDecodingLibrary:
    enum_attributes_type_definitions: list[EnumAttributesTypeDefinition]
    packets_definitions: list[PacketDefinition]

    @staticmethod
    def create_fields_or_variants_definition(values_dicts: list[dict]) -> list[PacketVariantsDefinition | PacketFieldDefinition]:
        ret: list[PacketVariantsDefinition | PacketFieldDefinition] = []
        for value_dict in values_dicts:
            name = value_dict.get("name")
            variants = value_dict.get("Variants")

            if name is not None:
                ret.append(UpperLayerDecodingLibrary.create_packet_field_definition(value_dict))
            elif variants is not None:
                ret.append(UpperLayerDecodingLibrary.create_variants_definition(value_dict))

        assert ret
        return ret

    @staticmethod
    def create_variants_definition(value_dict: dict) -> PacketVariantsDefinition:
        variants_definitions = value_dict.get("Variants")
        packet_variant_definitions: list[PacketVariantDefinition] = []
        for variant_definition in variants_definitions:
            packet_variant_definition = UpperLayerDecodingLibrary.create_variant_definition(value_dict=variant_definition)
            packet_variant_definitions.append(packet_variant_definition)
            pass

        assert packet_variant_definitions
        return PacketVariantsDefinition(packet_variant_definitions)

    @staticmethod
    def create_variant_definition(value_dict: dict) -> PacketVariantDefinition:

        variables_found = [(variable_key, variable_value) for (variable_key, variable_value) in value_dict.items() if variable_key not in ["name", "Fields", "Alias"]]

        alias = value_dict.get("Alias")

        assert variables_found
        assert len(variables_found) == 1

        variable_found = variables_found[0]

        trigger_variable_name = variable_found[0]
        trigger_variable_value = variable_found[1]
        assert isinstance(trigger_variable_value, int)

        name = value_dict.get("name")
        assert isinstance(name, str)

        return PacketVariantDefinition(
            name=name,
            trigger_variable_name=trigger_variable_name,
            trigger_variable_value=trigger_variable_value,
            fields_or_variants=UpperLayerDecodingLibrary.create_fields_or_variants_definition(value_dict.get("Fields")) if value_dict.get("Fields") else [],
            alias=alias,
        )

    @staticmethod
    def create_packet_field_definition(value_dict: dict) -> PacketFieldDefinition:

        name = value_dict.get("name")
        assert isinstance(name, str)

        return PacketFieldDefinition(
            name=name,
            size_in_bits=value_dict.get("size"),
            enum_type_definition=value_dict.get("type"),
            fields_or_variants=UpperLayerDecodingLibrary.create_fields_or_variants_definition(value_dict.get("Fields")) if value_dict.get("Fields") else [],
        )

    @classmethod
    @logger_config.stopwatch_decorator(monitor_ram_usage=True)
    def from_next_json_file_full_path(cls, json_file_full_path: str) -> Self:
        enum_attributes_type_definitions: list[EnumAttributesTypeDefinition] = []
        with open(json_file_full_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)

            for type_definition_found in json_data.get("Types"):
                enum_attributes_type_definitions.append(
                    EnumAttributesTypeDefinition(
                        name=type_definition_found.get(""),
                        states_ordered_by_value_from_zero=[value_dict.get("name") for value_dict in type_definition_found.get("Values")],
                    )
                )

            logger_config.print_and_log_info(f"{len(enum_attributes_type_definitions)} enum_attributes_type_definitions created")

            packets_definitions: list[PacketDefinition] = []

            for packet_definition_found in json_data.get("Packets"):
                fields: list[PacketFieldDefinition] = []
                for value_dict in packet_definition_found.get("Fields") or []:
                    fields.append(UpperLayerDecodingLibrary.create_packet_field_definition(value_dict))
                packets_definitions.append(
                    PacketDefinition(
                        name=packet_definition_found["Packet"],
                        alias=packet_definition_found.get("Alias"),
                        identifier=cast(int, packet_definition_found["Id"]),
                        fields=fields,
                    )
                )

            logger_config.print_and_log_info(f"{len(packets_definitions)} packets_definitions created")

        return cls(enum_attributes_type_definitions, packets_definitions)
