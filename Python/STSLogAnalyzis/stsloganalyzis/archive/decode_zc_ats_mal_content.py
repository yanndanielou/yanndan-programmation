from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stsloganalyzis.archive.decode_message import DecodedMessage

from stsloganalyzis.archive import decode_specific_message_content
from stsloganalyzis.topology import line_topology

PAS_ATS_TM_AO_SIG_MESSAGE_ID = 205


class MALType(IntEnum):
    AUTOMATIC_TRAIN = 0  # 0 = AT (train contrôlé)
    MT_MANUAL = 1  # 1 = MT (train en manuel)
    UNEQUIPPED_TRAIN = 2  # 2 = UT (train non équipé ou muet)
    HOME_SIGNAL = 3  # 3 = HS (Origine de manoeuvre)
    TRACK_LIMIT = 4  # 4 = Track_Limit (Limite de voie)
    DEFAULT = 5  # 5 = Default (Défaut)
    NOT_USED_6 = 6
    NOT_USED_7 = 7


@dataclass
class ZcAtsMalDecoder:
    railway_line: line_topology.Line

    def decode(self, decoded_message: "DecodedMessage") -> decode_specific_message_content.SpecificMessageContentDecoded:

        decoded_specific_message = decode_specific_message_content.SpecificMessageContentDecoded()

        train_label = f"Train_{decoded_message.decoded_fields_flat_directory["CCId1"]}_{decoded_message.decoded_fields_flat_directory["CCId3"]}"

        decoded_specific_message.fields_with_value[f"{train_label}_MALType"] = MALType(decoded_message.decoded_fields_flat_directory["MALType"]).name
        decoded_message.decoded_fields_flat_directory.pop("MALType")

        # add train prefix
        for initial_field_name in [
            "MALSegIdV",
            "MALOffsetV",
            "MALDirectionPlus",
            "MalWithCaution",
            "MALSegIdNv",
            "MALOffsetNv",
            "ExtRearSegId",
            "ExtRearOffset",
        ]:
            decoded_message.decoded_fields_flat_directory[f"{train_label}_{initial_field_name}"] = decoded_message.decoded_fields_flat_directory[initial_field_name]
            decoded_message.decoded_fields_flat_directory.pop(initial_field_name)

        decoded_specific_message.decode_location_to_human_readable_by_fields_common_prefix_and_suffix(
            label=f"{train_label}_VitalMal",
            decoded_message=decoded_message,
            location_fields_prefix=f"{train_label}_MAL",
            location_fields_suffix="V",
            railway_line=self.railway_line,
        )
        decoded_specific_message.decode_location_to_human_readable_by_fields_common_prefix_and_suffix(
            label=f"{train_label}_NonVitalMal",
            decoded_message=decoded_message,
            location_fields_prefix=f"{train_label}_MAL",
            location_fields_suffix="Nv",
            railway_line=self.railway_line,
        )
        decoded_specific_message.decode_location_to_human_readable_by_fields_common_prefix_and_suffix(
            decoded_message=decoded_message,
            location_fields_prefix=f"{train_label}_ExtRear",
            railway_line=self.railway_line,
        )
        assert decoded_specific_message
        return decoded_specific_message
