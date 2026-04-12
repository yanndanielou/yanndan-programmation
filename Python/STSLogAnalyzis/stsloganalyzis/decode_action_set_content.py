from typing import List, Dict, TYPE_CHECKING, cast
from dataclasses import dataclass

if TYPE_CHECKING:
    from stsloganalyzis.decode_message import DecodedMessage


from stsloganalyzis import decode_specific_message_content
import csv

from logger import logger_config


ATS_CC_ACTION_SET_MESSAGE_ID = 192


class DecodedActionSet(decode_specific_message_content.SpecificMessageContentDecoded):
    def __init__(self) -> None:
        super().__init__()
        self.undecoded_bits_by_error: List[int] = []
        self.action_set_id_with_value_true: List[str] = []


@dataclass
class ActionSetContentDecoder:
    csv_file_file_path: str

    def decode(self, decoded_message: "DecodedMessage") -> DecodedActionSet:
        actions_field = cast(str, decoded_message.decoded_fields_flat_directory["Actions"])
        action_set_decoded = self._decode_actions_bitfield(bitfield=actions_field)
        return action_set_decoded

    def _decode_actions_bitfield(self, bitfield: str) -> DecodedActionSet:

        decoded_action_set = DecodedActionSet()
        decoded_bits = set()

        # Read the CSV file
        with open(self.csv_file_file_path, mode="r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file, delimiter=";")

            # Iterate through each row in the CSV
            for csv_row in csv_reader:

                num_ats_str = csv_row["NUM_ACTION_SET_ATS"] if "NUM_ACTION_SET_ATS" in csv_row else csv_row["NUM_ATS"]
                num_ats = int(num_ats_str)
                # num_ats = int(row["NUM_ATS"])
                decoded_bits.add(num_ats)  # Track decoded bits
                bit_value_str = bitfield[num_ats]
                bit_value_bool = bool(int(bit_value_str))

                action_set_id_str = csv_row["ACTION_SET_ID"] if "ACTION_SET_ID" in csv_row else csv_row["ID"]

                # results.append({"ID": row["ID"], "Value": bit_value})
                decoded_action_set.fields_with_value[action_set_id_str] = bit_value_bool

                if bit_value_str == "1":
                    # results.append(row["ID"])
                    action_set_id_str = csv_row["ACTION_SET_ID"] if "ACTION_SET_ID" in csv_row else csv_row["ID"]
                    decoded_action_set.action_set_id_with_value_true.append(action_set_id_str)

        # Check for any "1" in the bitfield that doesn't have a corresponding entry
        for index, bit in enumerate(bitfield):
            if bit == "1" and index not in decoded_bits:
                decoded_action_set.undecoded_bits_by_error.append(index)
                logger_config.print_and_log_error(f"Warning: Bit at position {index} is '1' but has no corresponding entry in the CSV.")

        return decoded_action_set
