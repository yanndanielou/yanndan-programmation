import csv
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, cast

from logger import logger_config

from stsloganalyzis import decode_specific_message_content, line_topology

if TYPE_CHECKING:
    from stsloganalyzis.decode_message import DecodedMessage

ZC_ATS_MAL_MESSAGE_ID = 148


@dataclass
class ZcAtsMalMessageDecoder:
    railway_line: line_topology.Line

    def decode(self, decoded_message: "DecodedMessage") -> decode_specific_message_content.SpecificMessageContentDecoded:
        specific_message_content_decoded = decode_specific_message_content.SpecificMessageContentDecoded()

        mal_seg_id = cast(int, decoded_message.decoded_fields_flat_directory.get("MALSegIdV"))
        mal_offset = cast(int, decoded_message.decoded_fields_flat_directory["MALOffsetV"])
        vital_mal_is_defined = mal_seg_id > 0
        vital_mal_pk = self.railway_line.get_pk_by_segment_and_abscissa(segment=mal_seg_id, abscissa=mal_offset) if vital_mal_is_defined else 0
        specific_message_content_decoded.fields_with_value["VitalMal_Pk"] = vital_mal_pk

        vital_mal_tracking_block_id = self.railway_line.get_tracking_block_by_segment_and_abscissa(segment=mal_seg_id, abscissa=mal_offset).identifier if vital_mal_is_defined else "NA"
        specific_message_content_decoded.fields_with_value["VitalMal_TB"] = vital_mal_tracking_block_id

        pass
        return specific_message_content_decoded
