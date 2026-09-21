import json
from dataclasses import dataclass
from typing import Self, cast

from logger import logger_config


@dataclass
class EnumAttributesTypeDefinition:
    name: str
    states_ordered_by_value_from_zero: list[str]


@dataclass
class PacketFieldDefinition:
    name: str
    size_in_bits: int | None
    enum_type_definition: EnumAttributesTypeDefinition | None = None


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

    @classmethod
    @logger_config.stopwatch_decorator()
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
                packets_definitions.append(
                    PacketDefinition(
                        name=packet_definition_found["Packet"],
                        alias=packet_definition_found.get("Alias"),
                        identifier=cast(int, packet_definition_found["Id"]),
                        fields=(
                            [
                                PacketFieldDefinition(
                                    name=value_dict.get("name"),
                                    size_in_bits=value_dict.get("size"),
                                    enum_type_definition=value_dict.get("type"),
                                )
                                for value_dict in packet_definition_found.get("Fields") or []
                            ]
                        ),
                    )
                )

            logger_config.print_and_log_info(f"{len(packets_definitions)} packets_definitions created")

        return cls(enum_attributes_type_definitions, packets_definitions)
