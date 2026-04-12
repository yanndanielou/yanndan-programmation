import csv
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List

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

        vital_mal_pk = self.railway_line.get_pk_by_segment_and_abscissa(
            segment=int(decoded_message.decoded_fields_flat_directory["MALSegIdV"]), abscissa=int(decoded_message.decoded_fields_flat_directory["MALOffsetV"])
        )
        specific_message_content_decoded.fields_with_value["VitalMalPk"] = vital_mal_pk
        pass
        return specific_message_content_decoded
