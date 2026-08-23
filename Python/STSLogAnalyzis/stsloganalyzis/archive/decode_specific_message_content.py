import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Tuple, cast, Optional

from logger import logger_config

from stsloganalyzis.topology import (
    line_topology,
)
from stsloganalyzis.archive import constants, helpers

if TYPE_CHECKING:
    from stsloganalyzis.archive import decode_message


@dataclass
class SpecificMessageContentDecoded:

    def __init__(self) -> None:
        # self.fields_with_value: Dict[str, bool | int | str | float] = dict()
        self.fields_with_value: Dict[str, constants.FIELD_TYPE] = dict()

    def _get_track_circuit_and_tracking_block_info(self, mal_seg_id: int, mal_offset: int, railway_line: line_topology.Line, decoded_message: "decode_message.DecodedMessage") -> Tuple[str, str]:
        location_is_defined = mal_seg_id > 0
        if location_is_defined:
            tracking_block = railway_line.get_tracking_block_by_segment_and_abscissa(segment=mal_seg_id, abscissa_in_cm=mal_offset)
            logger_config.print_and_log_warning_if(not tracking_block, f"{decoded_message.message_number}, no TB defined at {mal_seg_id}/{mal_offset}")
            tracking_block_id = tracking_block.identifier if tracking_block else f"No TB defined at {mal_seg_id}/{mal_offset}"
            track_circuit_id = tracking_block.track_circuit_id if tracking_block else f"No TB thus TC defined at {mal_seg_id}/{mal_offset}"
            return track_circuit_id, tracking_block_id
        else:
            return "NA", "NA"

    def decode_location_to_human_readable_by_fields_common_prefix_and_suffix(
        self,
        decoded_message: "decode_message.DecodedMessage",
        location_fields_prefix: str,
        railway_line: line_topology.Line,
        location_fields_suffix: str = "",
        label: Optional[str] = None,
    ) -> None:
        if label is None:
            label = f"{location_fields_prefix}{location_fields_suffix}"
        self.decode_location_to_human_readable_by_fields_names(
            label=label,
            decoded_message=decoded_message,
            railway_line=railway_line,
            seg_id_field_name=f"{location_fields_prefix}SegId{location_fields_suffix}",
            offset_field_name=f"{location_fields_prefix}Offset{location_fields_suffix}",
        )

    def decode_location_to_human_readable_by_fields_names(
        self, label: str, decoded_message: "decode_message.DecodedMessage", seg_id_field_name: str, offset_field_name: str, railway_line: line_topology.Line
    ) -> None:

        try:
            assert (
                seg_id_field_name in decoded_message.decoded_fields_flat_directory
            ), f"Field {seg_id_field_name} not found in message {decoded_message.message_number} among {decoded_message.decoded_fields_flat_directory.keys()}"
            assert (
                offset_field_name in decoded_message.decoded_fields_flat_directory
            ), f"Field {offset_field_name} not found in message {decoded_message.message_number} among {decoded_message.decoded_fields_flat_directory.keys()}"

            location_seg_id = cast(int, decoded_message.decoded_fields_flat_directory.get(seg_id_field_name))
            location_offset = cast(int, decoded_message.decoded_fields_flat_directory[offset_field_name])
            is_defined = location_seg_id > 0
            pk = railway_line.get_pk_by_segment_and_abscissa(segment=location_seg_id, abscissa=location_offset) if is_defined else 0
            self.fields_with_value[f"{label}_Pk"] = pk

            track_circuit_id, tracking_block_id = self._get_track_circuit_and_tracking_block_info(
                mal_seg_id=location_seg_id, mal_offset=location_offset, railway_line=railway_line, decoded_message=decoded_message
            )
            self.fields_with_value[f"{label}_TB"] = tracking_block_id

            self.fields_with_value[f"{label}_TC"] = track_circuit_id

            exact_location = helpers.decode_one_exact_location(
                decoded_fields_flat_directory=decoded_message.decoded_fields_flat_directory,
                abscissa_field_name=offset_field_name,
                railway_line=railway_line,
                segment_id_field_name=seg_id_field_name,
            )

            self.fields_with_value[f"{label}_CV"] = exact_location.get_virtual_canton_id_string_if_no() if exact_location else f"No CV defined at {location_seg_id}/{location_offset}"
        except AssertionError as err:
            logger_config.print_and_log_exception(err)


@dataclass
class TopologyDependentMessageDecoder(ABC):
    railway_line: line_topology.Line

    def __post_init__(self) -> None:
        self.specific_message_content_decoded = SpecificMessageContentDecoded()

    def decode(self, decoded_message: "decode_message.DecodedMessage") -> SpecificMessageContentDecoded:
        self.do_decode(decoded_message)
        return self.specific_message_content_decoded

    @abstractmethod
    def do_decode(self, decoded_message: "decode_message.DecodedMessage") -> None:
        pass

    def decode_location_to_human_readable_by_fields_names(self, label: str, decoded_message: "decode_message.DecodedMessage", seg_id_field_name: str, offset_field_name: str) -> None:
        self.specific_message_content_decoded.decode_location_to_human_readable_by_fields_names(
            label=label,
            decoded_message=decoded_message,
            seg_id_field_name=seg_id_field_name,
            offset_field_name=offset_field_name,
            railway_line=self.railway_line,
        )

    def decode_location_to_human_readable_by_fields_common_prefix_and_suffix(
        self,
        decoded_message: "decode_message.DecodedMessage",
        location_fields_prefix: str,
        location_fields_suffix: str = "",
        label: Optional[str] = None,
    ) -> None:
        self.specific_message_content_decoded.decode_location_to_human_readable_by_fields_common_prefix_and_suffix(
            label=label,
            decoded_message=decoded_message,
            railway_line=self.railway_line,
            location_fields_prefix=location_fields_prefix,
            location_fields_suffix=location_fields_suffix,
        )
