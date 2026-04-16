import csv
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, cast, Tuple

from logger import logger_config

from stsloganalyzis import decode_specific_message_content, line_topology

if TYPE_CHECKING:
    from stsloganalyzis.decode_message import DecodedMessage

CC_ATS_SPE_OPERATION_MESSAGE_ID___disabled = 36000
CC_ATS_SPE_RS_OPERATION_MESSAGE_ID = 100
ATS_CC_SPE_RC_MESSAGE_ID = 101


class CcAtsRsOperationMessageDecoder(decode_specific_message_content.TopologyDependentMessageDecoder):

    def do_decode(self, decoded_message: "DecodedMessage") -> None:

        self.decode_location_to_human_readable_by_fields_common_prefix_and_suffix(
            label="NvFront",
            decoded_message=decoded_message,
            location_fields_prefix="NvFront",
        )


class AtsCcSpecificRemoteControlMessageDecoder(decode_specific_message_content.TopologyDependentMessageDecoder):

    def do_decode(self, decoded_message: "DecodedMessage") -> None:

        if decoded_message.decoded_fields_flat_directory["CcRcType"] == 4:

            self.decode_location_to_human_readable_by_fields_common_prefix_and_suffix(
                decoded_message=decoded_message,
                location_fields_prefix="RestrEnd1",
            )

            self.decode_location_to_human_readable_by_fields_common_prefix_and_suffix(
                decoded_message=decoded_message,
                location_fields_prefix="RestrEnd2",
            )


class CcAtsSpecificOperationMessageDecoder(decode_specific_message_content.TopologyDependentMessageDecoder):

    def do_decode(self, decoded_message: "DecodedMessage") -> None:

        self.decode_location_to_human_readable_by_fields_common_prefix_and_suffix(
            decoded_message=decoded_message,
            location_fields_prefix="RestrEnd1",
        )

        self.decode_location_to_human_readable_by_fields_common_prefix_and_suffix(
            decoded_message=decoded_message,
            location_fields_prefix="RestrEnd2",
        )

        self.decode_location_to_human_readable_by_fields_common_prefix_and_suffix(
            decoded_message=decoded_message,
            location_fields_prefix="TransponderFrontEnd",
        )
