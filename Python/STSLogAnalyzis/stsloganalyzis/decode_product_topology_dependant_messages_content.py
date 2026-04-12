import csv
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, cast, Tuple

from logger import logger_config

from stsloganalyzis import decode_specific_message_content, line_topology

if TYPE_CHECKING:
    from stsloganalyzis.decode_message import DecodedMessage

ZC_ATS_MAL_MESSAGE_ID = 148
CC_ATS_TRACKING_MESSAGE_ID = 20


class ZcAtsMalMessageDecoder(decode_specific_message_content.TopologyDependentMessageDecoder):

    def do_decode(self, decoded_message: "DecodedMessage") -> None:

        self.decode_location_to_human_readable_by_fields_common_prefix_and_suffix(
            label="VitalMal",
            decoded_message=decoded_message,
            location_fields_prefix="MAL",
            location_fields_suffix="V",
        )
        self.decode_location_to_human_readable_by_fields_common_prefix_and_suffix(
            label="NonVitalMal",
            decoded_message=decoded_message,
            location_fields_prefix="MAL",
            location_fields_suffix="Nv",
        )
        self.decode_location_to_human_readable_by_fields_common_prefix_and_suffix(
            decoded_message=decoded_message,
            location_fields_prefix="ExtRear",
        )


class CcAtsTrackingMessageDecoder(decode_specific_message_content.TopologyDependentMessageDecoder):

    def do_decode(self, decoded_message: "DecodedMessage") -> None:

        self.decode_location_to_human_readable_by_fields_common_prefix_and_suffix(
            decoded_message=decoded_message,
            location_fields_prefix="ExtFront",
        )
        self.decode_location_to_human_readable_by_fields_common_prefix_and_suffix(
            decoded_message=decoded_message,
            location_fields_prefix="IntFront",
        )
        self.decode_location_to_human_readable_by_fields_common_prefix_and_suffix(
            decoded_message=decoded_message,
            location_fields_prefix="ExtRear",
        )
        self.decode_location_to_human_readable_by_fields_common_prefix_and_suffix(
            decoded_message=decoded_message,
            location_fields_prefix="IntRear",
        )

        for cc_id in ["1", "3"]:
            self.decode_location_to_human_readable_by_fields_names(
                label=f"CCId{cc_id}FoncLoc", decoded_message=decoded_message, seg_id_field_name=f"CCId{cc_id}RefPtSegId", offset_field_name=f"CCId{cc_id}NvRefPtOffset"
            )
