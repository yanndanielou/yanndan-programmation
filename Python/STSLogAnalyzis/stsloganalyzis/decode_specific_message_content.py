import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Tuple, cast

from stsloganalyzis import line_topology

if TYPE_CHECKING:
    from stsloganalyzis import decode_message


@dataclass
class SpecificMessageContentDecoded:

    def __init__(self) -> None:
        # self.fields_with_value: Dict[str, bool | int | str | float] = dict()
        self.fields_with_value: Dict[str, float | int | bool | str | List[int] | List[str] | List[bool]] = dict()

    def _get_track_circuit_and_tracking_block_info(self, mal_seg_id: int, mal_offset: int, railway_line: line_topology.Line) -> Tuple[str, str]:
        mal_is_defined = mal_seg_id > 0
        if mal_is_defined:
            tracking_block = railway_line.get_tracking_block_by_segment_and_abscissa(segment=mal_seg_id, abscissa=mal_offset)
            tracking_block_id = tracking_block.identifier if tracking_block else f"No TB defined at {mal_seg_id}/{mal_offset}"
            track_circuit_id = tracking_block.track_circuit_id if tracking_block else f"No TB thus TC defined at {mal_seg_id}/{mal_offset}"
            return track_circuit_id, tracking_block_id
        else:
            return "NA", "NA"

    def decode_location_to_human_readable(self, label: str, decoded_message: "decode_message.DecodedMessage", seg_id_field_name: str, offset_field_name: str, railway_line: line_topology.Line) -> None:

        mal_seg_id = cast(int, decoded_message.decoded_fields_flat_directory.get(seg_id_field_name))
        mal_offset = cast(int, decoded_message.decoded_fields_flat_directory[offset_field_name])
        is_defined = mal_seg_id > 0
        pk = railway_line.get_pk_by_segment_and_abscissa(segment=mal_seg_id, abscissa=mal_offset) if is_defined else 0
        self.fields_with_value[f"{label}_Pk"] = pk

        track_circuit_id, tracking_block_id = self._get_track_circuit_and_tracking_block_info(mal_seg_id=mal_seg_id, mal_offset=mal_offset, railway_line=railway_line)
        self.fields_with_value[f"{label}_TB"] = tracking_block_id

        self.fields_with_value[f"{label}_TC"] = track_circuit_id
