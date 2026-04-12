import csv
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, cast, Tuple

from logger import logger_config

from stsloganalyzis import decode_specific_message_content, line_topology

if TYPE_CHECKING:
    from stsloganalyzis.decode_message import DecodedMessage

ZC_ATS_MAL_MESSAGE_ID = 148


@dataclass
class ZcAtsMalMessageDecoder:
    railway_line: line_topology.Line

    def __post_init__(self) -> None:
        self.specific_message_content_decoded = decode_specific_message_content.SpecificMessageContentDecoded()

    def decode(self, decoded_message: "DecodedMessage") -> decode_specific_message_content.SpecificMessageContentDecoded:

        self.specific_message_content_decoded.decode_location_to_human_readable(
            label="VitalMal", decoded_message=decoded_message, seg_id_field_name="MALSegIdV", offset_field_name="MALOffsetV", railway_line=self.railway_line
        )
        self.specific_message_content_decoded.decode_location_to_human_readable(
            label="NonVitalMal", decoded_message=decoded_message, seg_id_field_name="MALSegIdNv", offset_field_name="MALOffsetNv", railway_line=self.railway_line
        )
        self.specific_message_content_decoded.decode_location_to_human_readable(
            label="ExtRear", decoded_message=decoded_message, seg_id_field_name="ExtRearSegId", offset_field_name="ExtRearOffset", railway_line=self.railway_line
        )
        return self.specific_message_content_decoded
